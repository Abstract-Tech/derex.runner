"""
Bare minimum settings for dumping database migrations.
"""

from derex_django.constants import DEREX_OPENEDX_SUPPORTED_VERSIONS
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

try:
    DEREX_OPENEDX_VERSION = os.environ["DEREX_OPENEDX_VERSION"]
    assert DEREX_OPENEDX_VERSION in DEREX_OPENEDX_SUPPORTED_VERSIONS
except KeyError:
    raise RuntimeError("DEREX_OPENEDX_VERSION environment variable must be defined!")
except AssertionError:
    raise RuntimeError(
        "DEREX_OPENEDX_VERSION must be on of {}".format(
            DEREX_OPENEDX_SUPPORTED_VERSIONS
        )
    )

if DEREX_OPENEDX_VERSION == "koa":
    # Since we installed django_celery_beat to take advantage from the
    # database scheduler we need to run its migrations too
    INSTALLED_APPS.extend(["django_celery_beat"])  # type: ignore # noqa: F401, F405

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
