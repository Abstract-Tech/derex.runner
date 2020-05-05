"""Utility functions for the derex commands.
"""
from functools import wraps

import click


def ensure_project(func):
    """Decorator that checks if the current command was invoked from inside a project,
    (i.e. if the click context has a project) and prints a nice message if it's not.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        if click.get_current_context().obj is None:
            click.echo("This command needs to be run inside a derex project")
            return 1
        func(*args, **kwargs)

    return wrapper
