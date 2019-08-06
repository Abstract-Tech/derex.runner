# -*- coding: utf-8 -*-

"""Console script for derex.runner."""
import os
import sys
import pluggy
from typing import List, Tuple
from derex.runner.docker import execute_mysql_query
from derex.runner.docker import check_services
from derex.runner.docker import reset_mysql
from derex.runner.docker import wait_for_mysql
from derex.runner.docker import is_docker_working
from derex.runner.docker import load_dump
from derex.runner.docker import create_deps
from derex.runner.plugins import ConfigSpec
from derex.runner.config import BaseConfig
import logging
import click

from compose.cli.main import main


logger = logging.getLogger(__name__)


COMPOSE_EXTRA_OPTS: List[str] = []


def setup_logging():
    logging.basicConfig()
    for logger in ("urllib3.connectionpool", "compose", "docker"):
        logging.getLogger(logger).setLevel(logging.WARN)
    logging.getLogger("").setLevel(logging.INFO)


def setup_plugin_manager():
    plugin_manager = pluggy.PluginManager("derex.runner")
    plugin_manager.add_hookspecs(ConfigSpec)
    plugin_manager.load_setuptools_entrypoints("derex.runner")
    plugin_manager.register(BaseConfig())
    return plugin_manager


def run_compose(args: List[str], plugin: str = None, variant: str = "services"):
    create_deps()

    plugin_manager = setup_plugin_manager()
    config = plugin_manager.get_plugin(plugin)

    if config:
        # We use the specified configuration
        logging.info(f"Loaded settings from {config.__class__.__name__}")
        settings = config.settings()
    else:
        # We use the last loaded configuration
        settings = plugin_manager.hook.settings().pop(0)

    try:
        yaml_opts = settings[variant]()
    except Exception as e:
        logger.error("Can't load yaml options from settings")
        raise e

    old_argv = sys.argv
    try:
        sys.argv = ["docker-compose"] + yaml_opts + COMPOSE_EXTRA_OPTS + args
        logger.info(f"Running %s", " ".join(sys.argv))
        main()
    finally:
        sys.argv = old_argv


@click.command(context_settings=dict(ignore_unknown_options=True))
@click.argument("compose_args", nargs=-1)
@click.option(
    "--reset-mailslurper",
    default=False,
    is_flag=True,
    help="Resets mailslurper database",
)
@click.option(
    "--plugin", default=None, type=str, help="Plugin name to load configurations from"
)
def ddc(compose_args: Tuple[str, ...], plugin: str, reset_mailslurper: bool):
    """Derex docker-compose: run docker-compose with additional parameters.
    Adds docker compose file paths for services and administrative tools.
    If the environment variable DEREX_ADMIN_SERVICES is set to a falsey value,
    only the core ones will be started (mysql, mongodb etc).
    """
    check_docker()
    setup_logging()
    if reset_mailslurper:
        if not check_services(["mysql"]):
            print("Mysql not found.\nMaybe you forgot to run\nddc up -d")
            return 1
        resetmailslurper()
        return 0
    run_compose(list(compose_args), plugin=plugin)
    return 0


@click.command(context_settings=dict(ignore_unknown_options=True))
@click.argument("compose_args", nargs=-1)
@click.option(
    "--reset-mysql", default=False, is_flag=True, help="Resets the MySQL database"
)
@click.option(
    "--plugin", default=None, type=str, help="Plugin name to load configurations from"
)
def ddc_ironwood(compose_args: Tuple[str, ...], plugin: str, reset_mysql: bool):
    """Derex docker-compose running ironwood files: run docker-compose
    with additional parameters.
    Adds docker compose file paths for edx ironwood daemons.
    """
    check_docker()
    setup_logging()

    if (
        not check_services(["mysql", "mongodb", "rabbitmq"])
        and "down" not in compose_args
    ):
        print("Mysql/mongo/rabbitmq services not found.")
        print("Maybe you forgot to run")
        print("ddc up -d")
        return -1

    if reset_mysql:
        resetdb()
        return 0

    run_compose(list(compose_args), plugin, variant="openedx")
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
    load_dump("fixtures/mailslurper.sql")


def check_docker():
    if not is_docker_working():
        click.echo(click.style("Could not connect to docker.", fg="red"))
        click.echo(
            "Is it installed and running? Make sure the docker command works and try again."
        )
        sys.exit(1)
