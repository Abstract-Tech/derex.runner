#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `derex.runner` package."""

from click.testing import CliRunner

# from derex.runner import derex.runner
from derex.runner import cli

import pytest


@pytest.fixture
def response():
    """Sample pytest fixture.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    # import requests
    # return requests.get('https://github.com/veit/cookiecutter-namespace-template')


def test_content(response):
    """Sample pytest test function with the pytest fixture as an argument."""
    # from bs4 import BeautifulSoup
    # assert 'GitHub' in BeautifulSoup(response.content).title.string


def test_command_line_interface():
    """Test the CLI."""
    runner = CliRunner()
    result = runner.invoke(cli.main, ["ps"])
    assert result.exit_code == 0
    assert "lms_worker" in result.output
    help_result = runner.invoke(cli.main, ["--help"])
    assert help_result.exit_code == 0
    assert "Run Open edX docker images" in help_result.output
