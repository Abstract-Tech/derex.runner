from openedx.core.djangoapps.plugins import constants as plugin_constants
from openedx.core.djangoapps.plugins import plugin_settings
from openedx.core.lib.derived import derive_settings
from path import Path

import os
import sys


SERVICE_VARIANT = os.environ["SERVICE_VARIANT"]
assert SERVICE_VARIANT in ("lms", "cms")
PROJECT_TYPE = getattr(plugin_constants.ProjectType, SERVICE_VARIANT.upper())
exec("from {}.envs.derex.base import *".format(SERVICE_VARIANT), globals(), locals())

if SERVICE_VARIANT == "lms":
    SITE_NAME = "localhost:4700"
else:
    SITE_NAME = "localhost:4800"

if "runserver" in sys.argv:
    SITE_NAME = SITE_NAME[:-1] + "1"

STATIC_ROOT_BASE = "/openedx/staticfiles"

MEDIA_ROOT = "/openedx/media"
VIDEO_TRANSCRIPTS_SETTINGS["location"] = MEDIA_ROOT  # type: ignore  # noqa
VIDEO_IMAGE_SETTINGS["STORAGE_KWARGS"]["location"] = MEDIA_ROOT  # type: ignore  # noqa
PROFILE_IMAGE_BACKEND["options"]["location"] = MEDIA_ROOT  # type: ignore  # noqa
COMPREHENSIVE_THEME_DIRS.append(Path("/openedx/themes"))  # type: ignore  # noqa
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

plugin_settings.add_plugins(
    __name__, PROJECT_TYPE, plugin_constants.SettingsType.PRODUCTION
)

derive_settings(__name__)
