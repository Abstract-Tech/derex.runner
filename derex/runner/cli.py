# -*- coding: utf-8 -*-

"""Console script for derex.runner."""
import click
import sys
from derex.runner.utils import run_compose


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


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
