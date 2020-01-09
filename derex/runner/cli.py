# -*- coding: utf-8 -*-

"""Console script for derex.runner."""
from functools import wraps

import click
import logging
import os


logger = logging.getLogger(__name__)


@click.group()
@click.pass_context
def derex(ctx):
    """Derex directs edX: commands to manage an Open edX installation
    """
    # Optimize --help and bash completion by importing
    from derex.runner.project import Project

    try:
        ctx.obj = Project()
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
    load_dump("fixtures/mailslurper.sql")
    return 0


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


@derex.command()
@click.pass_obj
@ensure_project
def compile_theme(project):
    """Compile theme sass files"""
    from derex.runner.compose_utils import run_compose

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
    run_compose(args, project=project)
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
        click.echo("Mysql service not found.\nMaybe you forgot to run\nddc-services up -d")
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


@derex.command()
@click.pass_obj
@ensure_project
def build_requirements(project):
    """Build the image that contains python requirements"""
    from derex.runner.build import build_requirements_image

    click.echo(
        f'Building docker image {project.requirements_image_tag} ("{project.name}" requirements)'
    )
    build_requirements_image(project)


@derex.command()
@click.pass_obj
@click.pass_context
@ensure_project
def build_themes(ctx, project):
    """Build the image that includes compiled themes"""
    from derex.runner.build import build_themes_image

    ctx.forward(build_requirements)
    click.echo(
        f'Building docker image {project.themes_image_tag} with "{project.name}" themes'
    )
    build_themes_image(project)
    click.echo(f"Built image {project.themes_image_tag}")


@derex.command()
@click.pass_obj
@click.pass_context
@ensure_project
def build_final(ctx, project):
    """Build the final image for this project.
    For now this is the same as the final image"""
    ctx.forward(build_themes)


@derex.command()
@click.pass_obj
@click.pass_context
@ensure_project
def build_final_refresh(ctx, project):
    """Also pull base docker image before starting building"""
    from derex.runner.docker import pull_images

    pull_images([project.base_image, project.final_base_image])
    ctx.forward(build_final)
