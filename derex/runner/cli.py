# -*- coding: utf-8 -*-

"""Console script for derex.runner."""
from pathlib import Path
import os
import sys
import pluggy
from typing import List, Tuple, Dict
import docker
from derex.runner.docker import build_image
from derex.runner.docker import check_services
from derex.runner.docker import create_deps
from derex.runner.docker import execute_mysql_query
from derex.runner.docker import is_docker_working
from derex.runner.docker import load_dump
from derex.runner.docker import reset_mysql
from derex.runner.docker import wait_for_mysql
from derex.runner.plugins import Registry
from derex.runner.plugins import setup_plugin_manager
from derex.runner.utils import project_dir
import logging
import click

from compose.cli.main import main


logger = logging.getLogger(__name__)


def setup_logging():
    logging.basicConfig()
    for logger in ("urllib3.connectionpool", "compose", "docker"):
        logging.getLogger(logger).setLevel(logging.WARN)
    logging.getLogger("").setLevel(logging.INFO)


def run_compose(args: List[str], variant: str = "services", dry_run: bool = False):
    create_deps()

    plugin_manager = setup_plugin_manager()
    registry = Registry()
    for opts in plugin_manager.hook.compose_options():
        if opts["variant"] == variant:
            logger.debug(f"Loading {opts['name']}")
            registry.add(
                key=opts["name"], value=opts["options"], location=opts["priority"]
            )
    settings = [el for lst in registry for el in lst]
    old_argv = sys.argv
    try:
        sys.argv = ["docker-compose"] + settings + args
        if not dry_run:
            click.echo(f'Running {" ".join(sys.argv)}')
            main()
        else:
            click.echo("Would have run")
            click.echo(click.style(" ".join(sys.argv), fg="blue"))
    finally:
        sys.argv = old_argv


@click.command(context_settings=dict(ignore_unknown_options=True))
@click.argument("compose_args", nargs=-1)
@click.option(
    "--build",
    help="build docker image for this project",
    type=click.Choice(["requirements", "themes"]),
    default=None,
)
def ddc_local(compose_args: Tuple[str, ...], build: str):
    if build in ["requirements", "themes"]:
        click.echo("Building docker image with project requirements")
        build_requirements_image(project_dir(os.getcwd()))
    if build == "themes":
        click.echo("Building docker image with themes")
        build_themes_image(project_dir(os.getcwd()))


def build_requirements_image(path: str):
    """Build the docker image the includes project requirements for the project
    specified by `path`.
    """
    dockerfile_contents = ["FROM derex/openedx-ironwood:latest"]

    requirements_path = os.path.join(path, "requirements")
    paths_to_copy: List[str] = []
    if os.path.exists(requirements_path):
        paths_to_copy = [requirements_path]
        dockerfile_contents.extend(["COPY requirements /tmp/requirements/"])
        for requirments_file in os.listdir(requirements_path):
            if requirments_file.endswith(".txt"):
                dockerfile_contents.extend(
                    [f"RUN pip install -r /tmp/requirements/{requirments_file}"]
                )
    dockerfile_text = "\n".join(dockerfile_contents)
    build_image(dockerfile_text, paths_to_copy)


BUILD_ASSETS_SCRIPT = (
    "PATH=/openedx/edx-platform/node_modules/.bin:/openedx/nodeenv/bin:/openedx/bin:${PATH};"
    "compile_assets.sh;"
    "cleanup_assets.sh;"
    "symlink_duplicates.py /openedx/staticfiles;"
)


def build_themes_image(path: str):
    """Build the docker image the includes project requirements for the project
    specified by `path`.
    """
    dockerfile_contents = ["FROM derex/openedx-ironwood:latest"]

    themes_path = os.path.join(path, "themes")
    paths_to_copy: List[str] = []
    if os.path.exists(themes_path):
        paths_to_copy = [themes_path]
        dockerfile_contents.extend(
            ["COPY themes /openedx/themes/", f"RUN sh -c '{BUILD_ASSETS_SCRIPT}'"]
        )
    dockerfile_text = "\n".join(dockerfile_contents)
    build_image(dockerfile_text, paths_to_copy)


@click.command(context_settings=dict(ignore_unknown_options=True))
@click.argument("compose_args", nargs=-1)
@click.option(
    "--reset-mailslurper",
    default=False,
    is_flag=True,
    help="Resets mailslurper database",
)
@click.option(
    "--dry-run",
    default=False,
    is_flag=True,
    help="Don't actually do anything, just print what would have been run",
)
def ddc(compose_args: Tuple[str, ...], reset_mailslurper: bool, dry_run: bool):
    """Derex docker-compose: run docker-compose with additional parameters.
    Adds docker compose file paths for services and administrative tools.
    If the environment variable DEREX_ADMIN_SERVICES is set to a falsey value,
    only the core ones will be started (mysql, mongodb etc).
    """
    check_docker()
    setup_logging()
    if reset_mailslurper:
        if not check_services(["mysql"]):
            click.echo("Mysql not found.\nMaybe you forgot to run\nddc up -d")
            return 1
        resetmailslurper()
        return 0
    run_compose(list(compose_args), dry_run=dry_run)
    return 0


@click.command(context_settings=dict(ignore_unknown_options=True))
@click.argument("compose_args", nargs=-1)
@click.option(
    "--reset-mysql", default=False, is_flag=True, help="Resets the MySQL database"
)
@click.option(
    "--dry-run",
    default=False,
    is_flag=True,
    help="Don't actually do anything, just print what would have been run",
)
def ddc_ironwood(compose_args: Tuple[str, ...], reset_mysql: bool, dry_run: bool):
    """Derex docker-compose running ironwood files: run docker-compose
    with additional parameters.
    Adds docker compose file paths for edx ironwood daemons.
    """
    check_docker()
    setup_logging()

    if not check_services(["mysql", "mongodb", "rabbitmq"]) and any(
        param in compose_args for param in ["up", "start"]
    ):
        click.echo("Mysql/mongo/rabbitmq services not found.")
        click.echo("Maybe you forgot to run")
        click.echo("ddc up -d")
        return -1

    if reset_mysql:
        resetdb()
        return 0

    run_compose(list(compose_args), variant="openedx", dry_run=dry_run)
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
