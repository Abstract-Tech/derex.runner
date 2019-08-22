# -*- coding: utf-8 -*-
from pathlib import Path
import contextlib
import os


MINIMAL_PROJ = Path(__file__).parent / "fixtures" / "minimal"


def test_project_config():
    """
    """
    from derex.runner.utils import project_config

    with working_directory(MINIMAL_PROJ):
        res = project_config()
    assert res["project_name"] == "minimal"


def test_project_dir():
    """
    """
    from derex.runner.utils import project_dir

    assert project_dir(MINIMAL_PROJ) == project_dir(MINIMAL_PROJ / "themes")


def test_asbool():
    """It's lifted from pyramid.settings, but testing it here won't harm.
    """
    from derex.runner.utils import asbool

    assert asbool(True) is True
    assert asbool("True") is True
    assert asbool("false") is False
    assert asbool(0) is False
    assert asbool("0") is False
    assert asbool(None) is False


@contextlib.contextmanager
def working_directory(path: Path):
    """Changes working directory and returns to previous on exit."""
    prev_cwd = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(prev_cwd)
