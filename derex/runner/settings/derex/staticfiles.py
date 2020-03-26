from path import Path


STATIC_ROOT_BASE = "/openedx/staticfiles"
STATIC_ROOT = {  # type: ignore
    "lms": Path(STATIC_ROOT_BASE),
    "cms": Path(STATIC_ROOT_BASE) / "studio",
}[SERVICE_VARIANT]

WEBPACK_LOADER["DEFAULT"]["STATS_FILE"] = (  # type: ignore
    STATIC_ROOT / "webpack-stats.json"
)
COMPREHENSIVE_THEME_DIRS.append(Path("/openedx/themes"))  # type: ignore  # noqa
# STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

if "runserver" in sys.argv:
    REQUIRE_DEBUG = True
    PIPELINE_ENABLED = False
    STATICFILES_STORAGE = "openedx.core.storage.DevelopmentStorage"
    # Revert to the default set of finders as we don't want the production pipeline
    STATICFILES_FINDERS = [
        "openedx.core.djangoapps.theming.finders.ThemeFilesFinder",
        "django.contrib.staticfiles.finders.FileSystemFinder",
        "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    ]
    # Disable JavaScript compression in development
    PIPELINE_JS_COMPRESSOR = None
    # Whether to run django-require in debug mode.
    PIPELINE_SASS_ARGUMENTS = "--debug-info"
    # Load development webpack donfiguration
    WEBPACK_CONFIG_PATH = "webpack.dev.config.js"
