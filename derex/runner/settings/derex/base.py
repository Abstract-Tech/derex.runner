from openedx.core.lib.derived import derive_settings
from path import Path

import os
import sys


try:
    # This will fail if the project is overriding settings
    from ..common import *
except ImportError:
    from ...common import *

SERVICE_VARIANT = os.environ["SERVICE_VARIANT"]
DEREX_PROJECT = os.environ["DEREX_PROJECT"]

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
    "container_env",
    "plugins",
    "auth",
]

for setting_module in _settings_modules:
    setting_module_path = str(Path(__file__).parent / setting_module + ".py")
    # We are using execfile in order to share the current scope so that we
    # don't have to redefine and reimport everything in every single settings
    # module
    if sys.version_info[0] < 3:
        # In python 2 we should use execfile
        execfile(setting_module_path, globals(), locals())  # noqa: F821
    else:  # python 3: use exec
        exec(open(setting_module_path).read())

derive_settings(__name__)
