FROM node:12-alpine AS base

RUN apk add --no-cache \
    git \
    autoconf \
    automake \
    build-base \
    libpng-dev \
    pngquant

RUN mkdir -p /openedx/microfrontend
WORKDIR /openedx/microfrontend
ENV PATH ./node_modules/.bin:${PATH}

FROM base AS sourceonly
RUN git clone https://github.com/edx/frontend-app-profile.git \
    --branch open-release/lilac.master --depth 1 /openedx/microfrontend
RUN npm install
COPY .env.derex .env
RUN npm run build

FROM docker.io/caddy:2.3.0-alpine

RUN mkdir -p /openedx/dist
COPY --from=sourceonly \
    /openedx/microfrontend/dist /srv/microfrontend
COPY ./Caddyfile /etc/caddy/Caddyfile
