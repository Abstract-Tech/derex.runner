# syntax = docker/dockerfile:experimental

# Debugging a Dockerfile can be difficult. A good pattern is to put a breakpoint, enter
# the build container and have a look. To do this, put the command
# sleep infinity
# in the place you want to examine. When execution stops there, run
# sudo nsenter --target $(pgrep sleep) --mount --uts --ipc --net --pid sh

ARG PYTHON_VERSION=3.6
FROM docker.io/python:${PYTHON_VERSION}-alpine3.11 as libgeos

RUN --mount=type=cache,target=/var/cache/apk apk add alpine-sdk
ENV GEOS_VERSION=3.8.0

RUN wget -c http://download.osgeo.org/geos/geos-${GEOS_VERSION}.tar.bz2 -O - | tar xjf - --directory /usr/local && \
    cd /usr/local/geos-${GEOS_VERSION} && ./configure && make -j 4 && make install

FROM docker.io/python:${PYTHON_VERSION}-alpine3.11 as base
# This image will be used to build all other images in this Dockerfile
# The base image is defined later, and it has rmlint added to this base
ENV GEOS_VERSION=3.8.0

RUN wget -q -O - "https://github.com/jwilder/dockerize/releases/download/v0.6.1/dockerize-linux-amd64-v0.6.1.tar.gz" | tar xzf - --directory /usr/local/bin

RUN --mount=type=cache,target=/var/cache/apk apk add \
    gettext \
    git \
    graphviz \
    freetype \
    graphviz \
    openblas \
    lapack \
    libstdc++ \
    libjpeg \
    libxslt \
    mariadb-connector-c \
    sqlite \
    xmlsec \
    wget

COPY patch_ldconfig_to_fix_shapely.sh /tmp/patch_ldconfig_to_fix_shapely.sh

COPY --from=libgeos /usr/local/lib/libgeos* /usr/lib/
# Patch ldconfig and test that libgeos works
RUN /tmp/patch_ldconfig_to_fix_shapely.sh && \
     python -c "from  ctypes import CDLL; CDLL('$(echo /usr/lib/libgeos_c.so)').GEOSversion"


# we want to use paver without remembering to specify these
ENV NO_PREREQ_INSTALL=True
ENV NO_PYTHON_UNINSTALL=True

FROM base as sourceonly
ARG EDX_PLATFORM_VERSION=open-release/juniper.alpha1

ARG EDX_PLATFORM_REPOSITORY=https://github.com/edx/edx-platform.git

RUN mkdir -p /openedx/themes /openedx/locale /openedx/bin/ && \
    git clone ${EDX_PLATFORM_REPOSITORY} --branch ${EDX_PLATFORM_VERSION} --depth 1 /openedx/edx-platform

WORKDIR /openedx/edx-platform

FROM base as wheels

RUN --mount=type=cache,target=/var/cache/apk apk add \
    alpine-sdk \
    blas-dev \
    freetype-dev \
    gettext \
    gfortran \
    graphviz-dev \
    jpeg-dev \
    lapack-dev \
    libffi-dev \
    libpng-dev \
    libxml2-dev \
    libxslt-dev \
    linux-headers \
    mariadb-connector-c-dev \
    mariadb-dev \
    openblas-dev \
    pkgconfig \
    python-dev \
    sqlite-dev \
    swig \
    xmlsec-dev && \
    `# From https://github.com/jfloff/alpine-python/issues/32` \
    sed '/st_mysql_options options;/a unsigned int reconnect;' /usr/include/mysql/mysql.h -i

COPY --from=sourceonly /openedx/edx-platform/requirements/edx/base.txt /tmp/base.txt
RUN --mount=type=cache,target=/root/.cache/pip \
    cat /tmp/base.txt | grep -v github | grep -v ^-e > /tmp/derex.txt && \
    export PIP_FIND_LINKS="https://wheels.derex.page/alpine-$(cat /etc/alpine-release)" && \
    pip install numpy -c /tmp/derex.txt && \
    pip wheel --wheel-dir=/wheelhouse -r /tmp/derex.txt && \
    pip wheel --wheel-dir=/wheelhouse gevent "whitenoise[brotli]<5"

FROM wheels as rmlint
RUN pip install scons && \
    apk add \
    glib-dev \
    json-glib

RUN wget -q https://github.com/sahib/rmlint/tarball/e56626d39134b7ac6317c19940c446eace01d7ad -O - | tar xvzf - && \
    cd sahib-rmlint* && \
    scons && \
    mv rmlint /usr/local/bin/

FROM sourceonly as notranslations

COPY --from=rmlint /usr/local/bin/rmlint /usr/local/bin/rmlint

# TODO: extract these package list and put it in a file external to the Dockerfile
RUN --mount=type=cache,target=/root/.cache/pip --mount=type=bind,source=/wheelhouse,from=wheels,target=/wheelhouse \
    pip install "whitenoise[brotli]<5" flower gevent --find-links /wheelhouse -c /openedx/edx-platform/requirements/edx/development.txt
RUN --mount=type=cache,target=/root/.cache/pip --mount=type=bind,source=/wheelhouse,from=wheels,target=/wheelhouse \
    pip install --find-links /wheelhouse -r /openedx/edx-platform/requirements/edx/base.txt && \
    `# We install a newer version of gunicorn to take advantage of the --max-requests-jitter option` \
    `# It s not very clear why it was pinned in the first place` \
    pip install gunicorn==19.10.0

COPY whitenoise_edx.py assets.py translations.sh cleanup_assets.sh compile_assets.sh /usr/local/bin/

RUN mkdir -p /openedx/edx-platform/lms/envs/derex/ /openedx/edx-platform/cms/envs/derex/ && \
    touch /openedx/edx-platform/lms/envs/derex/__init__.py /openedx/edx-platform/cms/envs/derex/__init__.py && \
    mv /usr/local/bin/assets.py /openedx/edx-platform/lms/envs/derex/ && \
    mv /usr/local/bin/whitenoise_edx.py /openedx/edx-platform/whitenoise_edx.py && \
    cp /openedx/edx-platform/lms/envs/derex/assets.py /openedx/edx-platform/cms/envs/derex/assets.py

FROM notranslations as translations

RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=secret,id=transifex,dst=/root/.transifexrc-orig \
    pip install transifex-client -c /openedx/edx-platform/requirements/edx/development.txt && \
    /usr/local/bin/translations.sh

FROM notranslations as nostatic
# This image contains the Open edX source code and all necessary python packages installed.
# It's still missing the static files, hence the name.

RUN --mount=type=bind,from=translations,target=/translations \
    cp -avu /translations/openedx/edx-platform/conf/locale/ conf/ && \
    `# Add a pth file to Python site packages to mimic derex_django installation` \
    echo /openedx/derex_django > $(python -c 'import site; print(site.getsitepackages()[0])')/derex.pth


FROM nostatic as nostatic-dev
# This image has node dependencies installed, and can be used to compile assets

ENV NODE_URL=https://unofficial-builds.nodejs.org/download/release/v10.19.0/node-v10.19.0-linux-x64-musl.tar.xz
# The latest node release does not work on ironwood: its node-sass version fails to compile
# ENV NODE_URL=https://unofficial-builds.nodejs.org/download/release/v12.16.1/node-v12.16.1-linux-x64-musl.tar.xz

WORKDIR /openedx/edx-platform
RUN --mount=type=cache,target=/root/.npm \
    --mount=type=cache,target=/usr/local/share/.cache \
    --mount=type=cache,target=/var/cache/apk \
    --mount=type=cache,target=/root/.cache/pip \
    apk add g++ make coreutils vim mariadb-client && \
    wget ${NODE_URL} -O - | tar --directory / -xJf - && ln -s /node-*/bin/* /usr/local/bin/ && \
    npm install -g yarn@latest && ln -sf /node-*/bin/* /usr/local/bin/ && yarn install && \
    pip install pdbpp ipython ipdb

FROM nostatic-dev as dev-nodump
RUN /usr/local/bin/compile_assets.sh && \
    cleanup_assets.sh

FROM dev-nodump as dev
# This image will be used to compile themes and collect assets

# TODO: fixtures should not be included in the image
COPY fixtures /openedx/fixtures/
COPY migration.py /openedx/edx-platform/lms/envs/derex/
RUN --mount=type=tmpfs,target=/mysql/var/lib/mysql \
    --mount=type=bind,from=docker.io/mysql:5.6.36,target=/mysql,rw=true \
    set -ex; \
    cp /openedx/edx-platform/lms/envs/derex/migration.py /openedx/edx-platform/cms/envs/derex/; \
    cp -a /dev/ /mysql; \
    touch /openedx/edx-platform/lms/envs/derex/__init__.py; \
    touch /openedx/edx-platform/cms/envs/derex/__init__.py; \
    export MYSQL_ALLOW_EMPTY_PASSWORD=1; \
    echo -e '[mysqld]\n'port=3399 >> /mysql/etc/mysql/conf.d/custom_port.cnf; \
    chroot /mysql /usr/local/bin/docker-entrypoint.sh mysqld > /mysql/mysqld.out & \
    until grep "MySQL init process done. Ready for start up" /mysql/mysqld.out ; do sleep 1; done; \
    until chroot /mysql mysqladmin -P 3399 create edxapp ; do sleep 1; done; \
    ./manage.py lms --settings=derex.migration migrate; \
    ./manage.py cms --settings=derex.migration migrate; \
    chroot /mysql mysqldump edxapp | bzip2 -9 - > /openedx/empty_dump.sql.bz2;

ENV DJANGO_SETTINGS_MODULE=lms.envs.derex.migration
ENV SERVICE_VARIANT=lms
ENV DEREX_VERSION=0.0.2.dev6
