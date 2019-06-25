# -*- coding: utf-8 -*-

"""Console script for derex.runner."""
import sys
from derex.runner.utils import run_compose
import logging


def setup_logging():
    logging.basicConfig()
    for logger in ("urllib3.connectionpool", "compose", "docker"):
        logging.getLogger(logger).setLevel(logging.WARN)
    logging.getLogger("").setLevel(logging.INFO)


def ddc():
    """Derex docker-compose: run docker-compose with additional parameters.
    Adds docker compose file paths for services and administrative tools.
    If the environment variable DEREX_ADMIN_SERVICES is set to a falsey value,
    only the core ones will be started (mysql, mongodb etc).
    """
    setup_logging()
    run_compose(list(sys.argv[1:]))
    return 0
