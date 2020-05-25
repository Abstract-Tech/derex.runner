from compose.cli.main import main
from contextlib import contextmanager
from typing import List

import click
import derex  # noqa  # This is ugly, but makes mypy and flake8 happy and still performs type checks
import logging
import sys


logger = logging.getLogger(__name__)


def run_docker_compose(
    compose_argv: List[str], dry_run: bool = False, exit_afterwards: bool = False
):
    """Run a docker-compose command with the specified arguments.
    """
    system_argv = sys.argv
    try:
        sys.argv = ["docker-compose"] + compose_argv
        if not dry_run:
            click.echo(f'Running\n{" ".join(sys.argv)}', err=True)
            if exit_afterwards:
                main()
            else:
                with exit_cm():
                    main()
        else:
            click.echo("Would have run:\n")
            click.echo(click.style(" ".join(sys.argv), fg="blue"))
    finally:
        sys.argv = system_argv


@contextmanager
def exit_cm():
    # Context manager to monkey patch sys.exit calls
    import sys

    def myexit(result_code=0):
        if result_code != 0:
            raise RuntimeError

    orig = sys.exit
    sys.exit = myexit

    try:
        yield
    finally:
        sys.exit = orig
