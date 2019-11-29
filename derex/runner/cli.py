# -*- coding: utf-8 -*-

"""Console script for derex.runner."""
from derex.runner.docker import check_services
from derex.runner.docker import execute_mysql_query
from derex.runner.docker import load_dump
from derex.runner.docker import pull_images
from derex.runner.docker import wait_for_mysql

import click
import logging
import os


logger = logging.getLogger(__name__)


@click.group()
def derex():
    """Derex directs edX: commands to manage an Open edX installation
    """


@derex.command()
def reset_mailslurper():
    """Reset the mailslurper database.
    """
    if not check_services(["mysql"]):
        click.echo("Mysql not found.\nMaybe you forgot to run\nddc-services up -d")
        return 1
    wait_for_mysql()
    click.echo("Dropping mailslurper database")
    execute_mysql_query("DROP DATABASE IF EXISTS mailslurper")
    click.echo("Priming mailslurper database")
    load_dump("fixtures/mailslurper.sql")
    return 0


@derex.command()
def compile_theme():
    """Compile theme sass files"""
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


@derex.command()
def reset_mysql():
    """Reset mysql database for the project"""
    if not check_services(["mysql"]):
        click.echo("Mysql service not found.\nMaybe you forgot to run\nddc up -d")
        return
    resetdb(project, dry_run=dry_run)
    return 0


@derex.command()
def reset_rabbitmq():
    """Create rabbitmq vhost"""
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
    return 0


@derex.command()
def build_requirements():
    """Build the image that contains python requirements"""


@derex.command()
def build_themes():
    """Build the image that includes compiled themes"""


@derex.command()
def build_final():
    """Build the final image for this project"""


@derex.command()
def build_final_refresh():
    """Also pull base docker image before starting building"""
    pull_images([project.base_image, project.final_base_image])
