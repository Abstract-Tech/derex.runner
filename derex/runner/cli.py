# -*- coding: utf-8 -*-

"""Console script for derex.runner."""
from click_plugins import with_plugins
from derex.runner import __version__
from derex.runner.project import DebugProject
from derex.runner.project import OpenEdXVersions
from derex.runner.project import Project
from derex.runner.project import ProjectRunMode
from derex.runner.project import SettingsModified
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
@click.group()
@click.pass_context
def derex(ctx):
    """Derex directs edX: commands to manage an Open edX installation
    """
    # Optimize --help and bash completion by importing
    from derex.runner.project import Project

    # Set up a StreamHandler
    handler = logging.StreamHandler()
    handler.setLevel(logging.WARN)
    logging.getLogger("derex").addHandler(handler)

    try:
        ctx.obj = Project()
    except SettingsModified as error:
        print(
            f"Derex settings file modified:\n{error.filename}\nDelete or rename the file, and we'll put back the stock version"
        )
    except ValueError:
        pass


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
    run_compose(args, project=DebugProject())
    return


@derex.command(name="reset-mysql")
@click.pass_obj
@ensure_project
def reset_mysql_cmd(project):
    """Reset mysql database for the project"""
    from derex.runner.compose_utils import reset_mysql
    from derex.runner.docker import check_services
    from derex.runner.docker import execute_mysql_query
    from derex.runner.docker import wait_for_mysql

    if not check_services(["mysql"]):
        click.echo(
            "Mysql service not found.\nMaybe you forgot to run\nddc-services up -d"
        )
        return
    wait_for_mysql()
    execute_mysql_query(f"CREATE DATABASE IF NOT EXISTS {project.mysql_db_name}")
    reset_mysql(project)
    return 0


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
    run_compose(args)
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
        f'Building docker image {project.requirements_image_tag} ("{project.name}" requirements)'
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
        f'Building docker image {project.themes_image_tag} with "{project.name}" themes'
    )
    build_themes_image(project)
    click.echo(f"Built image {project.themes_image_tag}")


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
    type=click.Choice(["dev", "nostatic", "translations", "nodump"]),
    default="dev",
    help="Target to build (nostatic, dev, translations)",
)
@click.option(
    "--push/--no-push", default=False, help="Also push image to registry after building"
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
def openedx(version, target, push, docker_opts):
    """Build openedx image using docker. Defaults to dev image target."""
    dockerdir = abspath_from_egg("derex.runner", "docker-definition/Dockerfile").parent
    git_repo = version.value["git_repo"]
    git_branch = version.value["git_branch"]
    python_version = version.value.get("python_version", "3.6")
    docker_image_prefix = version.value["docker_image_prefix"]
    push_arg = ",push=true" if push else ""
    command = [
        "docker",
        "buildx",
        "build",
        str(dockerdir),
        "-t",
        f"{docker_image_prefix}-{target}:{__version__}",
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
    except (ValueError, SettingsModified):
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
