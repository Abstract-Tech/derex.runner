import pkg_resources
from compose.cli.main import main
from typing import List
import sys
from logging import getLogger


logger = getLogger(__name__)


def run_compose(args: List[str]):
    old_argv = sys.argv
    try:
        sys.argv = ["docker-compose"] + yaml_opts() + args
        logger.info(f"Running {' '.join(sys.argv)}")
        main()
    finally:
        sys.argv = old_argv


def yaml_opts() -> List[str]:
    """Return a list of strings pointing to docker-compose yml files suitable
    to be passed as options to docker-compose.
    The list looks like:
    ['-f', '/path/to/docker-compose.yml', '-f', '/path/to/another-docker-compose.yml']
    """
    return [
        "-f",
        pkg_resources.resource_filename(
            __name__, "templates/docker-compose-services.yml"
        ),
        "-f",
        pkg_resources.resource_filename(__name__, "templates/docker-compose-edx.yml"),
        "-f",
        pkg_resources.resource_filename(__name__, "templates/docker-compose-admin.yml"),
    ]


def start_service():
    run_compose(["ps"])
