# -*- coding: utf-8 -*-
"""Console script for derex.runner."""
from .build import build
from .mongodb import mongodb
from .mysql import mysql
from .utils import ensure_project
from click_plugins import with_plugins
from derex.runner.logging_utils import setup_logging_decorator
from derex.runner.project import DebugBaseImageProject
from derex.runner.project import Project
from derex.runner.project import ProjectNotFound
from derex.runner.project import ProjectRunMode
from derex.runner.secrets import HAS_MASTER_SECRET
from rich import box
from rich.console import Console
from rich.table import Table
from typing import Any
from typing import Optional

import click
import importlib_metadata
import logging
import os
import sys


logger = logging.getLogger(__name__)


@with_plugins(importlib_metadata.entry_points().get("derex.runner.cli_plugins", []))
@click.group(invoke_without_command=True)
@click.version_option()
@click.pass_context
@setup_logging_decorator
def derex(ctx):
    """Derex directs edX: commands to manage an Open edX installation
    """
    # Optimize --help and bash completion by importing
    from derex.runner.project import Project

    try:
        ctx.obj = Project()
    except ProjectNotFound:
        pass
    except Exception as ex:
        logger.error("\n".join(map(str, ex.args)))
        sys.exit(1)

    if ctx.invoked_subcommand:
        return

    click.echo(derex.get_help(ctx) + "\n")

    from derex.runner.docker_utils import get_exposed_container_names

    container_names = get_exposed_container_names()
    if not container_names:
        return

    console = Console()
    table = Table(
        title="[bold green]These containers are running and exposing an HTTP server on port 80",
        box=box.SIMPLE,
    )
    table.add_column("Name")
    for container in container_names:
        container = (f"[bold]{container[0]}",) + container[1:]
        table.add_row(*container)
    console.print(table)


@derex.group()
@click.pass_context
def debug(ctx):
    """Debugging utilities
    """


@derex.command()
@click.pass_obj
def reset_mailslurper(project):
    """Reset the mailslurper database.
    """
    from derex.runner.mysql import drop_database
    from derex.runner.docker_utils import load_dump

    drop_database("mailslurper")
    click.echo("Priming mailslurper database")
    load_dump("derex/runner/fixtures/mailslurper.sql")
    return 0


@derex.command()
@click.pass_obj
@ensure_project
def compile_theme(project):
    """Compile theme sass files"""
    from derex.runner.ddc import run_ddc_project

    if project.themes_dir is None:
        click.echo("No theme directory present in this project")
        return
    themes = ",".join(el.name for el in project.themes_dir.iterdir())
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
    run_ddc_project(args, DebugBaseImageProject(), exit_afterwards=True)


@derex.command()
@click.pass_obj
@ensure_project
def create_bucket(project):
    """Create S3 buckets on Minio"""
    from derex.runner.docker_utils import run_minio_shell

    click.echo(f"Creating bucket {project.name} with dowload policy on /profile-images")
    command = f"mc mb --ignore-existing local/{project.name}; "
    command += f"mc policy set download local/{project.name}/profile-images"
    run_minio_shell(command)


@derex.command()
@click.pass_obj
@ensure_project
def reset_rabbitmq(project):
    """Create rabbitmq vhost"""
    from derex.runner.ddc import run_ddc_services

    vhost = f"{project.name}_edxqueue"
    args = [
        "exec",
        "-T",
        "rabbitmq",
        "sh",
        "-c",
        f"""rabbitmqctl add_vhost {vhost}
        rabbitmqctl set_permissions -p {vhost} guest ".*" ".*" ".*"
        """,
    ]
    run_ddc_services(args, exit_afterwards=True)
    click.echo(f"Rabbitmq vhost {vhost} created")
    return 0


@derex.command()
@click.argument(
    "runmode",
    type=click.Choice(ProjectRunMode.__members__),
    required=False,
    callback=lambda _, __, value: value and ProjectRunMode[value],
)
@click.option(
    "--force/-f",
    required=False,
    default=False,
    help="Allows switching to production mode without a main secret defined",
)
@click.pass_obj
@ensure_project
def runmode(project: Project, runmode: Optional[ProjectRunMode], force):
    """Get/set project runmode (debug/production)"""
    if runmode is None:
        click.echo(project.runmode.name)
    else:
        if project.runmode == runmode:
            click.echo(
                f"The current project runmode is already {runmode.name}", err=True
            )
            return
        if not force:
            if runmode is ProjectRunMode.production:
                if not HAS_MASTER_SECRET:
                    click.echo(
                        red("Set a master secret before switching to production"),
                        err=True,
                    )
                    sys.exit(1)
                    return 1
                    # We need https://github.com/Santandersecurityresearch/DrHeader/pull/102
                    # for the return 1 to work, but it's not released yet
        previous_runmode = project.runmode
        project.runmode = runmode
        click.echo(
            f"Switched runmode: {previous_runmode.name} → {runmode.name}", err=True
        )


def get_available_settings():
    """Return settings available on the current project"""
    try:
        project = Project()
    except ValueError:
        return None
    return project.get_available_settings().__members__


def materialise_settings(ctx, _, value):
    if value:
        return ctx.obj.get_available_settings()[value]
    return None


@derex.command()
@ensure_project
@click.argument(
    "settings",
    type=click.Choice(get_available_settings()),
    required=False,
    callback=materialise_settings,
)
@click.pass_obj
def settings(project: Project, settings: Optional[Any]):
    """Get/set project settings module to use (base.py/production.py)"""
    if settings is None:
        click.echo(project.settings.name)
    else:
        project.settings = settings


@debug.command()
def minio_shell():
    from derex.runner.docker_utils import run_minio_shell

    run_minio_shell()


@derex.command()
@click.option(
    "--old-key",
    # This is the key that the current default master secret generates
    default="ICDTE0ZnlbIR7r6/qE81nkF7Kshc2gXYv6fJR4I/HKPeTbxEeB3nxC85Ne6C844hEaaC2+KHBRIOzGou9leulZ7t",
    help="The old key to use for the update",
)
def update_minio(old_key: str):
    """Run minio to re-key data with the new secret. The output is very confusing, but it works.
    If you read a red warning and "Rotation complete" at the end, it means rekeying has worked.
    If your read your current SecretKey, it means the current credentials are correct and you don't need
    to update your keys.
    """
    from derex.runner.ddc import run_ddc_services

    # We need to stop minio after it's done re-keying. To this end, we use the expect package
    script = "apk add expect --no-cache "
    # We need to make sure the current credentials are not working...
    script += ' && expect -c "spawn /usr/bin/minio server /data; expect "Endpoint" { close; exit 1 }"'
    # ..but the old ones are
    script += f' && if MINIO_SECRET_KEY="{old_key}" expect -c \'spawn /usr/bin/minio server /data; expect "Endpoint" {{ close; exit 1 }}\'; then exit 1; fi'
    script += f' && export MINIO_ACCESS_KEY_OLD="$MINIO_ACCESS_KEY" MINIO_SECRET_KEY_OLD="{old_key}"'
    expected_string = "Rotation complete, please make sure to unset MINIO_ACCESS_KEY_OLD and MINIO_SECRET_KEY_OLD envs"
    script += f" && expect -c 'spawn /usr/bin/minio server /data; expect \"{expected_string}\" {{ close; exit 0 }}'"
    args = ["run", "--rm", "--entrypoint", "/bin/sh", "-T", "minio", "-c", script]
    run_ddc_services(args, exit_afterwards=False)
    click.echo("Minio server rekeying finished")


def red(string: str) -> str:
    return click.style(string, fg="red")


derex.add_command(mysql)
derex.add_command(mongodb)
derex.add_command(build)


__all__ = ["derex"]
