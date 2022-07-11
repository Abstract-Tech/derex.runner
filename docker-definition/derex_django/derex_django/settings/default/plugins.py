from openedx.core.djangoapps.plugins import constants as plugin_constants


try:
    from openedx.core.djangoapps.plugins import plugin_settings
except ImportError:
    from edx_django_utils.plugins import plugin_settings


PROJECT_TYPE = getattr(plugin_constants.ProjectType, SERVICE_VARIANT.upper())

# Adding plugins for AWS chokes if these are not defined
ENV_TOKENS = {}
AUTH_TOKENS = {}

# This is at the bottom because it is going to load more settings after base settings are loaded
plugin_settings.add_plugins(
    __name__, PROJECT_TYPE, plugin_constants.SettingsType.COMMON
)
