# -*- coding: utf-8 -*-
from .fixtures import MINIMAL_PROJ, working_directory


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


def test_get_image_tag():
    from derex.runner.utils import get_image_tag

    with working_directory(MINIMAL_PROJ):
        requirements_image_tag = get_image_tag([MINIMAL_PROJ / "requirements"])
        themes_image_tag = get_image_tag([MINIMAL_PROJ / "themes"])

    assert requirements_image_tag != themes_image_tag
    assert len(requirements_image_tag) == len(themes_image_tag) == 22
