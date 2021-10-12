# syntax = docker/dockerfile:experimental

# Debugging a Dockerfile can be difficult. A good pattern is to put a breakpoint, enter
# the build container and have a look. To do this, put the command
# sleep infinity
# in the place you want to examine. When execution stops there, run
# sudo nsenter --target $(pgrep sleep) --mount --uts --ipc --net --pid sh

ARG ALPINE_VERSION=alpine3.11
ARG PYTHON_VERSION=3.6
FROM docker.io/python:${PYTHON_VERSION}-${ALPINE_VERSION} as libgeos

RUN --mount=type=cache,target=/var/cache/apk apk add alpine-sdk
ENV GEOS_VERSION=3.8.0

RUN wget -c http://download.osgeo.org/geos/geos-${GEOS_VERSION}.tar.bz2 -O - | tar xjf - --directory /usr/local && \
    cd /usr/local/geos-${GEOS_VERSION} && ./configure && make -j 4 && make install

FROM docker.io/python:${PYTHON_VERSION}-${ALPINE_VERSION} as base
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
    wget \
    bash

COPY scripts/derex_patch_ldconfig_to_fix_shapely /tmp/derex_patch_ldconfig_to_fix_shapely

COPY --from=libgeos /usr/local/lib/libgeos* /usr/lib/
# Patch ldconfig and test that libgeos works
RUN /tmp/derex_patch_ldconfig_to_fix_shapely && \
     python -c "from  ctypes import CDLL; CDLL('$(echo /usr/lib/libgeos_c.so)').GEOSversion"

# we want to use paver without remembering to specify these
ENV NO_PREREQ_INSTALL=True
ENV NO_PYTHON_UNINSTALL=True

ARG PIP_VERSION=21.0.1
RUN pip install -U pip==${PIP_VERSION}

FROM base as sourceonly
ARG EDX_PLATFORM_RELEASE=koa
ARG EDX_PLATFORM_VERSION=open-release/koa.master
ARG EDX_PLATFORM_REPOSITORY=https://github.com/edx/edx-platform.git

RUN mkdir -p /openedx/themes /openedx/locale /openedx/bin/ /openedx/requirements/ && \
    git clone ${EDX_PLATFORM_REPOSITORY} --branch ${EDX_PLATFORM_VERSION} --depth 1 /openedx/edx-platform
# Copy derex overrides to edx-platform source code
COPY openedx_customizations/${EDX_PLATFORM_RELEASE} /openedx/edx-platform

WORKDIR /openedx/edx-platform
COPY requirements/${EDX_PLATFORM_RELEASE}/* /openedx/requirements/
# The following layer is going to produce 3 requirements file:
# * edx base requirements with some fixes which will be installed (openedx_base_fixed.txt)
# * edx base requirements with relative paths converted to absolute paths which will be
#   used to create wheels (openedx_wheels.txt)
# * edx base requirements without links and extras to be used as constraints (openedx_constraints.txt)
RUN cp /openedx/edx-platform/requirements/edx/base.txt /openedx/requirements/openedx_base_fixed.txt && \
    `# Versioning of this package is wrong at the pinned commit` \
    sed -e "s|django-oauth-plus.git@01ec2a161dfc3465f9d35b9211ae790177418316|django-oauth-plus.git@6218624ef19aea37c5abec35b4ea2e049dc8ee4e|" -i /openedx/requirements/openedx_base_fixed.txt && \
    `# Without the following line pip produces an error:` \
    `# Generating metadata for package <package> produced metadata for project name django-ratelimit. Fix your #egg=ratelimit fragments.` \
    sed -e "s|#egg=ratelimit|#egg=django-ratelimit|" -i /openedx/requirements/openedx_base_fixed.txt && \
    sed -e "s|#egg=pystache_custom-dev|#egg=pystache-custom|" -i /openedx/requirements/openedx_base_fixed.txt && \
    cat /openedx/requirements/openedx_base_fixed.txt | sed -e "/git+https/!s/-e /-e \/openedx\/edx-platform\//" > /openedx/requirements/openedx_wheels.txt && \
    `# scipy 1.4.1 has a problem and does not build. Our fork includes a fix` \
    sed -e "s|.*scipy==1.4.1.*|https://github.com/Abstract-Tech/scipy/tarball/maintenance/1.4.x#egg=scipy|" -i /openedx/requirements/openedx_wheels.txt && \
    `# From version 20.3 pip use a new dependency resolver which doesn t accept extras or links as constraints` \
    `# Read more at https://github.com/pypa/pip/issues/8210` \
    cat /openedx/requirements/openedx_wheels.txt | grep -v github | grep -v ^-e | sed -e "s|\[.*\]||" > /openedx/requirements/openedx_constraints.txt

FROM sourceonly as wheels

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
    sqlite-dev \
    swig \
    xmlsec-dev && \
    `# From https://github.com/jfloff/alpine-python/issues/32` \
    sed '/st_mysql_options options;/a unsigned int reconnect;' /usr/include/mysql/mysql.h -i

# Latest versions of cryptography requires the newest version of Rust to build successfully
# Unfortunately alpine versions prior to 3.13 doesn't include it
ENV CRYPTOGRAPHY_DONT_BUILD_RUST=1

RUN --mount=type=cache,target=/root/.cache/pip \
    export PIP_FIND_LINKS="https://wheels.derex.page/alpine-$(cat /etc/alpine-release)" && \
    `# xmlsec is a dependecy of python-saml.` \
    `# We need to build it with this flag in order to avoid this error on import:` \
    `# xmlsec.Error: (19, 'xmlsec library version mismatch.')` \
    export CFLAGS=-DXMLSEC_NO_SIZE_T && \
    `# We need to add the --no-verify option due to django-oauth-plus metadata` \
    `# violating PEP 440 (https://www.python.org/dev/peps/pep-0440/)` \
    pip wheel --wheel-dir=/wheelhouse -r /openedx/requirements/openedx_wheels.txt --no-verify
RUN --mount=type=cache,target=/root/.cache/pip \
    export PIP_FIND_LINKS="https://wheels.derex.page/alpine-$(cat /etc/alpine-release)" && \
    pip wheel --wheel-dir=/wheelhouse -r /openedx/requirements/derex.txt -c /openedx/requirements/openedx_constraints.txt
RUN --mount=type=cache,target=/root/.cache/pip \
    export PIP_FIND_LINKS="https://wheels.derex.page/alpine-$(cat /etc/alpine-release)" && \
    pip wheel --wheel-dir=/wheelhouse -r /openedx/requirements/overrides.txt

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

RUN --mount=type=cache,target=/root/.cache/pip --mount=type=bind,source=/wheelhouse,from=wheels,target=/wheelhouse \
    pip install -r /openedx/requirements/openedx_base_fixed.txt --find-links /wheelhouse

RUN --mount=type=cache,target=/root/.cache/pip --mount=type=bind,source=/wheelhouse,from=wheels,target=/wheelhouse \
    pip install -U -r /openedx/requirements/derex.txt --find-links /wheelhouse -c /openedx/requirements/openedx_constraints.txt

RUN --mount=type=cache,target=/root/.cache/pip --mount=type=bind,source=/wheelhouse,from=wheels,target=/wheelhouse \
    pip install -U -r /openedx/requirements/overrides.txt --find-links /wheelhouse

COPY derex_django/ /openedx/derex_django
RUN --mount=type=cache,target=/root/.cache/pip --mount=type=bind,source=/wheelhouse,from=wheels,target=/wheelhouse \
    pip install /openedx/derex_django --find-links /wheelhouse

COPY scripts/* scripts/assets/* /tmp/

RUN cp /tmp/derex* /usr/local/bin/ && chmod +x /usr/local/bin/*

FROM notranslations as translations

RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=secret,id=transifex,dst=/root/.transifexrc-orig \
    pip install transifex-client -c /openedx/requirements/openedx_constraints.txt && \
    export DJANGO_SETTINGS_MODULE="derex_django.settings.build.translations" && \
    derex_update_translations

FROM notranslations as nostatic
# This image contains the Open edX source code and all necessary python packages installed.
# It's still missing the static files, hence the name.

RUN --mount=type=bind,from=translations,target=/translations \
    cp -avu /translations/openedx/edx-platform/conf/locale/ conf/

FROM nostatic as nostatic-dev
# This image has node dependencies installed, and can be used to compile assets

ARG NODE_VERSION=v10.22.1
ENV NODE_URL=https://unofficial-builds.nodejs.org/download/release/${NODE_VERSION}/node-${NODE_VERSION}-linux-x64-musl.tar.xz

WORKDIR /openedx/edx-platform
RUN --mount=type=cache,target=/root/.npm \
    --mount=type=cache,target=/usr/local/share/.cache \
    --mount=type=cache,target=/var/cache/apk \
    --mount=type=cache,target=/root/.cache/pip \
    apk add g++ make coreutils vim mariadb-client && \
    wget ${NODE_URL} -O - | tar --directory / -xJf - && ln -s /node-*/bin/* /usr/local/bin/ && \
    npm install --unsafe-perm

FROM nostatic-dev as dev-nodump
RUN derex_update_assets && derex_cleanup_assets

FROM dev-nodump as dev
# This image will be used to compile themes and collect assets

# TODO: fixtures should not be included in the image
COPY fixtures /openedx/fixtures/
RUN --mount=type=tmpfs,target=/mysql/var/lib/mysql \
    --mount=type=bind,from=docker.io/mysql:5.6.36,target=/mysql,rw=true \
    set -ex; \
    cp -a /dev/ /mysql; \
    export MYSQL_ALLOW_EMPTY_PASSWORD=1; \
    echo -e '[mysqld]\nport=3399\ncollation-server = utf8_general_ci\ncharacter-set-server = utf8' >> /mysql/etc/mysql/conf.d/custom_port.cnf; \
    chroot /mysql /usr/local/bin/docker-entrypoint.sh mysqld > /mysql/mysqld.out & \
    until grep "MySQL init process done. Ready for start up" /mysql/mysqld.out ; do sleep 1; done; \
    until chroot /mysql mysqladmin -P 3399 create edxapp ; do sleep 1; done; \
    export DJANGO_SETTINGS_MODULE="derex_django.settings.build.migration"; \
    export DEREX_OPENEDX_VERSION=${EDX_PLATFORM_RELEASE}; \
    SERVICE_VARIANT="lms" python manage.py lms migrate; \
    SERVICE_VARIANT="cms" python manage.py cms migrate; \
    chroot /mysql mysqldump edxapp | bzip2 -9 - > /openedx/empty_dump.sql.bz2;

ENV DJANGO_SETTINGS_MODULE=derex_django.settings.default
ENV SERVICE_VARIANT=lms
ENV DEREX_VERSION=0.3.2
