#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `derex.runner` package."""

from itertools import repeat
from types import SimpleNamespace
from click.testing import CliRunner
from pathlib import Path
import contextlib
import sys
import pytest
import os
from .fixtures import MINIMAL_PROJ, working_directory


runner = CliRunner()


def test_ddc(sys_argv):
    """Test the derex docker compose shortcut."""
    from derex.runner.cli import ddc

    os.environ["DEREX_ADMIN_SERVICES"] = "False"
    result = runner.invoke(ddc, ["config"])
    assert "mongodb" in result.output
    assert "adminer" not in result.output

    os.environ["DEREX_ADMIN_SERVICES"] = "True"
    result = runner.invoke(ddc, ["config"])
    assert "adminer" in result.output


def test_ddc_ironwood(sys_argv, mocker):
    """Test the open edx ironwood docker compose shortcut."""
    from derex.runner.cli import ddc_ironwood

    # It should check for services to be up before trying to do anything
    check_services = mocker.patch("derex.runner.cli.check_services")

    check_services.return_value = False
    for param in ["up", "start"]:
        result = runner.invoke(ddc_ironwood, [param, "--dry-run"])
        assert "ddc up -d" in result.output

    check_services.return_value = True
    for param in ["up", "start"]:
        result = runner.invoke(ddc_ironwood, [param, "--dry-run"])
        assert "Would have run" in result.output

    result = runner.invoke(ddc_ironwood, ["config"])
    assert "cms_worker" in result.output


def test_ddc_ironwood_reset_mysql(sys_argv, mocker):
    """Test the open edx ironwood docker compose shortcut."""
    from derex.runner.cli import ddc_ironwood

    mocker.patch("derex.runner.cli.check_services", return_value=True)
    client = mocker.patch("derex.runner.docker.client")
    client.containers.get.return_value.exec_run.side_effect = [
        SimpleNamespace(exit_code=-1)
    ] + list(repeat(SimpleNamespace(exit_code=0), 10))

    result = runner.invoke(ddc_ironwood, ["--reset-mysql"])
    assert result.exit_code == 0


def test_ddc_local():
    from derex.runner.cli import ddc_local

    with working_directory(MINIMAL_PROJ):
        output = runner.invoke(ddc_local, ["--build=themes", "--dry-run"])

    assert "Successfully built" in output.stdout
    assert "Successfully tagged" in output.stdout


@pytest.fixture
def sys_argv(mocker):
    @contextlib.contextmanager
    def my_cm(eargs):
        with mocker.mock_module.patch.object(sys, "argv", eargs):
            try:
                yield
            except SystemExit as exc:
                if exc.code != 0:
                    raise

    return my_cm
