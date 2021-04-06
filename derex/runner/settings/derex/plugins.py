from edx_django_utils.plugins import constants as plugin_constants
from edx_django_utils.plugins import plugin_settings


PROJECT_TYPE = getattr(plugin_constants.ProjectType, SERVICE_VARIANT.upper())

# Adding plugins for AWS chokes if these are not defined
ENV_TOKENS = {}
AUTH_TOKENS = {}

# This is at the bottom because it is going to load more settings after base settings are loaded

if hasattr(plugin_constants.SettingsType, "AWS"):
    # Load aws.py in plugins for reverse compatibility.  This can be removed after aws.py
    # is officially removed.
    plugin_settings.add_plugins(
        __name__, PROJECT_TYPE, plugin_constants.SettingsType.AWS
    )

# We continue to load production.py over aws.py

plugin_settings.add_plugins(
    __name__, PROJECT_TYPE, plugin_constants.SettingsType.PRODUCTION
)
