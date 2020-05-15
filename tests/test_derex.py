# -*- coding: utf-8 -*-
"""Tests for `derex.runner.cli` module."""

from .conftest import assert_result_ok
from click.testing import CliRunner
from derex.runner.cli import derex as derex_cli_group
from derex.runner.ddc import ddc_services
from derex.runner.project import Project
from itertools import repeat
from pathlib import Path
from types import SimpleNamespace

import os
import pytest


MINIMAL_PROJ = Path(__file__).with_name("fixtures") / "minimal"
COMPLETE_PROJ = Path(__file__).with_name("fixtures") / "complete"
runner = CliRunner(mix_stderr=False)


@pytest.mark.slowtest
def test_derex_compile_theme(workdir_copy, sys_argv):
    with workdir_copy(COMPLETE_PROJ):
        result = runner.invoke(derex_cli_group, ["compile-theme"])
        assert_result_ok(result)
        assert os.path.isdir(Project().root / ".derex")


@pytest.mark.slowtest
def test_derex_reset_mysql(sys_argv, mocker, workdir_copy):
    """Test the open edx ironwood docker compose shortcut."""
    mocker.patch("derex.runner.ddc.check_services", return_value=True)
    client = mocker.patch("derex.runner.docker.client")
    client.containers.get.return_value.exec_run.side_effect = [
        SimpleNamespace(exit_code=-1)
    ] + list(repeat(SimpleNamespace(exit_code=0), 10))

    with sys_argv(["ddc-services", "up", "-d"]):
        ddc_services()
    with workdir_copy(MINIMAL_PROJ):
        result = runner.invoke(derex_cli_group, ["mysql", "reset"])
    assert_result_ok(result)
    assert result.exit_code == 0


def test_derex_runmode(testproj, mocker):
    with testproj:
        result = runner.invoke(derex_cli_group, ["runmode"])
        assert result.exit_code == 0, result.output
        assert result.output == "debug\n"
        # Until this PR is merged we can't peek into `.stderr`
        # https://github.com/pallets/click/pull/1194
        assert result.stderr_bytes == b""

        result = runner.invoke(derex_cli_group, ["runmode", "aaa"])
        assert result.exit_code == 2, result.output
        assert "Usage:" in result.stderr

        mocker.patch("derex.runner.cli.HAS_MASTER_SECRET", new=False)
        result = runner.invoke(derex_cli_group, ["runmode", "production"])
        assert result.exit_code == 1, result.output
        assert "Set a master secret" in result.stderr_bytes.decode("utf8")

        mocker.patch("derex.runner.cli.HAS_MASTER_SECRET", new=True)
        result = runner.invoke(derex_cli_group, ["runmode", "production"])
        assert result.exit_code == 0, result.output
        assert "debug → production" in result.stderr_bytes.decode("utf8")

        mocker.patch("derex.runner.cli.HAS_MASTER_SECRET", new=True)
        result = runner.invoke(derex_cli_group, ["runmode", "production"])
        assert result.exit_code == 0, result.output
        assert "already production" in result.stderr_bytes.decode("utf8")

        result = runner.invoke(derex_cli_group, ["runmode"])
        assert result.exit_code == 0, result.output
        assert result.output == "production\n"
        assert result.stderr_bytes == b""


def test_derex_runmode_wrong(testproj):
    with testproj:
        project = Project()
        # Use low level API to inject invalid value
        project._set_status("runmode", "garbage-not-a-valid-runmode")

        result = runner.invoke(derex_cli_group, "runmode")
        # Ensure presence of error message
        assert "garbage-not-a-valid-runmode" in result.stderr
        assert "valid as runmode" in result.stderr


def test_derex_cli_group_no_containers_running(monkeypatch):
    from derex.runner import docker

    # Run when no container is running
    monkeypatch.setattr(docker, "get_exposed_container_names", lambda: ())
    result = runner.invoke(derex_cli_group, catch_exceptions=False)
    assert (
        "These containers are running and exposing an HTTP server on port 80"
        not in result.output
    )


def test_derex_cli_group_one_container_running(monkeypatch):
    from derex.runner import docker

    # Test output when containers are running
    monkeypatch.setattr(
        docker,
        "get_exposed_container_names",
        lambda: (("http://projectone.localhost",),),
    )
    result = runner.invoke(derex_cli_group)
    assert (
        # Note the \n, necessary because rich laid out the text for us
        "These containers are running and \nexposing an HTTP server on port 80"
        in result.output
    )
