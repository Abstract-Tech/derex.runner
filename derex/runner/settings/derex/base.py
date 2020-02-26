# type: ignore
# flake8: noqa

from kombu.utils.functional import maybe_list
from openedx.core.djangoapps.plugins import constants as plugin_constants
from openedx.core.djangoapps.plugins import plugin_settings
from openedx.core.lib.derived import derive_settings
from path import Path
from xmodule.modulestore.modulestore_settings import update_module_store_settings

import os


SERVICE_VARIANT = os.environ["SERVICE_VARIANT"]
assert SERVICE_VARIANT in ("lms", "cms")

exec("from {}.envs.common import *".format(SERVICE_VARIANT), globals(), locals())

PLATFORM_NAME = "TestEdX"
MYSQL_HOST = os.environ.get("MYSQL_HOST", "mysql")
MYSQL_PORT = os.environ.get("MYSQL_PORT", "3306")
MYSQL_DB = os.environ.get("MYSQL_DB", "derex")
MYSQL_USER = os.environ.get("MYSQL_USER", "root")
MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "secret")
DATABASES = {
    "default": {
        "ATOMIC_REQUESTS": True,
        "ENGINE": "django.db.backends.mysql",
        "HOST": MYSQL_HOST,
        "NAME": MYSQL_DB,
        "PASSWORD": MYSQL_PASSWORD,
        "PORT": MYSQL_PORT,
        "USER": MYSQL_USER,
    }
}
MONGODB_HOST = "mongodb"
MONGODB_DB = os.environ.get("MONGO_DB", "mongoedx")
CONTENTSTORE = {
    "ENGINE": "xmodule.contentstore.mongo.MongoContentStore",
    "DOC_STORE_CONFIG": {"host": MONGODB_HOST, "db": MONGODB_DB},
}
DOC_STORE_CONFIG = {"host": MONGODB_HOST, "db": MONGODB_DB}
update_module_store_settings(MODULESTORE, doc_store_settings=DOC_STORE_CONFIG)

XQUEUE_INTERFACE = {"url": None, "django_auth": None}
ALLOWED_HOSTS = ["*"]

# Default value
CELERY_BROKER_VHOST = "/"

# Per-project db separation
DEREX_PROJECT = os.environ.get("DEREX_PROJECT")
if DEREX_PROJECT:
    # Setup mysql database
    MYSQL_DB = "{}_myedx".format(DEREX_PROJECT)
    DATABASES["default"]["NAME"] = MYSQL_DB

    # Mongodb
    MONGODB_DB = "{}_mongoedx".format(DEREX_PROJECT)
    DOC_STORE_CONFIG["db"] = MONGODB_DB
    CONTENTSTORE["DOC_STORE_CONFIG"] = DOC_STORE_CONFIG
    for store in MODULESTORE["default"]["OPTIONS"]["stores"]:
        store["DOC_STORE_CONFIG"]["db"] = MONGODB_DB

    CELERY_BROKER_VHOST = "{}_edxqueue".format(DEREX_PROJECT)

if "runserver" in sys.argv:
    DEBUG = True
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
    REQUIRE_DEBUG = DEBUG
    PIPELINE_SASS_ARGUMENTS = "--debug-info"
    # Load development webpack donfiguration
    WEBPACK_CONFIG_PATH = "webpack.dev.config.js"

EMAIL_HOST = os.environ.get("EMAIL_HOST", "smtp")
EMAIL_PORT = os.environ.get("EMAIL_PORT", "25")
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

##################### Celery #######################
CELERY_BROKER_TRANSPORT = os.environ.get("CELERY_BROKER_TRANSPORT", "amqp")
CELERY_BROKER_HOSTNAME = os.environ.get("CELERY_BROKER_HOSTNAME", "rabbitmq")
CELERY_BROKER_USER = os.environ.get("CELERY_BROKER_USER", "guest")
CELERY_BROKER_PASSWORD = os.environ.get("CELERY_BROKER_PASSWORD", "guest")
BROKER_URL = "{0}://{1}:{2}@{3}/{4}".format(
    CELERY_BROKER_TRANSPORT,
    CELERY_BROKER_USER,
    CELERY_BROKER_PASSWORD,
    CELERY_BROKER_HOSTNAME,
    CELERY_BROKER_VHOST,
)
CELERY_RESULT_BACKEND = "mongodb://{MONGODB_HOST}/".format(**locals())
CELERY_MONGODB_BACKEND_SETTINGS = {
    "database": MONGODB_DB,
    "taskmeta_collection": "taskmeta_collection",
}

CELERY_RESULT_DB_TABLENAMES = {"task": "celery_edx_task", "group": "celery_edx_group"}

CELERY_QUEUES = {"lms.default": {}, "cms.default": {}}
CELERY_ROUTES = "{}.celery.Router".format(SERVICE_VARIANT)
CELERY_DEFAULT_QUEUE = "{}.default".format(SERVICE_VARIANT)

##################### CMS Settings ###################

LMS_BASE = "http://localhost:4700"

if SERVICE_VARIANT == "cms":
    CMS_SEGMENT_KEY = "foobar"
    LOGIN_URL = "/signin"
    FRONTEND_LOGIN_URL = LOGIN_URL

# enterprise.views tries to access settings.ECOMMERCE_PUBLIC_URL_ROOT,
ECOMMERCE_PUBLIC_URL_ROOT = None

# Provide a default for SITE_NAME
# It will be overridden later, if an `lms_site_name` variable has been specified in the config
SITE_NAME = {"lms": "localhost:4700", "cms": "localhost:4700"}[SERVICE_VARIANT]

STATIC_ROOT_BASE = "/openedx/staticfiles"
COMPREHENSIVE_THEME_DIRS.append("/openedx/themes")  # type: ignore
STATIC_ROOT_BASE = os.environ.get("STATIC_ROOT_LMS", "/openedx/staticfiles")
STATIC_ROOT = {  # type: ignore
    "lms": path(STATIC_ROOT_BASE),
    "cms": path(STATIC_ROOT_BASE) / "studio",
}[os.environ.get("SERVICE_VARIANT")]
WEBPACK_LOADER["DEFAULT"]["STATS_FILE"] = (  # type: ignore
    STATIC_ROOT / "webpack-stats.json"
)


MEDIA_ROOT = "/openedx/media"
VIDEO_TRANSCRIPTS_SETTINGS["location"] = MEDIA_ROOT  # type: ignore  # noqa
VIDEO_IMAGE_SETTINGS["STORAGE_KWARGS"]["location"] = MEDIA_ROOT  # type: ignore  # noqa
PROFILE_IMAGE_BACKEND["options"]["location"] = MEDIA_ROOT  # type: ignore  # noqa
COMPREHENSIVE_THEME_DIRS.append(Path("/openedx/themes"))  # type: ignore  # noqa
# STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
PROJECT_TYPE = getattr(plugin_constants.ProjectType, SERVICE_VARIANT.upper())


####################### Plugin Settings ##########################

# Adding plugins for AWS chokes if these are not defined
ENV_TOKENS = {}
AUTH_TOKENS = {}

# This is at the bottom because it is going to load more settings after base settings are loaded

# Load aws.py in plugins for reverse compatibility.  This can be removed after aws.py
# is officially removed.
plugin_settings.add_plugins(__name__, PROJECT_TYPE, plugin_constants.SettingsType.AWS)

# We continue to load production.py over aws.py

plugin_settings.add_plugins(
    __name__, PROJECT_TYPE, plugin_constants.SettingsType.PRODUCTION
)


CELERY_IMPORTS = locals().get("CELERY_IMPORTS", [])
####################### Celery fix ##########################
# XXX for some reason celery is not registering the bookmarks app
CELERY_IMPORTS = list(maybe_list(CELERY_IMPORTS)) + [
    "openedx.core.djangoapps.bookmarks.tasks"
]

########################## This container should never be exposed directly  #######################
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

########################## Derive Any Derived Settings  #######################


########################## Features #########################
FEATURES = locals().get("FEATURES", {})
FEATURES.update(
    {"ENABLE_COMBINED_LOGIN_REGISTRATION": True, "ENABLE_DISCUSSION_SERVICE": False}
)

from .container_env import *  # isort:skip

derive_settings(__name__)
