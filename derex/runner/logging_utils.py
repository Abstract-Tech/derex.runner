from rich.logging import RichHandler

import logging
import os


def setup_logging():
    loglevel = getattr(logging, os.environ.get("DEREX_LOGLEVEL", "WARN"))
    logging.basicConfig(
        level=loglevel, format="%(message)s", datefmt="[%X] ", handlers=[RichHandler()],
    )


def setup_logging_decorator(func):
    """Decorator to run the setup_logging function before the decorated one.
    """

    def inner(*args, **kwargs):
        setup_logging()
        func(*args, **kwargs)

    return inner
