from notesserver.settings.common import *
from notesserver.settings.logger import get_logger_config

import os


DEBUG = True

ALLOWED_HOSTS = ["*"]

LOGGING = get_logger_config(debug=DEBUG, dev_env=True, local_loglevel="DEBUG")
del LOGGING["handlers"]["local"]

CLIENT_ID = "edx_notes_api-key"
CLIENT_SECRET = "edx_notes_api-secret"

ES_INDEXES = {"default": "notes_index"}
HAYSTACK_CONNECTIONS["default"]["URL"] = "http://elasticsearch:9200/"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.environ.get("DB_NAME", "derex_notes"),
        "USER": os.environ.get("DB_USER", "root"),
        "PASSWORD": os.environ.get("DB_PASSWORD", "secret"),
        "HOST": os.environ.get("DB_HOST", "mysql"),
        "PORT": os.environ.get("DB_PORT", 3306),
        "CONN_MAX_AGE": 60,
    }
}

JWT_AUTH = {}
