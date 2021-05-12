"""
Bare minimum settings for dumping database migrations.
"""

from openedx.core.lib.derived import derive_settings


# Use a custom mysql port to increase the probability of finding it free on a build machine.
# buildkit seems to always use host networking mode, so it might clash
# Attempts to add `--network=none` to the Dockerfile RUN directives proved fruitless
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "edxapp",
        "HOST": "127.0.0.1",
        "PORT": "3399",
    }
}

# We need to define this, or we get an error
XQUEUE_INTERFACE = {"django_auth": None, "url": None}

derive_settings(__name__)
