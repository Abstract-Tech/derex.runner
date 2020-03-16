from compose.cli.main import main
from contextlib import contextmanager
from derex.runner.docker import ensure_volumes_present
from derex.runner.plugins import Registry
from derex.runner.plugins import setup_plugin_manager
from derex.runner.project import DebugProject
from derex.runner.project import Project
from derex.runner.project import ProjectRunMode
from derex.runner.utils import abspath_from_egg
from tempfile import mkstemp
from typing import Any
from typing import List
from typing import Optional

import click
import derex  # noqa  # This is ugly, but makes mypy and flake8 happy and still performs type checks
import json
import logging
import os
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


def run_script(project, script_text: str, context: str = "lms") -> Any:
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
        run_compose(args, project=DebugProject())
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
