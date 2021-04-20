# About wheels

Currently wheels are hosted on https://wheels.derex.page/.
The current process used to generate them follows:

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
