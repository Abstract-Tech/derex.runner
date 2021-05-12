"""
Bare minimum settings for collecting production assets.
"""

from openedx.core.lib.derived import derive_settings
from path import Path as path

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

ENABLE_COMPREHENSIVE_THEMING = True
COMPREHENSIVE_THEME_DIRS.append("/openedx/themes")  # type: ignore # noqa: 405
STATIC_ROOT_BASE = os.environ.get("STATIC_ROOT_LMS", "/openedx/staticfiles")
STATIC_ROOT = {  # type: ignore
    "lms": path(STATIC_ROOT_BASE),
    "cms": path(STATIC_ROOT_BASE) / "studio",
}[SERVICE_VARIANT]
WEBPACK_LOADER["DEFAULT"]["STATS_FILE"] = (  # type: ignore # noqa: 405
    STATIC_ROOT / "webpack-stats.json"
)

SECRET_KEY = "secret"
XQUEUE_INTERFACE = {"django_auth": None, "url": None}
DATABASES = {"default": {}}  # type: ignore

# enterprise.views tries to access settings.ECOMMERCE_PUBLIC_URL_ROOT,
ECOMMERCE_PUBLIC_URL_ROOT = None

STATICFILES_STORAGE = "derex_django.staticfiles_storages.WhitenoiseEdxStorage"
derive_settings(__name__)
