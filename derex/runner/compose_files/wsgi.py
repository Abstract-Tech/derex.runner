from whitenoise import WhiteNoise

import os


service = os.environ["SERVICE_VARIANT"]
assert service in ("lms", "cms")

static_root = {"lms": "/openedx/staticfiles", "cms": "/openedx/staticfiles/studio"}[
    service
]

edx_application = __import__("{}.wsgi".format(service)).wsgi.application  # type: ignore

application = WhiteNoise(edx_application, root=static_root, prefix="/static")
