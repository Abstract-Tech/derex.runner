# About wheels

Currently wheels are hosted on https://wheels.derex.page/.
The current process used to generate them follows:

```
derex build openedx <release> -t wheels
export WHEEL_CONTAINER=$(docker create derex/openedx-juniper-wheels:0.1.0)
export ALPINE_RELEASE=$(docker run --rm derex/openedx-juniper-wheels:0.1.0 cat /etc/alpine-release)
sudo docker cp $WHEEL_CONTAINER:/wheelhouse/. /opt/wheels.derex.page/$ALPINE_RELEASE
docker rm $WHEEL_CONTAINER
```
