# -*- coding: utf-8 -*-

"""Console script for derex.runner."""
from click_plugins import with_plugins
from derex.runner import __version__
from derex.runner.logging_utils import setup_logging_decorator
from derex.runner.project import DebugBaseImageProject
from derex.runner.project import OpenEdXVersions
from derex.runner.project import Project
from derex.runner.project import ProjectRunMode
from derex.runner.utils import abspath_from_egg
from distutils.spawn import find_executable
from functools import wraps
from typing import Any
from typing import Optional

import click
import importlib_metadata
import logging
import os
import sys


logger = logging.getLogger(__name__)


def ensure_project(func):
    """Decorator that checks if the current command was invoked from inside a project,
    (i.e. if the click context has a project) and prints a nice message if it's not.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        if click.get_current_context().obj is None:
            click.echo("This command needs to be run inside a derex project")
            return 1
        func(*args, **kwargs)

    return wrapper


@with_plugins(importlib_metadata.entry_points().get("derex.runner.cli_plugins", []))
@click.group(invoke_without_command=True)
@click.pass_context
@setup_logging_decorator
def derex(ctx):
    """Derex directs edX: commands to manage an Open edX installation
    """
    # Optimize --help and bash completion by importing
    from derex.runner.project import Project

    try:
        ctx.obj = Project()
    except ValueError:
        pass

    if ctx.invoked_subcommand:
        return

    click.echo(derex.get_help(ctx))

    from .docker import get_exposed_container_names

    containers = "\n".join(get_exposed_container_names())
    click.echo(
        f"\nThese containers are running and exposing an HTTP server on port 80:\n\n{containers}"
    )


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
    from derex.runner.docker import check_services
    from derex.runner.docker import execute_mysql_query
    from derex.runner.docker import load_dump
    from derex.runner.docker import wait_for_mysql

    if not check_services(["mysql"]):
        click.echo("Mysql not found.\nMaybe you forgot to run\nddc-services up -d")
        return 1
    wait_for_mysql()
    click.echo("Dropping mailslurper database")
    execute_mysql_query("DROP DATABASE IF EXISTS mailslurper")
    click.echo("Priming mailslurper database")
    load_dump("derex/runner/fixtures/mailslurper.sql")
    return 0


@derex.command()
@click.pass_obj
@ensure_project
def compile_theme(project):
    """Compile theme sass files"""
    from derex.runner.compose_utils import run_compose

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
    run_compose(args, project=DebugBaseImageProject(), exit_afterwards=True)


@derex.command(name="reset-mysql")
@click.pass_obj
@ensure_project
@click.option(
    "--force",
    is_flag=True,
    default=False,
    help="Allow resetting mysql database if runmode is production",
)
def reset_mysql_cmd(project, force):
    """Reset mysql database for the project"""
    from derex.runner.compose_utils import reset_mysql
    from derex.runner.docker import check_services
    from derex.runner.docker import execute_mysql_query
    from derex.runner.docker import wait_for_mysql

    if project.runmode is not ProjectRunMode.debug and not force:
        # Safety belt: we don't want people to run this in production
        click.get_current_context().fail(
            "The command reset-mysql can only be run in `debug` runmode.\n"
            "Use --force to override"
        )

    if not check_services(["mysql"]):
        click.echo(
            "Mysql service not found.\nMaybe you forgot to run\nddc-services up -d"
        )
        return
    wait_for_mysql()
    execute_mysql_query(f"CREATE DATABASE IF NOT EXISTS {project.mysql_db_name}")
    reset_mysql(DebugBaseImageProject())
    return 0


@derex.command()
@click.pass_obj
@ensure_project
def create_bucket(project):
    """Create S3 buckets on Minio"""
    from derex.runner.docker import run_minio_mc

    click.echo(f"Creating bucket {project.name} with dowload policy on /profile-images")
    command = f"mc mb --ignore-existing local/{project.name}"
    command += f" && mc policy set download local/{project.name}/profile-images"
    run_minio_mc(command)


@derex.command()
@click.pass_obj
@ensure_project
def reset_rabbitmq(project):
    """Create rabbitmq vhost"""
    from derex.runner.compose_utils import run_compose

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
    run_compose(args, exit_afterwards=True)
    click.echo(f"Rabbitmq vhost {vhost} created")
    return 0


@derex.group()
def build():
    """Commands to build container images"""


@build.command()
@click.pass_obj
@ensure_project
def requirements(project):
    """Build the image that contains python requirements"""
    from derex.runner.build import build_requirements_image

    click.echo(
        f'Building docker image {project.requirements_image_name} ("{project.name}" requirements)'
    )
    build_requirements_image(project)


@build.command()
@click.pass_obj
@click.pass_context
@ensure_project
def themes(ctx, project: Project):
    """Build the image that includes compiled themes"""
    from derex.runner.build import build_themes_image

    ctx.forward(requirements)
    click.echo(
        f'Building docker image {project.themes_image_name} with "{project.name}" themes'
    )
    build_themes_image(project)
    click.echo(f"Built image {project.themes_image_name}")


@build.command()
@click.pass_obj
@click.pass_context
@ensure_project
def final(ctx, project: Project):
    """Build the final image for this project.
    For now this is the same as the final image"""
    ctx.forward(themes)


@build.command()
@click.pass_obj
@click.pass_context
@ensure_project
def final_refresh(ctx, project: Project):
    """Also pull base docker image before starting building"""
    from derex.runner.docker import pull_images

    pull_images([project.base_image, project.final_base_image])
    ctx.forward(final)


@build.command()
@click.argument(
    "version",
    type=click.Choice(OpenEdXVersions.__members__),
    required=True,
    callback=lambda _, __, value: value and OpenEdXVersions[value],
)
@click.option(
    "-t",
    "--target",
    type=click.Choice(
        [
            "dev",
            "nostatic-dev",
            "nostatic",
            "libgeos",
            "base",
            "sourceonly",
            "wheels",
            "translations",
            "nodump",
        ]
    ),
    default="dev",
    help="Target to build (nostatic, dev, translations)",
)
@click.option(
    "--push/--no-push", default=False, help="Also push image to registry after building"
)
@click.option(
    "--only-print-image-name/--do-build",
    default=False,
    help="Only print image name for the given target",
)
@click.option(
    "-d",
    "--docker-opts",
    envvar="DOCKER_OPTS",
    default="--output type=image,name={docker_image_prefix}-{target}{push_arg}",
    help=(
        "Additional options to pass to the docker invocation.\n"
        "By default outputs the image to the local docker daemon."
    ),
)
def openedx(version, target, push, only_print_image_name, docker_opts):
    """Build openedx image using docker. Defaults to dev image target."""
    dockerdir = abspath_from_egg("derex.runner", "docker-definition/Dockerfile").parent
    git_repo = version.value["git_repo"]
    git_branch = version.value["git_branch"]
    python_version = version.value.get("python_version", "3.6")
    docker_image_prefix = version.value["docker_image_prefix"]
    image_name = f"{docker_image_prefix}-{target}:{__version__}"
    if only_print_image_name:
        click.echo(image_name)
        return
    push_arg = ",push=true" if push else ""
    command = [
        "docker",
        "buildx",
        "build",
        str(dockerdir),
        "-t",
        image_name,
        "--build-arg",
        f"PYTHON_VERSION={python_version}",
        "--build-arg",
        f"EDX_PLATFORM_VERSION={git_branch}",
        "--build-arg",
        f"EDX_PLATFORM_REPOSITORY={git_repo}",
        f"--target={target}",
    ]
    transifex_path = os.path.expanduser("~/.transifexrc")
    if os.path.exists(transifex_path):
        command.extend(["--secret", f"id=transifex,src={transifex_path}"])
    if docker_opts:
        command.extend(docker_opts.format(**locals()).split())
    print("Invoking\n" + " ".join(command), file=sys.stderr)
    os.execve(find_executable(command[0]), command, os.environ)


@derex.command()
@click.argument(
    "runmode",
    type=click.Choice(ProjectRunMode.__members__),
    required=False,
    callback=lambda _, __, value: value and ProjectRunMode[value],
)
@click.pass_obj
@ensure_project
def runmode(project: Project, runmode: Optional[ProjectRunMode]):
    """Get/set project runmode (debug/production)"""
    if runmode is None:
        click.echo(project.runmode.name)
    else:
        if project.runmode == runmode:
            click.echo(
                f"The current project runmode is already {runmode.name}", err=True
            )
        else:
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
    from derex.runner.docker import run_minio_shell

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
    from derex.runner.compose_utils import run_compose

    # We need to stop minio after it's done re-keying. To this end, we use the expect package
    script = "apk add expect --no-cache "
    # We need to make sure the current credentials are not working...
    script += ' && expect -c "spawn /usr/bin/minio server /data; expect "Endpoint" { close; exit 1 }"'
    # ..but the old ones are
    script += f' && if MINIO_SECRET_KEY="{old_key}" expect -c \'spawn /usr/bin/minio server /data; expect "Endpoint" {{ close; exit 1 }}\'; then exit 0; fi'
    script += f' && export MINIO_ACCESS_KEY_OLD="$MINIO_ACCESS_KEY" MINIO_SECRET_KEY_OLD="{old_key}"'
    expected_string = "Rotation complete, please make sure to unset MINIO_ACCESS_KEY_OLD and MINIO_SECRET_KEY_OLD envs"
    script += f" && expect -c 'spawn /usr/bin/minio server /data; expect \"{expected_string}\" {{ close; exit 0 }}'"
    args = [
        "run",
        "--rm",
        "--entrypoint",
        "/bin/sh",
        "-T",
        "minio",
        "-c",
        script,
    ]
    run_compose(args, exit_afterwards=True)
    click.echo(f"Minio server rekeying finished")
