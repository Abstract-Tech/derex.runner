# -*- coding: utf-8 -*-
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


def test_abspath_from_egg():
    import derex.runner.utils

    result = derex.runner.utils.abspath_from_egg("derex/runner/utils.py")
    assert str(result) == derex.runner.utils.__file__
