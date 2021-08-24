# -*- coding: utf-8 -*-

"""Package for derex.runner."""

__author__ = """Silvio Tomatis"""
__email__ = "silviot@gmail.com"
__version__ = "0.3.1"


from functools import partial
from pathlib import Path
from typing import Optional

import importlib_metadata
import pluggy


hookimpl = pluggy.HookimplMarker("derex.runner")
"""Marker to be imported and used in plugins (and for own implementations)"""


def abspath_from_egg(egg: str, path: str) -> Optional[Path]:
    """Given a path relative to the egg root, find the absolute
    filesystem path for that resource.
    For instance this file's absolute path can be found passing
    derex/runner/utils.py
    to this function.
    """
    for file in importlib_metadata.files(egg):
        if str(file) == path:
            return file.locate()
    return None


derex_path = partial(abspath_from_egg, "derex.runner")
