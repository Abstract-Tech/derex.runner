# -*- coding: utf-8 -*-

"""Console script for derex.runner."""
from derex.runner.docker import check_services
from derex.runner.docker import execute_mysql_query
from derex.runner.docker import load_dump
from derex.runner.docker import wait_for_mysql

import click
import logging


logger = logging.getLogger(__name__)


@click.group()
def derex():
    """Derex directs edX.
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
