import pkg_resources
import os
from compose.cli.main import main
from derex.runner.docker import create_deps
from typing import List
import sys
import logging
from enum import Enum


EXTRA_OPTS = ["--project-name", "derex"]


class Variant(Enum):
    services = "services"
    ironwood = "ironwood"


def run_compose(args: List[str], variant=Variant.services):
    create_deps()
    old_argv = sys.argv
    yaml_opts = YAML_OPTS[variant]()
    try:
        sys.argv = ["docker-compose"] + yaml_opts + EXTRA_OPTS + args
        logging.getLogger(__name__).info(f"Running %s", " ".join(sys.argv))
        main()
    finally:
        sys.argv = old_argv


def compose_path(name: str) -> str:
    """Given a docker compose file name return its path
    inside this package.
    """
    return pkg_resources.resource_filename(__name__, f"compose_files/{name}")


def yaml_opts_services() -> List[str]:
    """Return a list of strings pointing to docker-compose yml files suitable
    to be passed as options to docker-compose.
    The compose file includes services needed to run Open edX (mysql. mongodb etc)
    and (if not disabled) administrative tools.
    The list looks like:
    ['-f', '/path/to/docker-compose.yml', '-f', '/path/to/another-docker-compose.yml']
    """
    result = ["-f", compose_path("services.yml")]
    if asbool(os.environ.get("DEREX_ADMIN_SERVICES", True)):
        result += ["-f", compose_path("admin.yml")]
    return result


def yaml_opts_ironwood() -> List[str]:
    """Return a list of strings pointing to docker-compose yml files suitable
    to be passed as options to docker-compose.
    The compose file includes services needed to run Open edX (mysql. mongodb etc)
    and (if not disabled) administrative tools.
    The list looks like:
    ['-f', '/path/to/docker-compose.yml', '-f', '/path/to/another-docker-compose.yml']
    """
    return ["-f", compose_path("ironwood.yml")]


YAML_OPTS = {Variant.services: yaml_opts_services, Variant.ironwood: yaml_opts_ironwood}


truthy = frozenset(("t", "true", "y", "yes", "on", "1"))


def asbool(s):
    """ Return the boolean value ``True`` if the case-lowered value of string
    input ``s`` is a :term:`truthy string`. If ``s`` is already one of the
    boolean values ``True`` or ``False``, return it.
    Lifted from pyramid.settings.
    """
    if s is None:
        return False
    if isinstance(s, bool):
        return s
    s = str(s).strip()
    return s.lower() in truthy
