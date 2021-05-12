from importlib import import_module

import os


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

# Load common settings for LMS and CMS
common_settings = import_module("{}.envs.common".format(SERVICE_VARIANT))
settings = [
    setting for setting in common_settings.__dict__ if not setting.startswith("_")
]
for setting in settings:
    globals().update({setting: getattr(common_settings, setting)})
