# -*- coding: utf-8 -*-
"""ddc (derex docker compose) wrappers.
These wrappers invoke `docker-compose` functions to get their job done.
They put a `docker.compose.yml` file in place based on user configuration.
"""
from derex.runner.compose_utils import run_docker_compose
from derex.runner.docker_utils import check_services
from derex.runner.docker_utils import ensure_volumes_present
from derex.runner.docker_utils import is_docker_working
from derex.runner.logging_utils import setup_logging
from derex.runner.plugins import get_sorted_plugins
from derex.runner.plugins import setup_plugin_manager
from derex.runner.project import DebugBaseImageProject
from derex.runner.project import Project
from tempfile import mkstemp
from typing import Any
from typing import List
from typing import Optional
from typing import Tuple

import click
import json
import os
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
    run_ddc_services(args, dry_run=dry_run, exit_afterwards=True)


def ddc_project():
    """Proxy for docker-compose: writes a docker-compose.yml file with the
    configuration of this project, and then run `docker-compose` on it.

    You probably want do run `ddc-project up -d` and `ddc-project logs -f`.
    """
    check_docker()
    setup_logging()
    try:
        project = Project()
    except ValueError as exc:
        click.echo(str(exc))
        sys.exit(1)
    compose_args, dry_run = ddc_parse_args(sys.argv)
    # If trying to start up containers, first check that needed services are running
    is_start_cmd = any(param in compose_args for param in ["up", "start"])
    if is_start_cmd and not check_services(["mysql", "mongodb", "rabbitmq"]):
        click.echo(
            "Mysql/mongo/rabbitmq services not found.\nMaybe you forgot to run\nddc-services up -d"
        )
        return
    run_ddc_project(list(compose_args), project, dry_run=dry_run, exit_afterwards=True)


def check_docker():
    if not is_docker_working():
        click.echo(click.style("Could not connect to docker.", fg="red"))
        click.echo(
            "Is it installed and running? Make sure the docker command works and try again."
        )
        sys.exit(1)


def run_ddc_services(
    argv: List[str], dry_run: bool = False, exit_afterwards: bool = False,
):
    """Run a docker-compose command relative to the system services.
    Plugin arguments are added to arguments passed in this function sorted by
    plugin priority.

    Used by ddc-services cli command.
    """
    ensure_volumes_present()
    plugins_argv = get_sorted_plugins(
        setup_plugin_manager().hook.ddc_services_options()
    )
    compose_argv = plugins_argv + argv
    run_docker_compose(compose_argv, dry_run, exit_afterwards)


def run_ddc_project(
    argv: List[str],
    project: Project,
    dry_run: bool = False,
    exit_afterwards: bool = False,
):
    """Run a docker-compose command relative to a project.
    Plugin arguments are added to arguments passed in this function sorted by
    plugin priority.

    Used by ddc-project cli command.
    """
    plugins_argv = get_sorted_plugins(
        setup_plugin_manager().hook.ddc_project_options(project=project),
    )
    compose_argv = plugins_argv + argv
    run_docker_compose(compose_argv, dry_run, exit_afterwards)


def run_django_script(
    project: Optional[Project], script_text: str, context: str = "lms"
) -> Any:
    """Run a script in a django shell, decode its stdout
    with JSON and return it.
    If the script does not output a parsable JSON None is returned.
    """
    script_fp, script_path = mkstemp(".py", "derex-run-script-")
    result_fp, result_path = mkstemp(".json", "derex-run-script-result")
    os.write(script_fp, script_text.encode("utf-8"))
    os.close(script_fp)
    args = [
        "run",
        "--rm",
        "-v",
        f"{result_path}:/result.json",
        "-v",
        f"{script_path}:/script.py",
        context,
        "sh",
        "-c",
        f"echo \"exec(open('/script.py').read())\" | ./manage.py {context} shell > /result.json",
    ]

    try:
        run_ddc_project(args, project=DebugBaseImageProject())
    finally:
        result_json = open(result_path).read()
        try:
            os.close(result_fp)
        except OSError:
            pass
        try:
            os.close(script_fp)
        except OSError:
            pass
        os.unlink(result_path)
        os.unlink(script_path)
    try:
        return json.loads(result_json)
    except json.decoder.JSONDecodeError:
        return None
