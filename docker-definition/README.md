# About wheels

Currently wheels are hosted on https://wheels.derex.page/.
The current process used to generate them follows:

```
derex build openedx <release> -t wheels
export WHEEL_CONTAINER=$(docker create docker.io/derex/openedx-<release>-wheels:<derex version>)
export ALPINE_RELEASE=$(docker run --rm docker.io/derex/openedx-<release>-wheels:<derex version> cat /etc/alpine-release)
sudo docker cp $WHEEL_CONTAINER:/wheelhouse/. /opt/wheels.derex.page/alpine-$ALPINE_RELEASE
docker rm $WHEEL_CONTAINER
```
