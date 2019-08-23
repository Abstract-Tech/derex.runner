# -*- coding: utf-8 -*-
from pathlib import Path
import contextlib
import os


MINIMAL_PROJ = Path(__file__).parent / "fixtures" / "minimal"


def test_get_project_config():
    """
    """
    from derex.runner.utils import get_project_config

    with working_directory(MINIMAL_PROJ):
        res = get_project_config()
    assert res["project_name"] == "minimal"


def test_get_project_dir():
    """
    """
    from derex.runner.utils import get_project_dir

    assert get_project_dir(MINIMAL_PROJ) == get_project_dir(MINIMAL_PROJ / "themes")


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


def test_dirhash():
    from derex.runner.utils import dirhash

    def mypath(arg):
        return Path(__file__).parent / arg

    requirements_hash = dirhash(mypath("fixtures/minimal/requirements"))
    themes_hash = dirhash(mypath("fixtures/minimal/themes"))

    assert requirements_hash != themes_hash


@contextlib.contextmanager
def working_directory(path: Path):
    """Changes working directory and returns to previous on exit."""
    prev_cwd = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(prev_cwd)
