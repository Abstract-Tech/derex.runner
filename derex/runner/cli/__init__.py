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
from derex.runner.utils import get_rich_console
from derex.runner.utils import get_rich_table
from typing import Any
from typing import Optional

import click
import importlib_metadata
import logging
import os
import rich
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

    console = get_rich_console()
    table = get_rich_table(
        "Name",
        title="[bold green]These containers are running and exposing an HTTP server on port 80",
        box=rich.box.SIMPLE,
    )
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
    compose_args = [
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
    run_ddc_project(compose_args, DebugBaseImageProject(), exit_afterwards=True)


@derex.command()
@click.pass_obj
@click.argument("course_ids", nargs=-1)
@ensure_project
def reindex_courses(project, course_ids):
    """Reindex all courses on elasticsearch.
    Course ids may be specified as arguemnts in order
    to reindex specific courses.

    e.g. `derex reindex_courses course-v1:edX+DemoX+Demo_Course`"""

    from derex.runner.ddc import run_ddc_project

    django_cmd = ["python", "manage.py", "cms", "reindex_course"]

    if course_ids:
        for course_id in course_ids:
            django_cmd.append(course_id)
    else:
        # Here we use the "--setup" option instead of "--all" to avoid
        # the confirmation prompt
        django_cmd.append("--setup")

    compose_args = ["run", "--rm", "cms", "sh", "-c", " ".join(django_cmd)]
    run_ddc_project(compose_args, DebugBaseImageProject(), exit_afterwards=True)


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
    compose_args = [
        "exec",
        "-T",
        "rabbitmq",
        "sh",
        "-c",
        f"""rabbitmqctl add_vhost {vhost}
        rabbitmqctl set_permissions -p {vhost} guest ".*" ".*" ".*"
        """,
    ]
    run_ddc_services(compose_args, exit_afterwards=True)
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


@debug.command("print-secret")
@click.argument(
    "secret", type=str, required=True,
)
def print_secret(secret):
    from derex.runner.secrets import get_secret, DerexSecrets

    derex_secret = getattr(DerexSecrets, secret, None)
    if not derex_secret:
        raise click.exceptions.ClickException(f'No secrets found for "{secret}"')
    click.echo(get_secret(derex_secret))
    return 0


@derex.command("minio-update-key")
@click.option(
    "--old-key",
    # This is the key that the current default master secret generates
    default="ICDTE0ZnlbIR7r6/qE81nkF7Kshc2gXYv6fJR4I/HKPeTbxEeB3nxC85Ne6C844hEaaC2+KHBRIOzGou9leulZ7t",
    help="The old key to use for the update",
)
def minio_update_key(old_key: str):
    """Run minio to re-key data with the new secret"""
    from derex.runner.ddc import run_ddc_services
    from derex.runner.docker_utils import check_services, wait_for_service
    from derex.runner.utils import derex_path

    MINIO_SCRIPT_PATH = derex_path("derex/runner/compose_files/minio-update-key.sh")

    if not check_services(["minio"]):
        click.echo(
            "MinIO service not found.\nMaybe you forgot to run\nddc-services up -d"
        )
        return 1

    click.echo("Updating MinIO secret key...")
    compose_args = [
        "run",
        "--rm",
        "-v",
        f"{MINIO_SCRIPT_PATH}:/minio-update-key.sh",
        "-e",
        f"MINIO_SECRET_KEY_OLD={old_key}",
        "--entrypoint",
        "/bin/sh",
        "-T",
        "minio",
        "/minio-update-key.sh",
    ]
    try:
        run_ddc_services(compose_args)
    except RuntimeError:
        return 1

    # We need to recreate the minio container since we can't set
    # the new key in the running one
    # https://github.com/moby/moby/issues/8838
    # We'll let `docker-compose up` recreate it for us, if needed
    click.echo("\nRecreating MinIO container...")
    compose_args = ["up", "-d", "minio"]
    run_ddc_services(compose_args)

    wait_for_service(
        "minio",
        'curl -i http://localhost:80/minio/health/live | grep -c "200 OK" && exit 0',
    )
    click.echo("\nMinIO secret key updated successfully!")
    return 0


def red(string: str) -> str:
    return click.style(string, fg="red")


derex.add_command(mysql)
derex.add_command(mongodb)
derex.add_command(build)


__all__ = ["derex"]
