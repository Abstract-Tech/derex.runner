# -*- coding: utf-8 -*-
"""Tests for `derex.runner.ddc` module."""

import logging
import os
import pytest
import sys
import yaml


def test_ddc_services(sys_argv, capsys, monkeypatch, complete_project):
    """Test the derex docker compose shortcut."""
    from derex.runner.ddc import ddc_services
    from derex.runner.project import Project

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

    with complete_project:
        monkeypatch.setenv("DEREX_ETC_PATH", str(Project().root / "derex_etc_dir"))
        with sys_argv(["ddc-services", "config"]):
            ddc_services()

    output = capsys.readouterr().out
    assert "my-overridden-secret-password" in output


def test_ddc_project_minimal(sys_argv, mocker, minimal_project, capsys):
    from derex.runner.ddc import ddc_project
    from derex.runner.project import Project

    """Test the open edx ironwood docker compose shortcut."""
    # It should check for services to be up before trying to do anything
    check_services = mocker.patch("derex.runner.ddc.check_services", return_value=False)

    with minimal_project:
        for param in ["up", "start"]:
            check_services.return_value = False
            with sys_argv(["ddc-project", param, "--dry-run"]):
                ddc_project()
            assert "ddc-services up -d" in capsys.readouterr().out

            check_services.return_value = True
            with sys_argv(["ddc-project", param, "--dry-run"]):
                ddc_project()
            assert "Would have run" in capsys.readouterr().out

        with sys_argv(["ddc-project", "config"]):
            ddc_project()
        assert "worker" in capsys.readouterr().out

        if Project().openedx_version.name == "juniper":
            with sys_argv(["ddc-project", "config"]):
                ddc_project()
            assert (
                "/derex/runner/compose_files/openedx_customizations/juniper/"
                in capsys.readouterr().out
            )


def test_ddc_project_complete(sys_argv, complete_project, capsys):
    from derex.runner.ddc import ddc_project

    with complete_project:
        with sys_argv(["ddc-project", "config"]):
            ddc_project()
    assert (
        ":/openedx/edx-platform/test_openedx_customization.py"
        in capsys.readouterr().out
    )


def test_ddc_project_symlink_mounting(sys_argv, mocker, complete_project, capsys):
    """Make sure targets of symlinks in the requirements directory
    are mounted in the Open edX containers.
    """
    from derex.runner.ddc import ddc_project
    from derex.runner.project import Project

    mocker.patch("derex.runner.ddc.check_services", return_value=True)
    with complete_project:
        with sys_argv(["ddc-project", "config"]):
            ddc_project()
        config = yaml.load(capsys.readouterr().out, Loader=yaml.FullLoader)

        symlink_path = [
            el for el in (Project().root / "requirements").iterdir() if el.is_symlink()
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
