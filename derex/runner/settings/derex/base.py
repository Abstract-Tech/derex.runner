# type: ignore
# flake8: noqa

from ..common import *
from openedx.core.lib.derived import derive_settings
from path import Path

import inspect
import os
import sys


SERVICE_VARIANT = os.environ["SERVICE_VARIANT"]
DEREX_PROJECT = os.environ.get("DEREX_PROJECT")

_settings_modules = [
    "mysql",
    "mongo",
    "django",
    "platform",
    "staticfiles",
    "media",
    "plugins",
    "xqueue",
    "celery",
    "email",
    "features",
    "external_services",
]

for setting_module in _settings_modules:
    setting_module_path = str(Path(__file__).parent / setting_module + ".py")
    if sys.version_info[0] < 3:
        # In python 2 we should use execfile
        execfile(setting_module_path), globals(), locals()  # noqa: F821
    else:  # python 3: use exec
        exec(open(setting_module_path).read())

from .container_env import *  # isort:skip

derive_settings(__name__)
