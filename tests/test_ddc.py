# -*- coding: utf-8 -*-
"""Tests for `derex.runner.ddc` module."""

from pathlib import Path

import logging
import os
import pytest
import sys
import yaml


MINIMAL_PROJ = Path(__file__).with_name("fixtures") / "minimal"
COMPLETE_PROJ = Path(__file__).with_name("fixtures") / "complete"


def test_ddc_services(sys_argv, capsys):
    """Test the derex docker compose shortcut."""
    from derex.runner.ddc import ddc_services

    os.environ["DEREX_ADMIN_SERVICES"] = "False"
    with sys_argv(["ddc-services", "config"]):
        ddc_services()
    output = capsys.readouterr().out
    assert "mongodb" in output
    assert "adminer" not in output

    os.environ["DEREX_ADMIN_SERVICES"] = "True"
    with sys_argv(["ddc-services", "config"]):
        ddc_services()
    output = capsys.readouterr().out
    assert "adminer" in output


def test_ddc_project(sys_argv, mocker, workdir_copy, capsys):
    """Test the open edx ironwood docker compose shortcut."""
    from derex.runner.ddc import ddc_project

    # It should check for services to be up before trying to do anything
    check_services = mocker.patch("derex.runner.ddc.check_services", return_value=False)

    for param in ["up", "start"]:
        with workdir_copy(MINIMAL_PROJ):
            with sys_argv(["ddc-project", param, "--dry-run"]):
                ddc_project()
        assert "ddc-services up -d" in capsys.readouterr().out

    check_services.return_value = True
    for param in ["up", "start"]:
        with workdir_copy(MINIMAL_PROJ):
            with sys_argv(["ddc-project", param, "--dry-run"]):
                ddc_project()
        assert "Would have run" in capsys.readouterr().out

    with workdir_copy(MINIMAL_PROJ):
        with sys_argv(["ddc-project", "config"]):
            ddc_project()
    assert "worker" in capsys.readouterr().out


def test_ddc_project_symlink_mounting(sys_argv, mocker, workdir_copy, capsys):
    """Make sure targets of symlinks in the requirements directory
    are mounted in the Open edX containers.
    """
    from derex.runner.ddc import ddc_project

    mocker.patch("derex.runner.ddc.check_services", return_value=True)
    with workdir_copy(COMPLETE_PROJ) as project_path:
        with sys_argv(["ddc-project", "config"]):
            ddc_project()
        config = yaml.load(capsys.readouterr().out)

        symlink_path = [
            el
            for el in (Path(project_path) / "requirements").iterdir()
            if el.is_symlink()
        ][0]
        symlink_target_path = symlink_path.resolve()

        volumes = config["services"]["lms"]["volumes"]
        # Make sure that the symlink target is mounted as a volume
        assert any(el.startswith(str(symlink_target_path)) for el in volumes)


@pytest.fixture(autouse=True)
def reset_root_logger():
    """The logging setup of docker-compose does not expect main() to be invoked
    more than once in the same interpreter lifetime.
    Also pytest replaces sys.stdout/sys.stderr before every test.
    To prevent this from causing errors (attempts to act on a closed file) we
    reset docker compose's `console_handler` before each test.
    """
    from compose.cli import main

    main.console_handler = logging.StreamHandler(sys.stderr)
