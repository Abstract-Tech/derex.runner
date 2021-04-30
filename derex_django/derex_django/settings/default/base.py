from importlib import import_module
from openedx.core.lib.derived import derive_settings
from path import Path

import os
import sys


SERVICE_VARIANT = os.environ["SERVICE_VARIANT"]
DEREX_PROJECT = os.environ["DEREX_PROJECT"]
DEREX_OPENEDX_VERSION = os.environ["DEREX_OPENEDX_VERSION"]

assert SERVICE_VARIANT in ["lms", "cms"]

# Load common settings for LMS and CMS
common_settings = import_module("{}.envs.common".format(SERVICE_VARIANT))
settings = [
    setting for setting in common_settings.__dict__ if not setting.startswith("_")
]
for setting in settings:
    globals().update({setting: getattr(common_settings, setting)})

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
