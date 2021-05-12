from derex_django.constants import DEREX_OPENEDX_SUPPORTED_VERSIONS

import os


try:
    DEREX_PROJECT = os.environ["DEREX_PROJECT"]
except KeyError:
    raise RuntimeError(
        "DEREX_PROJECT environment variable must be defined in order to use derex default settings"
    )

try:
    DEREX_OPENEDX_VERSION = os.environ["DEREX_OPENEDX_VERSION"]
    assert DEREX_OPENEDX_VERSION in DEREX_OPENEDX_SUPPORTED_VERSIONS
except KeyError:
    raise RuntimeError(
        "DEREX_OPENEDX_VERSION environment variable must be defined in order to use derex default settings"
    )
except AssertionError:
    raise RuntimeError(
        "DEREX_OPENEDX_VERSION must be on of {}".format(
            DEREX_OPENEDX_SUPPORTED_VERSIONS
        )
    )

from .base import *  # noqa: F401 # isort:skip
