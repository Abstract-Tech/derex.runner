from rich.logging import RichHandler

import logging
import os


class CustomFormatter(logging.Formatter):
    """Logging Formatter to add colors and count warning / errors"""

    grey = "\x1b[38;21m"
    yellow = "\x1b[33;21m"
    red = "\x1b[31;21m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    logging_format = "%(message)s"

    FORMATS = {
        logging.DEBUG: grey + logging_format + reset,
        logging.INFO: grey + logging_format + reset,
        logging.WARNING: yellow + logging_format + reset,
        logging.ERROR: red + logging_format + reset,
        logging.CRITICAL: bold_red + logging_format + reset,
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def setup_logging():
    FORMAT = "%(message)s"
    loglevel = getattr(logging, os.environ.get("DEREX_LOGLEVEL", "WARN"))
    for logger in ("urllib3.connectionpool", "compose", "docker"):
        logging.getLogger(logger).setLevel(logging.WARN)
    logging.basicConfig(
        level=loglevel, format=FORMAT, datefmt="[%X] ", handlers=[RichHandler()],
    )


def setup_logging_decorator(func):
    """Decorator to run the setup_logging function before the decorated one.
    """

    def inner(*args, **kwargs):
        setup_logging()
        func(*args, **kwargs)

    return inner
