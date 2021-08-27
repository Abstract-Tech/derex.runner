from rich.console import Console
from rich.logging import RichHandler

import logging
import os
import sys


def do_setup_logging():
    loglevel = getattr(logging, os.environ.get("DEREX_LOGLEVEL", "WARNING"))
    for logger in ("urllib3.connectionpool", "compose", "docker"):
        logging.getLogger(logger).setLevel(loglevel)

    # python 3.8 introduced the `force` parameter to the basicConfig function
    # but here we do something more brutal to be able to test logging calls
    # After all this function should only be called when invoking click
    # commands, before running the current command.
    logging.getLogger().handlers = []
    logging.basicConfig(
        level=loglevel,
        format="%(message)s",
        datefmt="[%X] ",
        handlers=[RichHandler(console=Console(file=sys.stderr))],
    )


def setup_logging(func):
    """Decorator to run the setup_logging function before the decorated one."""

    def inner(*args, **kwargs):
        do_setup_logging()
        func(*args, **kwargs)

    return inner
