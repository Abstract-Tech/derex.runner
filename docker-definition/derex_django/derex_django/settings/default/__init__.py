from derex_django.constants import DEREX_OPENEDX_SUPPORTED_VERSIONS
from openedx.core.lib.derived import derive_settings
from path import Path

import os
import sys


try:
    SERVICE_VARIANT = os.environ["SERVICE_VARIANT"]
    assert SERVICE_VARIANT in ["lms", "cms"]
except KeyError:
    raise RuntimeError(
        "SERVICE_VARIANT environment variable must be defined in order to use derex default settings"
    )
except AssertionError:
    raise RuntimeError(
        'SERVICE_VARIANT environment variable must be one of ["lms", "cms"]'
    )

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

if SERVICE_VARIANT == "lms":
    from lms.envs.common import *  # noqa: F401, F403
if SERVICE_VARIANT == "cms":
    from cms.envs.common import *  # noqa: F401, F403


_settings_modules = [
    "django_settings",
    "mysql",
    "mongo",
    "caches",
    "logging",
    "staticfiles",
    "storages",
    "celery",
    "email",
    "placeholders",
    "features",
    "openedx_platform",
    "search",
    "container_env",
    "plugins",
    "auth",
]

for setting_module in _settings_modules:
    setting_module_path = str(Path(__file__).parent / "{}.py".format(setting_module))
    # We are using execfile in order to share the current scope so that we
    # don't have to redefine and reimport everything in every single settings
    # module
    if sys.version_info[0] < 3:
        # In python 2 we should use execfile
        execfile(setting_module_path, globals(), locals())  # noqa: F821
    else:  # python 3: use exec
        exec(open(setting_module_path).read())

derive_settings(__name__)
