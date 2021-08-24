# -*- coding: utf-8 -*-
def test_asbool():
    """It's lifted from pyramid.settings, but testing it here won't harm."""
    from derex.runner.utils import asbool

    assert asbool(True) is True
    assert asbool("True") is True
    assert asbool("false") is False
    assert asbool(0) is False
    assert asbool("0") is False
    assert asbool(None) is False


def test_abspath_from_egg():
    from derex.runner import abspath_from_egg

    assert abspath_from_egg("derex.runner", "derex/runner/utils.py")
    assert abspath_from_egg("derex.runner", "derex/runner/__init__.py")
