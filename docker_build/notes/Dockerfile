FROM docker.io/python:2.7.16-alpine3.10
MAINTAINER Silvio Tomatis <silviot@gmail.com>

RUN apk add --no-cache\
     alpine-sdk `# TODO prepare smaller image for distribution` \
     mariadb-connector-c

RUN mkdir -p /edx-notes-api

WORKDIR /edx-notes-api
RUN wget -O - https://github.com/edx/edx-notes-api/tarball/open-release/ironwood.master|tar xzf - --strip-components 1
RUN pip install -r requirements/base.txt --find-links http://pypi.abzt.de/alpine-3.10 --trusted-host pypi.abzt.de
CMD ./manage.py runserver 0.0.0.0:8120
