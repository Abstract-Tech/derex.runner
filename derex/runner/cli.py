# -*- coding: utf-8 -*-

"""Console script for derex.runner."""
import click
import sys


@click.command()
def main(args=None):
    """Console script for derex.runner."""
    click.echo(
        "Replace this message by putting your code into " "derex.runner.cli.main"
    )
    click.echo("See click documentation at http://click.pocoo.org/")
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
