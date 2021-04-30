# Alpine docker image

This directory contains scripts to build an Open edX image based
on Alpine Linux. The goal is to have a small image and fast image build.

To achieve the goal of fast image build, image preparation is divided into multiple steps.

The idea behind this is that some parts change more often than others, and we can build base images with the ones that are seldom updated, like operating system dependencies; the same reasoning is done about python wheels and the edx-platform code itself.

These are the images names:

- `openedx-<OPENEDX_VERSION>-buildwheels`: build dependencies included
- `openedx-<OPENEDX_VERSION>-base`: just runtime dependencies
- `openedx-<OPENEDX_VERSION>-sourceonly`: source code included
- `openedx-<OPENEDX_VERSION>-wheels`: build dependencies and wheels built for a specific edx-platform version
- `openedx-<OPENEDX_VERSION>-notranslations`: no build dependencies and wheels from the `wheels` image installed. Will also add a bunch of derex customizations and utility scripts.
- `openedx-<OPENEDX_VERSION>-translations`: setup the transifex-client package and download updated platform translations
- `openedx-<OPENEDX_VERSION>-nostatic`: contains the Open edX source code and all necessary python packages installed. It's still missing static files, hence the name.
- `openedx-<OPENEDX_VERSION>-nostatic-dev`: like nostatic, but includes also node dependencies and all dev tools to generate static files and assets
- `openedx-<OPENEDX_VERSION>-dev`: all edx code and static assets already compiled and collected, with javascript dev tools installed

### Build with translations

In order to build with translations from Transifex the `TRANSIFEX_USERNAME` and `TRANSIFEX_PASSWORD` environment variables must be set in the shell environment running the build.

# About wheels

Currently wheels are hosted on https://wheels.derex.page/.
The current process used to generate and update them follows:

```
export OPENEDX_RELEASE=koa
export DESTINATION=/opt/wheels.derex.page
export DEREX_VERSION=$(python -c "import derex.runner;print(derex.runner.__version__)")

derex build openedx $OPENEDX_RELEASE -t wheels
export WHEELS_CONTAINER=$(docker create docker.io/derex/openedx-$OPENEDX_RELEASE-wheels:$DEREX_VERSION)
export ALPINE_RELEASE=$(docker run --rm docker.io/derex/openedx-$OPENEDX_RELEASE-wheels:$DEREX_VERSION cat /etc/alpine-release)
docker cp $WHEELS_CONTAINER:/wheelhouse/. $DESTINATION/alpine-$ALPINE_RELEASE
docker rm $WHEELS_CONTAINER
```
