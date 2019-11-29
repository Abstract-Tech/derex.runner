# -*- coding: utf-8 -*-
"""ddc (derex docker compose) wrappers.
These wrappers invoke `docker-compose` functions to get their job done.
They put a `docker.compose.yml` file in place based on user configuration.
"""
from derex.runner.build import build_requirements_image
from derex.runner.build import build_themes_image
from derex.runner.compose_utils import reset_mysql
from derex.runner.compose_utils import run_compose
from derex.runner.docker import check_services
from derex.runner.docker import execute_mysql_query
from derex.runner.docker import is_docker_working
from derex.runner.docker import pull_images
from derex.runner.docker import wait_for_mysql
from derex.runner.project import Project
from typing import Tuple

import click
import logging
import os
import sys


def ddc_services():
    """Derex docker-compose: run docker-compose with additional parameters.
    Adds docker compose file paths for services and administrative tools.
    If the environment variable DEREX_ADMIN_SERVICES is set to a falsey value,
    only the core ones will be started (mysql, mongodb etc) and the nice-to-have
    will not (portainer and adminer).

    Besides the regular docker-compose options it also accepts the --dry-run
    option; in case it's specified docker-compose will not be invoked, but
    a line will be printed showing what would have been invoked.
    """
    check_docker()
    setup_logging()
    args = sys.argv[1:]
    dry_run = False
    if "--dry-run" in args:
        dry_run = True
        args = [el for el in args if el != "--dry-run"]
    run_compose(args, dry_run=dry_run)
    return 0


@click.command(context_settings=dict(ignore_unknown_options=True))
@click.argument("compose_args", nargs=-1)
@click.option(
    "--dry-run",
    default=False,
    is_flag=True,
    help="Don't actually do anything, just print what would have been run",
)
def ddc_project(compose_args: Tuple[str, ...], dry_run: bool):
    """Proxy for docker-compose: writes a docker-compose.yml file with the
    configuration of this project, and then run `docker-compose` on it.

    You probably want do run `ddc-local up -d` and `ddc-local logs -f`.

    Besides this, also accept these commands:\n
        * compile-theme (compile theme sass files)\n
        * reset-mysql (reset mysql database for the project)\n
        * reset-rabbitmq (create rabbitmq vhost)\n
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
    COMMANDS = BUILD_COMMANDS + ["reset-mysql", "reset-rabbitmq", "compile-theme"]
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
                export PATH=/openedx/edx-platform/node_modules/.bin:$PATH  # FIXME: this should not be necessary
                paver compile_sass --theme-dirs /openedx/themes --themes {themes}
                chown {uid}:{uid} /openedx/themes/* -R""",
        ]
        run_compose(args, project=project, dry_run=dry_run)
        return

    if command == "reset-mysql":
        if not check_services(["mysql"]):
            click.echo("Mysql service not found.\nMaybe you forgot to run\nddc up -d")
            return
        resetdb(project, dry_run=dry_run)
        return

    if command == "reset-rabbitmq":
        vhost = f"{project.name}_edxqueue"
        args = [
            "exec",
            "rabbitmq",
            "sh",
            "-c",
            f"""rabbitmqctl add_vhost {vhost}
            rabbitmqctl set_permissions -p {vhost} guest ".*" ".*" ".*"
            """,
        ]
        run_compose(args, dry_run=dry_run)
        return


def setup_logging():
    logging.basicConfig()
    for logger in ("urllib3.connectionpool", "compose", "docker"):
        logging.getLogger(logger).setLevel(logging.WARN)
    logging.getLogger("").setLevel(logging.INFO)


def resetdb(project: Project, dry_run: bool):
    """Reset the mysql database of LMS/CMS
    """
    wait_for_mysql()
    if not dry_run:
        execute_mysql_query(f"CREATE DATABASE IF NOT EXISTS {project.mysql_db_name}")
    reset_mysql(project, dry_run=dry_run)


def check_docker():
    if not is_docker_working():
        click.echo(click.style("Could not connect to docker.", fg="red"))
        click.echo(
            "Is it installed and running? Make sure the docker command works and try again."
        )
        sys.exit(1)
