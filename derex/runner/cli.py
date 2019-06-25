# -*- coding: utf-8 -*-

"""Console script for derex.runner."""
import click
import sys
from derex.runner.utils import run_compose
import logging


@click.command()
@click.argument("args", nargs=-1)
def main(args):
    """Run Open edX docker images."""
    if len(args) == 0:
        click.echo("Include arguments to pass to docker-compose")
        run_compose([])
        click.abort()
    run_compose(list(args))
    return 0


def setup_logging():
    logging.basicConfig()
    for logger in ("urllib3.connectionpool", "compose", "docker"):
        logging.getLogger(logger).setLevel(logging.WARN)
    logging.getLogger("").setLevel(logging.INFO)


def ddc():
    """Derex docker-compose: run docker-compose with additional parameters.
    Adds docker compose file paths for services and administrative tools.
    If the environment variable DEREX_ADMIN_SERVICES is set to a falsey value,
    only the core ones will be started (mysql, mongodb etc).
    """
    setup_logging()
    if len(sys.argv) == 1:
        click.echo("Include arguments to pass to docker-compose")
        run_compose([])
        click.abort()
    run_compose(list(sys.argv[1:]))
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
