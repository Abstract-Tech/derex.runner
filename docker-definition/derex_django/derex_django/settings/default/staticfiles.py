from path import Path

import sys


STATIC_ROOT_BASE = "/openedx/staticfiles"
STATIC_ROOT = {
    "lms": Path(STATIC_ROOT_BASE),
    "cms": Path(STATIC_ROOT_BASE) / "studio",
}[SERVICE_VARIANT]
STATIC_URL = {"lms": "/static/", "cms": "/static/studio/",}[  # noqa: E231
    SERVICE_VARIANT
]

WEBPACK_LOADER["DEFAULT"]["STATS_FILE"] = STATIC_ROOT / "webpack-stats.json"
COMPREHENSIVE_THEME_DIRS.append(Path("/openedx/themes"))
STATICFILES_STORAGE = "derex_django.staticfiles_storages.WhitenoiseEdxStorage"

if "runserver" in sys.argv:
    REQUIRE_DEBUG = True
    STATICFILES_STORAGE = "openedx.core.storage.DevelopmentStorage"
    # Load development webpack donfiguration
    WEBPACK_CONFIG_PATH = "webpack.dev.config.js"

    if sys.version_info.major < 3:
        PIPELINE_ENABLED = False
        # Disable JavaScript compression in development
        PIPELINE_JS_COMPRESSOR = None
        # Whether to run django-require in debug mode.
        PIPELINE_SASS_ARGUMENTS = "--debug-info"
        # Revert to the default set of finders as we don't want the production pipeline
        STATICFILES_FINDERS = [
            "openedx.core.djangoapps.theming.finders.ThemeFilesFinder",
            "django.contrib.staticfiles.finders.FileSystemFinder",
            "django.contrib.staticfiles.finders.AppDirectoriesFinder",
        ]
    else:
        # Disable JavaScript compression in development
        PIPELINE["JS_COMPRESSOR"] = None
        PIPELINE["PIPELINE_ENABLED"] = False
        PIPELINE["SASS_ARGUMENTS"] = "--debug-info"

if sys.version_info.major > 2:
    # django-pipeline may try to set mimetypes
    # as bytes in python3 causing errors when uploading
    # to MinIO
    PIPELINE["MIMETYPES"] = (
        ("text/coffeescript", ".coffee"),
        ("text/less", ".less"),
        ("text/javascript", ".js"),
        ("text/x-sass", ".sass"),
        ("text/x-scss", ".scss"),
    )
