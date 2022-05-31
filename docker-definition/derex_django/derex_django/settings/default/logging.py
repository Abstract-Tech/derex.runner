from openedx.core.lib.logsettings import get_logger_config

import os
import sys


LOG_DIR = "/openedx/logs"
TRACKING_LOGS_DIR = os.path.join(LOG_DIR, "tracking")
LOGGING_ENV = "staging"
LOGGING = get_logger_config(
    LOG_DIR,
    logging_env=LOGGING_ENV,
    local_loglevel="INFO",
    service_variant=SERVICE_VARIANT,
)
LOGGING["handlers"]["console"].update(
    {
        "level": "INFO",
        "class": "logging.StreamHandler",
        "formatter": "standard",
        "stream": sys.stderr,
    }
)
LOGGING["handlers"]["local"].update(
    {
        "level": "INFO",
        "class": "logging.handlers.RotatingFileHandler",
        "filename": os.path.join(LOG_DIR, "info.log"),
        "maxBytes": 1024 * 1024 * 10,  # 10MB
        "formatter": "standard",
    }
)
LOGGING["handlers"]["local"].pop("address", None)
LOGGING["handlers"]["local"].pop("facility", None)

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

LOGGING["handlers"]["mail_admins"] = {
    "level": "ERROR",
    "class": "django.utils.log.AdminEmailHandler",
    "email_backend": "django.core.mail.backends.smtp.EmailBackend",
    "include_html": True,
}

LOGGING["loggers"][""]["handlers"] = ["console", "local", "error"]


# TODO: Remove this when we are able to properly
# mount logs volumes
for directory in [LOG_DIR, TRACKING_LOGS_DIR]:
    if not os.path.exists(directory):
        os.makedirs(directory)
