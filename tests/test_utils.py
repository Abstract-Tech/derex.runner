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

    assert derex.runner.utils.abspath_from_egg("derex.runner", "derex/runner/utils.py")
    assert derex.runner.utils.abspath_from_egg(
        "derex.runner", "derex/runner/templates/docker-compose-project.yml.j2"
    )
