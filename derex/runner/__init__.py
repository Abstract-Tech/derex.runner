# -*- coding: utf-8 -*-

"""Package for derex.runner."""

__author__ = """Silvio Tomatis"""
__email__ = "silviot@gmail.com"
__version__ = "0.1.0"


import click_completion
import pluggy


click_completion.init()

hookimpl = pluggy.HookimplMarker("derex.runner")
"""Marker to be imported and used in plugins (and for own implementations)"""
