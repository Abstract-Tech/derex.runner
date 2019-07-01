# -*- coding: utf-8 -*-

"""Console script for derex.runner."""
import sys
from derex.runner.utils import run_compose
from derex.runner.utils import Variant
from derex.runner.docker import execute_mysql_query
from derex.runner.docker import check_services
from derex.runner.docker import reset_mysql
from derex.runner.docker import wait_for_mysql
from derex.runner.docker import is_docker_working
from derex.runner.docker import load_dump
import logging
import click


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
    check_docker()
    setup_logging()
    if len(sys.argv) > 1:
        if sys.argv[1] == "resetmailslurper":
            if not check_services(["mysql"]):
                print("Mysql not found.\nMaybe you forgot to run\nddc up -d")
                return 1
            resetmailslurper()
            return 0
    run_compose(list(sys.argv[1:]))
    return 0


def ddc_ironwood():
    """Derex docker-compose running ironwood files: run docker-compose
    with additional parameters.
    Adds docker compose file paths for edx ironwood daemons.
    """
    check_docker()
    setup_logging()
    if not check_services(["mysql", "mongodb", "rabbitmq"]):
        print("Mysql/mongo/rabbitmq services not found.")
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
    wait_for_mysql()
    execute_mysql_query("CREATE DATABASE IF NOT EXISTS derex")
    reset_mysql()


def resetmailslurper():
    wait_for_mysql()
    execute_mysql_query("DROP DATABASE IF EXISTS mailslurper")
    load_dump("compose_files/mailslurper.sql")


def check_docker():
    if not is_docker_working():
        click.echo(click.style("Could not connect to docker.", fg="red"))
        click.echo(
            "Is it installed and running? Make sure the docker command works and try again."
        )
        sys.exit(1)
