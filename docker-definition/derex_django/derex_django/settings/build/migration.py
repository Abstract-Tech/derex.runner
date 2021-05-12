"""
Bare minimum settings for dumping database migrations.
"""

from openedx.core.lib.derived import derive_settings

import os


try:
    SERVICE_VARIANT = os.environ["SERVICE_VARIANT"]
    assert SERVICE_VARIANT in ["lms", "cms"]
except KeyError:
    raise RuntimeError("SERVICE_VARIANT environment variable must be defined!")
except AssertionError:
    raise RuntimeError(
        'SERVICE_VARIANT environment variable must be one of ["lms", "cms"]'
    )

if SERVICE_VARIANT == "lms":
    from lms.envs.common import *  # noqa: F401, F403
if SERVICE_VARIANT == "cms":
    from cms.envs.common import *  # noqa: F401, F403

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
