from openedx.core.lib.derived import derive_settings
from path import Path as path
from xmodule.modulestore.modulestore_settings import update_module_store_settings

import os


SERVICE_VARIANT = os.environ["SERVICE_VARIANT"]
assert SERVICE_VARIANT in ("lms", "cms")

exec("from {}.envs.common import *".format(SERVICE_VARIANT), globals(), locals())

PLATFORM_NAME="TestEdX"
# XXX Remove CONFIG_ROOT: it's the path to the JSON files we're getting rid of
# Instead, we could just import something we KNOW comes from `edx-platform`
# and base other paths on that one.
ENV_ROOT = (path(os.environ["CONFIG_ROOT"]) / "..").normpath()
DATA_DIR = ENV_ROOT / "data"
LOG_DIR = "/openedx/data/logs"
SERVICE_VARIANT = os.environ["SERVICE_VARIANT"]
assert SERVICE_VARIANT in ("lms", "cms")

DATABASES = {
    "default": {
        "ATOMIC_REQUESTS": True,
        "ENGINE": "django.db.backends.mysql",
        "HOST": "mysql",
        "NAME": "myedx",
        "PASSWORD": "secret",
        "PORT": "3306",
        "USER": "root",
    }
}

CONTENTSTORE = {
    "ENGINE": "xmodule.contentstore.mongo.MongoContentStore",
    "DOC_STORE_CONFIG": {"host": "mongodb", "db": "mongoedx"},
}
DOC_STORE_CONFIG = {"host": "mongodb", "db": "mongoedx"}
update_module_store_settings(MODULESTORE, doc_store_settings=DOC_STORE_CONFIG)

XQUEUE_INTERFACE = {"url": None, "django_auth": None}
ALLOWED_HOSTS = ["*"]

# Not often changed nor in need of customization - move to a different file perhaps
# Let an environment variable control debug mode
DEBUG = bool(os.environ.get('DEBUG', False))
if DEBUG:  # In debug mode serve static files from `runserver`
    PIPELINE_ENABLED = False
    STATICFILES_STORAGE = 'openedx.core.storage.DevelopmentStorage'
    # Revert to the default set of finders as we don't want the production pipeline
    STATICFILES_FINDERS = [
        'openedx.core.djangoapps.theming.finders.ThemeFilesFinder',
        'django.contrib.staticfiles.finders.FileSystemFinder',
        'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    ]
    # Disable JavaScript compression in development
    PIPELINE_JS_COMPRESSOR = None
    # Whether to run django-require in debug mode.
    REQUIRE_DEBUG = DEBUG
    PIPELINE_SASS_ARGUMENTS = '--debug-info'
    # Load development webpack donfiguration
    WEBPACK_CONFIG_PATH = 'webpack.dev.config.js'


##################### CMS Settings ###################

if SERVICE_VARIANT == 'cms':
    CMS_SEGMENT_KEY = 'foobar'
    LOGIN_URL = '/signin'
    FRONTEND_LOGIN_URL = LOGIN_URL

derive_settings(__name__)
