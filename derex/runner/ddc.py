# -*- coding: utf-8 -*-
"""ddc (derex docker compose) wrappers.
These wrappers invoke `docker-compose` functions to get their job done.
They put a `docker.compose.yml` file in place based on user configuration.
"""
from derex.runner.compose_utils import run_compose
from derex.runner.docker import check_services
from derex.runner.docker import is_docker_working
from derex.runner.logging import setup_logging
from derex.runner.project import Project
from typing import List
from typing import Tuple

import click
import sys


def ddc_parse_args(args: List[str]) -> Tuple[List[str], bool]:
    """Given a list of args, extract the ones to be passed to docker-compose
    (basically just omit the first one) and return the adjusted list.

    Also checks if the `--dry-run` flag is present, removes it from the
    list of args if it is and returns a 2-tuple like `(args, dry_run)`
    """
    dry_run = False
    if "--dry-run" in args:
        dry_run = True
        args = [el for el in args if el != "--dry-run"]
    return args[1:], dry_run


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
    args, dry_run = ddc_parse_args(sys.argv)
    run_compose(args, dry_run=dry_run)
    return 0


def ddc_project():
    """Proxy for docker-compose: writes a docker-compose.yml file with the
    configuration of this project, and then run `docker-compose` on it.

    You probably want do run `ddc-project up -d` and `ddc-project logs -f`.
    """
    check_docker()
    setup_logging()
    try:
        project = Project()
    except ValueError:
        click.echo("You need to run this command in a derex project")
        sys.exit(1)
    compose_args, dry_run = ddc_parse_args(sys.argv)
    # If trying to start up containers, first check that needed services are running
    is_start_cmd = any(param in compose_args for param in ["up", "start"])
    if is_start_cmd and not check_services(["mysql", "mongodb", "rabbitmq"]):
        click.echo(
            "Mysql/mongo/rabbitmq services not found.\nMaybe you forgot to run\nddc-services up -d"
        )
        return
    run_compose(list(compose_args), project=project, dry_run=dry_run)


def check_docker():
    if not is_docker_working():
        click.echo(click.style("Could not connect to docker.", fg="red"))
        click.echo(
            "Is it installed and running? Make sure the docker command works and try again."
        )
        sys.exit(1)
