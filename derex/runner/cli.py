# -*- coding: utf-8 -*-

"""Console script for derex.runner."""
from derex.runner.compose_utils import reset_mysql
from derex.runner.compose_utils import run_compose
from derex.runner.docker import build_image
from derex.runner.docker import check_services
from derex.runner.docker import execute_mysql_query
from derex.runner.docker import is_docker_working
from derex.runner.docker import load_dump
from derex.runner.docker import pull_image
from derex.runner.docker import wait_for_mysql
from derex.runner.project import Project
from pathlib import Path
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

import click
import docker
import logging
import os
import pluggy
import sys


logger = logging.getLogger(__name__)


def setup_logging():
    logging.basicConfig()
    for logger in ("urllib3.connectionpool", "compose", "docker"):
        logging.getLogger(logger).setLevel(logging.WARN)
    logging.getLogger("").setLevel(logging.INFO)


@click.command(context_settings=dict(ignore_unknown_options=True))
@click.argument("compose_args", nargs=-1)
@click.option(
    "--build",
    help=(
        "Build docker image for this project.\n"
        "Argument can be one in:\n"
        "* requirements\n(build the image that contains python requirements)\n"
        "* themes\n(build the image that includes compiled themes)\n"
        "* final\n(build the final image for this project)\n"
        "* final-refresh\n(also pull base docker image before starting)\n"
    ),
    type=click.Choice(["requirements", "themes", "final", "final-refresh"]),
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
    try:
        project = Project()
    except ValueError:
        click.echo("You need to run this command in a derex project")
        sys.exit(1)
    if build == "final-refresh":
        pull_image(project.base_image)
    if build in ["requirements", "themes", "final", "final-refresh"]:
        click.echo(f'Building docker image with "{project.name}" project requirements')
        build_requirements_image(project)
    if build in ["themes", "final", "final-refresh"]:
        click.echo(f'Building docker image with "{project.name}" themes')
        build_themes_image(project)
    if build:
        return

    if not check_services(["mysql", "mongodb", "rabbitmq"]) and any(
        param in compose_args for param in ["up", "start"]
    ):
        click.echo(
            "Mysql/mongo/rabbitmq services not found.\nMaybe you forgot to run\nddc up -d"
        )
        return

    if reset_mysql:
        if not check_services(["mysql"]):
            click.echo("Mysql service not found.\nMaybe you forgot to run\nddc up -d")
            return
        resetdb(project)
        return
    run_compose(list(compose_args), project=project, dry_run=dry_run)


def build_requirements_image(project: Project):
    """Build the docker image the includes project requirements for the given project.
    """
    dockerfile_contents = [f"FROM {project.base_image}"]

    paths_to_copy: List[str] = []
    if project.requirements_dir:
        paths_to_copy = [str(project.requirements_dir)]
        dockerfile_contents.extend(["COPY requirements /openedx/derex.requirements/"])
        for requirments_file in os.listdir(project.requirements_dir):
            if requirments_file.endswith(".txt"):
                dockerfile_contents.extend(
                    [
                        f"RUN pip install -r /openedx/derex.requirements/{requirments_file}"
                    ]
                )
    dockerfile_text = "\n".join(dockerfile_contents)
    build_image(dockerfile_text, paths_to_copy, tag=project.requirements_image_tag)


BUILD_ASSETS_SCRIPT = (
    "PATH=/openedx/edx-platform/node_modules/.bin:/openedx/bin:${PATH};"
    "/opt/derex/bin/prepare_assets.sh;"
)


def build_themes_image(project: Project):
    """Build the docker image the includes themes for the given project.
    Dev tools will be left in the image, so this will be a "fat" image, not the final one
    to be distributed/deployed.
    """
    dockerfile_contents = [f"FROM {project.requirements_image_tag}"]

    paths_to_copy: List[str] = []
    if project.themes_dir:
        paths_to_copy = [str(project.themes_dir)]
        dockerfile_contents.append(f"COPY themes/ /openedx/themes/")
        compile_command = f"/opt/derex/bin/compile_assets.sh {' '.join(theme.name for theme in project.themes_dir.iterdir())} && cleanup_assets.sh"
        dockerfile_contents.append(f"RUN sh -c '{compile_command}'")

    dockerfile_text = "\n".join(dockerfile_contents)
    build_image(dockerfile_text, paths_to_copy, tag=project.themes_image_tag)


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


def resetdb(project: Project):
    """Reset the mysql database of LMS/CMS
    """
    wait_for_mysql()
    execute_mysql_query(f"CREATE DATABASE IF NOT EXISTS {project.mysql_db_name}")
    reset_mysql(project)


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
