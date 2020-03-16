from compose.cli.main import main
from contextlib import contextmanager
from derex.runner.docker import ensure_volumes_present
from derex.runner.plugins import Registry
from derex.runner.plugins import setup_plugin_manager
from derex.runner.project import Project
from derex.runner.project import ProjectRunMode
from derex.runner.utils import abspath_from_egg
from typing import List
from typing import Optional

import click
import derex  # noqa  # This is ugly, but makes mypy and flake8 happy and still performs type checks
import logging
import sys


logger = logging.getLogger(__name__)


def run_compose(
    args: List[str],
    variant: str = "services",
    dry_run: bool = False,
    project: Optional["derex.runner.project.Project"] = None,
):
    """Run a docker-compose command passed in the `args` list.
    If `variant` is passed, load plugins for that variant.
    If a project is passed, load plugins for that project.
    """
    plugin_manager = setup_plugin_manager()
    registry = Registry()
    if project:
        for opts in plugin_manager.hook.local_compose_options(project=project):
            registry.add(
                key=opts["name"], value=opts["options"], location=opts["priority"]
            )
    else:
        ensure_volumes_present()
        for opts in plugin_manager.hook.compose_options():
            if opts["variant"] == variant:
                registry.add(
                    key=opts["name"], value=opts["options"], location=opts["priority"]
                )
    settings = [el for lst in registry for el in lst]
    old_argv = sys.argv
    try:
        sys.argv = ["docker-compose"] + settings + args
        if not dry_run:
            click.echo(f'Running {" ".join(sys.argv)}', err=True)
            with exit_cm():
                main()
        else:
            click.echo("Would have run:")
            click.echo(click.style(" ".join(sys.argv), fg="blue"))
    finally:
        sys.argv = old_argv


@contextmanager
def exit_cm():
    # Context manager to monkey patch sys.exit calls
    import sys

    def myexit(result_code):
        if result_code != 0:
            raise RuntimeError

    orig = sys.exit
    sys.exit = myexit

    try:
        yield
    finally:
        sys.exit = orig


def reset_mysql(project: Project, dry_run: bool = False):
    """Run script from derex/openedx image to reset the mysql db.
    """
    if project.runmode is not ProjectRunMode.debug:
        click.get_current_context().fail(
            "The command reset-mysql can only be run in `debug` runmode"
        )
    logger.warning("Resetting mysql database")

    restore_dump_path = abspath_from_egg(
        "derex.runner", "derex/runner/restore_dump.py.source"
    )
    assert (
        restore_dump_path
    ), "Could not find restore_dump.py in derex.runner distribution"
    run_compose(
        [
            "run",
            "--rm",
            "-v",
            f"{restore_dump_path}:/restore_dump.py",
            "lms",
            "python",
            "/restore_dump.py",
        ],
        project=project,
        dry_run=dry_run,
    )
