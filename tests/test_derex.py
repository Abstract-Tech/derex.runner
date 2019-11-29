# -*- coding: utf-8 -*-
"""Tests for `derex.runner.cli` module."""

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


@pytest.mark.slowtest
def test_derex_build(workdir, sys_argv):
    from derex.runner.cli import derex
    from derex.runner.ddc import ddc_project

    with workdir(COMPLETE_PROJ):
        result = runner.invoke(derex, ["compile-theme"])
        assert_result_ok(result)

        with sys_argv(["ddc-project", "config"]):
            ddc_project()
        assert Project().name in result.output
        assert os.path.isdir(Project().root / ".derex")


@pytest.mark.slowtest
def test_derex_reset_mysql(sys_argv, mocker, workdir):
    """Test the open edx ironwood docker compose shortcut."""
    from derex.runner.cli import derex
    from derex.runner.ddc import ddc_services

    mocker.patch("derex.runner.ddc.check_services", return_value=True)
    client = mocker.patch("derex.runner.docker.client")
    client.containers.get.return_value.exec_run.side_effect = [
        SimpleNamespace(exit_code=-1)
    ] + list(repeat(SimpleNamespace(exit_code=0), 10))

    with sys_argv(["ddc-services", "up", "-d"]):
        ddc_services()
    with workdir(MINIMAL_PROJ):
        result = runner.invoke(derex, ["reset-mysql"])
    assert_result_ok(result)
    assert result.exit_code == 0


def assert_result_ok(result):
    """Makes sure the click script exited on purpose, and not by accident
    because of an exception.
    """
    if not isinstance(result.exc_info[1], SystemExit):
        tb_info = "\n".join(traceback.format_tb(result.exc_info[2]))
        assert result.exit_code == 0, tb_info
