from .utils import ensure_project
from .utils import red
from derex.runner.project import DebugBaseImageProject

import click


@click.group()
def translations():
    """Commands to manage translations"""


@translations.command()
@click.pass_obj
@ensure_project
def compile(project):
    """Compile project translations"""
    from derex.runner.ddc import run_ddc_project

    if not project.translations_dir:
        click.echo(
            red(f"No translations directory found at {project.translations_dir}"),
            err=True,
        )
        return 1

    click.echo("Compiling translations")
    # TODO: replace the command with a call to derex_update_translations script
    compose_args = [
        "run",
        "--rm",
        "lms",
        "sh",
        "-c",
        """set -ex
            python manage.py lms compilemessages
            python manage.py lms compilejsi18n
        """,
    ]
    run_ddc_project(compose_args, DebugBaseImageProject(), exit_afterwards=True)
