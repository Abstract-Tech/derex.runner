# -*- coding: utf-8 -*-

"""Console script for derex.runner."""
from pathlib import Path
import os
import sys
import logging
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
from derex.runner.utils import get_image_tag
from derex.runner.utils import get_project_base_image
from derex.runner.utils import get_project_config
from derex.runner.utils import get_project_dir
from derex.runner.utils import get_project_name
from derex.runner.utils import get_requirements_tag
from derex.runner.utils import get_themes_tag
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
    if variant == "local":
        try:
            project_dir = get_project_dir(os.getcwd())
        except ValueError:
            click.echo("You need to run this command in a derex project")
            sys.exit(1)
        for opts in plugin_manager.hook.local_compose_options(project_root=project_dir):
            if opts["variant"] == variant:
                registry.add(
                    key=opts["name"], value=opts["options"], location=opts["priority"]
                )
    else:
        for opts in plugin_manager.hook.compose_options():
            if opts["variant"] == variant:
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
@click.option(
    "--reset-mysql", default=False, is_flag=True, help="Resets the MySQL database"
)
@click.option(
    "--dry-run",
    default=False,
    is_flag=True,
    help="Don't actually do anything, just print what would have been run",
)
def ddc_local(compose_args: Tuple[str, ...], build: str, reset_mysql, dry_run: bool):
    check_docker()
    setup_logging()
    if build in ["requirements", "themes"]:
        click.echo(
            f'Building docker image with "{get_project_name()}" project requirements'
        )
        build_requirements_image(get_project_dir(os.getcwd()))
    if build == "themes":
        click.echo(f'Building docker image with "{get_project_name()}" themes')
        build_themes_image(get_project_dir(os.getcwd()))
    if build:
        return

    if not check_services(["mysql", "mongodb", "rabbitmq"]) and any(
        param in compose_args for param in ["up", "start"]
    ):
        click.echo("Mysql/mongo/rabbitmq services not found.")
        click.echo("Maybe you forgot to run")
        click.echo("ddc up -d")
        return

    if reset_mysql:
        resetdb()
        return
    run_compose(list(compose_args), variant="local", dry_run=dry_run)


def build_requirements_image(path: str):
    """Build the docker image the includes project requirements for the project
    specified by `path`.
    """
    dockerfile_contents = [f"FROM {get_project_base_image()}"]

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
    build_image(dockerfile_text, paths_to_copy, tag=get_requirements_tag(path))


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
    dockerfile_contents = [f"FROM {get_requirements_tag(path)}"]

    themes_path = os.path.join(path, "themes")
    paths_to_copy: List[str] = []
    if os.path.exists(themes_path):
        paths_to_copy = [themes_path]
        dockerfile_contents.extend(
            ["COPY themes /openedx/themes/", f"RUN sh -c '{BUILD_ASSETS_SCRIPT}'"]
        )
    dockerfile_text = "\n".join(dockerfile_contents)
    build_image(dockerfile_text, paths_to_copy, tag=get_themes_tag(path))


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


def resetdb(project_name="derex"):
    """Reset the mysql database of LMS/CMS
    """
    wait_for_mysql()
    execute_mysql_query(
        f"CREATE DATABASE IF NOT EXISTS {get_mysql_db_name(project_name)}"
    )
    reset_mysql()


def get_mysql_db_name(project_name):
    """Given a project name return a mysql database name
    """
    return project_name


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
