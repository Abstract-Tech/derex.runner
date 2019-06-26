# -*- coding: utf-8 -*-

"""Console script for derex.runner."""
import sys
from derex.runner.utils import run_compose
from derex.runner.utils import Variant
from derex.runner.docker import create_database
from derex.runner.docker import check_services
from derex.runner.docker import reset_mysql
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


def ddc_ironwood():
    """Derex docker-compose running ironwood files: run docker-compose
    with additional parameters.
    Adds docker compose file paths for edx ironwood daemons.
    """
    setup_logging()
    if not check_services():
        print("Mysql/mongo services not found.")
        print("Maybe you forgot to run")
        print("ddc up -d")
        return -1

    if len(sys.argv) > 1:
        if sys.argv[1] == "resetdb":
            resetdb()
            return 0
    run_compose(list(sys.argv[1:]), variant=Variant.ironwood)
    return 0


def resetdb():
    """Reset the mysql database of LMS/CMS
    """
    create_database("derex")
    reset_mysql()
