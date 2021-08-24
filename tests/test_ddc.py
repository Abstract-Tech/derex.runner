# -*- coding: utf-8 -*-
"""Tests for `derex.runner.ddc` module."""

from derex.runner.project import Project

import logging
import pytest
import sys
import yaml


def test_ddc_services(sys_argv, capsys, monkeypatch, complete_project):
    """Test the derex docker compose shortcut."""
    from derex.runner.ddc import ddc_services

    with complete_project:
        project = Project()
        with sys_argv(["ddc-services", "config"]):
            ddc_services()
        output = capsys.readouterr().out
        assert project.mongodb_host in output
        assert project.mysql_host in output
        assert project.elasticsearch_host in output

        monkeypatch.setenv("DEREX_ETC_PATH", str(Project().root / "derex_etc_dir"))
        with sys_argv(["ddc-services", "config"]):
            ddc_services()

        output = capsys.readouterr().out
        assert "my-overridden-secret-password" in output


def test_ddc_project_minimal(sys_argv, mocker, minimal_project, capsys):
    """Test the Open edX docker compose shortcut."""

    from derex.runner.ddc import ddc_project

    # It should check for services to be up before trying to do anything
    wait_for_container = mocker.patch("derex.runner.ddc.wait_for_container")

    with minimal_project:
        for param in ["up", "start"]:
            wait_for_container.return_value = 0
            wait_for_container.side_effect = None
            with sys_argv(["ddc-project", param, "--dry-run"]):
                ddc_project()
            assert "Would have run" in capsys.readouterr().out

            wait_for_container.side_effect = RuntimeError(
                "mysql service not found.\n"
                "Maybe you forgot to run\n"
                "ddc-services up -d"
            )
            with sys_argv(["ddc-project", param, "--dry-run"]):
                with pytest.raises(SystemExit):
                    ddc_project()
            assert "ddc-services up -d" in capsys.readouterr().out

        with sys_argv(["ddc-project", "config"]):
            ddc_project()
        assert "worker" in capsys.readouterr().out

        if Project().openedx_version.name == "juniper":
            with sys_argv(["ddc-project", "config"]):
                ddc_project()
            assert (
                "/derex/runner/compose_files/common/openedx_customizations/juniper/"
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

    mocker.patch("derex.runner.ddc.wait_for_container", return_value=0)
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
