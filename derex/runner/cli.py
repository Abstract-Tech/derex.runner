# -*- coding: utf-8 -*-

"""Console script for derex.runner."""
from derex.runner.build import build_requirements_image
from derex.runner.build import build_themes_image
from derex.runner.compose_utils import reset_mysql
from derex.runner.compose_utils import run_compose
from derex.runner.config import generate_local_edxbackup_config
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
        * backup-dump (creates a backup)\n
        * backup-restore (restore an existing backup)\n
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

    if compose_args and compose_args[0] == "backup-dump":
        backup_dump(project)
        return

    if compose_args and compose_args[0] == "backup-restore":
        backup_restore(project)
        return

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


def backup_dump(project: Project):
    """Run a backup for the project
    """
    if project.backups_dir is None:
        click.echo(f"Creating default backup dir at {project.root / 'backups'}")
        project.backups_dir = project.root / "backups"
        os.mkdir(project.root / "backups")
    if not check_services(["mysql"]):
        click.echo(
            "Mysql/mongo/rabbitmq services not found.\nMaybe you forgot to run\nddc up -d"
        )
        return
    if not is_docker_working():
        click.echo("Unable to connect to docker daemon")
        return

    client = docker.from_env()
    config_file = generate_local_edxbackup_config(project, dump=True)
    try:
        click.echo(f"Creating database backup")
        output = client.containers.run(
            "derex/edxbackup",
            "edxbackup edx_dump",
            mounts=[
                docker.types.Mount(
                    type="bind", source=str(project.backups_dir), target="/destination"
                ),
                docker.types.Mount(
                    type="bind",
                    source=str(config_file),
                    target="/etc/edxbackup.json",
                    read_only=True,
                ),
            ],
            network="derex",
            remove=True,
        )
        click.echo(output.decode("utf-8"))
        click.echo(f"Successfully run backup for project {project.name}")
    except docker.errors.ContainerError as exc:
        click.echo(f"Unable to backup project {project.name}")
        logger.exception(exc)
    return


def backup_restore(project: Project):
    """List and restore project backups
    """

    if project.backups_dir is None:
        click.echo("No backup dir found")
        return
    if not check_services(["mysql"]):
        click.echo(
            "Mysql/mongo/rabbitmq services not found.\nMaybe you forgot to run\nddc up -d"
        )
        return
    if not is_docker_working():
        click.echo("Unable to connect to docker daemon")
        return

    available_backups = sorted(os.listdir(project.backups_dir))
    if not available_backups:
        click.echo(f"Unable to find any backup in {project.backups_dir}")
        return

    click.echo("Available backups:")
    for index, backup in enumerate(available_backups):
        click.echo(f"{index}\t{backup}")

    while True:
        backup_choice = click.prompt(
            "\nWhich backup do you want to load?\n"
            "Enter an empty value to load the last one. Enter CTRL+C to exit.",
            type=click.IntRange(min=0, max=len(available_backups) - 1),
            default=str(len(available_backups) - 1),
        )
        confirmation = click.confirm(
            text="Are you sure you want to load backup "
            f"{backup_choice} ({available_backups[backup_choice]}) ?",
            default=False,
        )
        if confirmation:
            chosen_backup = available_backups[int(backup_choice)]
            break
        return

    client = docker.from_env()
    backup_dir = project.backups_dir / chosen_backup
    config_file = generate_local_edxbackup_config(project)
    try:
        click.echo(f'Restoring database backup "{chosen_backup}"')
        output = client.containers.run(
            "derex/edxbackup",
            "edxbackup edx_restore",
            mounts=[
                docker.types.Mount(
                    type="bind",
                    source=str(backup_dir),
                    target="/destination",
                    read_only=True,
                ),
                docker.types.Mount(
                    type="bind",
                    source=str(config_file),
                    target="/etc/edxbackup.json",
                    read_only=True,
                ),
            ],
            network="derex",
            remove=True,
        )
        click.echo(output.decode("utf-8"))
        click.echo(f'Successfully restored backup "{chosen_backup}"')
    except docker.errors.ContainerError as exc:
        click.echo(f'Unable to restore backup "{chosen_backup}"')
        logger.exception(exc)
    return


def resetdb(project: Project, dry_run: bool):
    """Reset the mysql database of LMS/CMS
    """
    wait_for_mysql()
    if not dry_run:
        execute_mysql_query(f"CREATE DATABASE IF NOT EXISTS {project.mysql_db_name}")
    reset_mysql(project, dry_run=dry_run)


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
