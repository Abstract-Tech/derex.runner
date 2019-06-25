#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `derex.runner` package."""

from click.testing import CliRunner
import contextlib
import sys
import pytest
import io
import os
from contextlib import redirect_stdout


def test_ddc(sys_argv):
    """Test the derex docker compose shortcut."""
    from derex.runner.cli import ddc

    f = io.StringIO()
    os.environ["DEREX_ADMIN_SERVICES"] = "False"
    with redirect_stdout(f):
        with sys_argv(["_", "config"]):
            ddc()
    assert "mongodb" in f.getvalue()
    assert "adminer" not in f.getvalue()

    os.environ["DEREX_ADMIN_SERVICES"] = "True"
    with redirect_stdout(f):
        with sys_argv(["_", "config"]):
            ddc()
    assert "adminer" in f.getvalue()


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
