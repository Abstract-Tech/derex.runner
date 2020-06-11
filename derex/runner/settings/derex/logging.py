from openedx.core.lib.logsettings import get_logger_config
from packaging.version import parse as version_parse

import django
import os
import sys


DJANGO_VERSION = version_parse(django.__version__)


LOG_DIR = "/openedx/logs"
TRACKING_LOGS_DIR = os.path.join(LOG_DIR, "tracking")
LOGGING_ENV = "staging"
LOGGING = get_logger_config(
    LOG_DIR,
    logging_env=LOGGING_ENV,
    local_loglevel="INFO",
    service_variant=SERVICE_VARIANT,
)

LOGGING["handlers"]["console"] = {
    "level": "INFO",
    "class": "logging.StreamHandler",
    "formatter": "standard",
    "stream": sys.stderr,
}
LOGGING["handlers"]["local"] = {
    "level": "INFO",
    "class": "logging.handlers.RotatingFileHandler",
    "filename": os.path.join(LOG_DIR, "info.log"),
    "maxBytes": 1024 * 1024 * 10,  # 10MB
    "formatter": "standard",
}
LOGGING["handlers"]["error"] = {
    "level": "ERROR",
    "class": "logging.handlers.RotatingFileHandler",
    "filename": os.path.join(LOG_DIR, "error.log"),
    "maxBytes": 1024 * 1024 * 10,  # 10MB
    "formatter": "standard",
}
LOGGING["handlers"]["tracking"] = {
    "level": "DEBUG",
    "class": "logging.handlers.RotatingFileHandler",
    "filename": os.path.join(TRACKING_LOGS_DIR, "tracking.log"),
    "maxBytes": 1024 * 1024 * 10,  # 10MB
    "formatter": "raw",
}
LOGGING["loggers"][""]["handlers"] = ["console", "local", "error"]


# Enable userid_context filter if on Juniper or later
if DJANGO_VERSION > version_parse("2"):
    LOGGING["handlers"]["console"]["filters"] = ["userid_context"]
    LOGGING["handlers"]["local"]["filters"] = ["userid_context"]


# TODO: Remove this when we are able to properly
# mount logs volumes
for directory in [LOG_DIR, TRACKING_LOGS_DIR]:
    if not os.path.exists(directory):
        os.makedirs(directory)
