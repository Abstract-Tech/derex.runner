from whitenoise import WhiteNoise

import os


service = os.environ["SERVICE_VARIANT"]
assert service in ("lms", "cms")


edx_application = __import__("{}.wsgi".format(service)).wsgi.application  # type: ignore

application = WhiteNoise(edx_application, root="/openedx/staticfiles", prefix="/static")
