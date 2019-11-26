# -*- coding: utf-8 -*-
"""Tests for `derex.runner` package."""

from click.testing import CliRunner
from derex.runner.project import Project
from itertools import repeat
from pathlib import Path
from types import SimpleNamespace

import os
import pytest
import traceback


MINIMAL_PROJ = Path(__file__).with_name("fixtures") / "minimal"
COMPLETE_PROJ = Path(__file__).with_name("fixtures") / "complete"
runner = CliRunner()


def test_ddc_services(sys_argv):
    """Test the derex docker compose shortcut."""
    from derex.runner.ddc import ddc_services

    os.environ["DEREX_ADMIN_SERVICES"] = "False"
    result = runner.invoke(ddc_services, ["config"])
    assert_result_ok(result)
    assert "mongodb" in result.output
    assert "adminer" not in result.output

    os.environ["DEREX_ADMIN_SERVICES"] = "True"
    result = runner.invoke(ddc_services, ["config"])
    assert_result_ok(result)
    assert "adminer" in result.output


def test_ddc_project(sys_argv, mocker, workdir):
    """Test the open edx ironwood docker compose shortcut."""
    from derex.runner.ddc import ddc_project

    # It should check for services to be up before trying to do anything
    check_services = mocker.patch("derex.runner.ddc.check_services")

    check_services.return_value = False
    for param in ["up", "start"]:
        with workdir(MINIMAL_PROJ):
            result = runner.invoke(ddc_project, [param, "--dry-run"])
        assert_result_ok(result)
        assert "ddc up -d" in result.output

    check_services.return_value = True
    for param in ["up", "start"]:
        with workdir(MINIMAL_PROJ):
            result = runner.invoke(ddc_project, [param, "--dry-run"])
        assert_result_ok(result)
        assert "Would have run" in result.output

    with workdir(MINIMAL_PROJ):
        result = runner.invoke(ddc_project, ["config"])
    assert_result_ok(result)
    assert "worker" in result.output


@pytest.mark.slowtest
def test_ddc_project_reset_mysql(sys_argv, mocker, workdir):
    """Test the open edx ironwood docker compose shortcut."""
    from derex.runner.ddc import ddc_services
    from derex.runner.ddc import ddc_project

    mocker.patch("derex.runner.ddc.check_services", return_value=True)
    client = mocker.patch("derex.runner.docker.client")
    client.containers.get.return_value.exec_run.side_effect = [
        SimpleNamespace(exit_code=-1)
    ] + list(repeat(SimpleNamespace(exit_code=0), 10))

    with workdir(MINIMAL_PROJ):
        result = runner.invoke(ddc_services, ["up", "-d"])
        result = runner.invoke(ddc_project, ["reset-mysql"])
    assert_result_ok(result)
    assert result.exit_code == 0


@pytest.mark.slowtest
def test_ddc_project_build(workdir):
    from derex.runner.ddc import ddc_project

    with workdir(COMPLETE_PROJ):
        result = runner.invoke(ddc_project, ["compile-theme"])
        assert_result_ok(result)

        result = runner.invoke(ddc_project, ["config"])
        assert_result_ok(result)
        assert Project().name in result.output
        assert os.path.isdir(Project().root / ".derex")


def assert_result_ok(result):
    """Makes sure the click script exited on purpose, and not by accident
    because of an exception.
    """
    if not isinstance(result.exc_info[1], SystemExit):
        tb_info = "\n".join(traceback.format_tb(result.exc_info[2]))
        assert result.exit_code == 0, tb_info
