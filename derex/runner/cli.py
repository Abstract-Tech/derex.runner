# -*- coding: utf-8 -*-

"""Console script for derex.runner."""
from derex.runner.build import build_requirements_image
from derex.runner.build import build_themes_image
from derex.runner.compose_utils import reset_mysql
from derex.runner.compose_utils import run_compose
from derex.runner.docker import check_services
from derex.runner.docker import execute_mysql_query
from derex.runner.docker import is_docker_working
from derex.runner.docker import load_dump
from derex.runner.docker import pull_images
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
    "--dry-run",
    default=False,
    is_flag=True,
    help="Don't actually do anything, just print what would have been run",
)
def ddc_local(compose_args: Tuple[str, ...], dry_run: bool):
    """Proxy for docker-compose: writes a docker-compose.yml file with the
    configuration of this project, and then run `docker-compose` on it.

    You probably want do run `ddc-local up -d` and `ddc-local logs -f`.

    Besides this, also accept these commands:\n
        * compile-theme (compile theme sass files)\n
        * reset-mysql (reset mysql database for the project)\n
        * build-requirements (build the image that contains python requirements)\n
        * build-themes (build the image that includes compiled themes)\n
        * build-final (build the final image for this project)\n
        * build-final-refresh (also pull base docker image before starting)\n
    """
    check_docker()
    setup_logging()
    try:
        project = Project()
    except ValueError:
        click.echo("You need to run this command in a derex project")
        sys.exit(1)
    BUILD_COMMANDS = [
        "build-requirements",
        "build-themes",
        "build-final",
        "build-final-refresh",
    ]
    COMMANDS = BUILD_COMMANDS + ["reset-mysql", "compile-theme"]
    command = ""
    if len(compose_args) == 1 and compose_args[0] in COMMANDS:
        command = compose_args[0]
    else:
        if not check_services(["mysql", "mongodb", "rabbitmq"]) and any(
            param in compose_args for param in ["up", "start"]
        ):
            click.echo(
                "Mysql/mongo/rabbitmq services not found.\nMaybe you forgot to run\nddc up -d"
            )
            return
        run_compose(list(compose_args), project=project, dry_run=dry_run)

    if command == "build-final-refresh":
        pull_images([project.base_image, project.final_base_image])
    if command in BUILD_COMMANDS:
        click.echo(
            f'Building docker image {project.requirements_image_tag} with "{project.name}" project requirements'
        )
        build_requirements_image(project)
    if command in ["build-themes", "build-final", "build-final-refresh"]:
        click.echo(
            f'Building docker image {project.themes_image_tag} with "{project.name}" themes'
        )
        build_themes_image(project)
    if command.startswith("build-"):
        click.echo(f"Built image {project.themes_image_tag}")
        return

    if command == "compile-theme":
        if project.themes_dir is None:
            click.echo("No theme directory present in this project")
            return
        themes = " ".join(el.name for el in project.themes_dir.iterdir())
        uid = os.getuid()
        args = [
            "run",
            "--rm",
            "lms",
            "sh",
            "-c",
            f"""set -ex
                paver compile_sass --theme-dirs /openedx/themes --themes {themes}
                chown {uid}:{uid} /openedx/themes/* -R""",
        ]
        run_compose(list(args), project=project, dry_run=dry_run)
        return

    if command == "reset-mysql":
        if not check_services(["mysql"]):
            click.echo("Mysql service not found.\nMaybe you forgot to run\nddc up -d")
            return
        resetdb(project)
        return


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
