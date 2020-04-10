from compose.cli.main import main
from contextlib import contextmanager
from derex.runner.docker import ensure_volumes_present
from derex.runner.plugins import Registry
from derex.runner.plugins import setup_plugin_manager
from derex.runner.project import DebugBaseImageProject
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
    exit_afterwards: bool = False,
):
    """Run a docker-compose command passed in the `args` list.
    If `variant` is passed, load plugins for that variant.
    If a project is passed, load plugins for that project.
    """
    old_argv = sys.argv
    try:
        sys.argv = get_compose_options(args=args, variant=variant, project=project)
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
        sys.argv = old_argv


def get_compose_options(
    args: List[str],
    variant: str = "services",
    project: Optional["derex.runner.project.Project"] = None,
):
    """Construct docker compose options in addition to the ones passed in `args`.
    For example, if `args` is ["run", "lms", "sh"] and a project is passed in,
    this function will return something like
    ["-f", "/path/to/project/.derex/docker-compose.yml", run", "lms", "sh"]

    It finds the options using a plugin manager, and sorts them by priority
    using a registry
    """
    plugin_manager = setup_plugin_manager()
    registry = Registry()
    if project:
        to_add = [
            (opts["name"], opts["options"], opts["priority"])
            for opts in plugin_manager.hook.local_compose_options(project=project)
        ]
        registry.add_list(to_add)
    else:
        ensure_volumes_present()
        to_add = [
            (opts["name"], opts["options"], opts["priority"])
            for opts in plugin_manager.hook.compose_options()
            if opts["variant"] == variant
        ]
        registry.add_list(to_add)
    settings = [el for lst in registry for el in lst]
    return ["docker-compose"] + settings + args


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
        run_compose(args, project=DebugBaseImageProject())
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
