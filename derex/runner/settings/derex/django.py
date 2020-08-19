import sys


ALLOWED_HOSTS = ["*"]
# This container should never be exposed directly
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
X_FRAME_OPTIONS = "SAMEORIGIN"

if "runserver" in sys.argv:
    DEBUG = True
else:
    DEBUG = False
