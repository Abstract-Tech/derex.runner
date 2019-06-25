#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `derex.runner.utils`."""


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
