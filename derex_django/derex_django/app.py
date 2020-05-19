from django.apps import AppConfig
from openedx.core.djangoapps.plugins.constants import PluginSettings
from openedx.core.djangoapps.plugins.constants import ProjectType
from openedx.core.djangoapps.plugins.constants import SettingsType


class DerexAppConfig(AppConfig):
    name = "derex_django"
    plugin_app = {
        PluginSettings.CONFIG: {
            ProjectType.LMS: {
                SettingsType.PRODUCTION: {PluginSettings.RELATIVE_PATH: "app"},
                SettingsType.AWS: {PluginSettings.RELATIVE_PATH: "app"},
                SettingsType.COMMON: {PluginSettings.RELATIVE_PATH: "app"},
                SettingsType.DEVSTACK: {PluginSettings.RELATIVE_PATH: "app"},
                SettingsType.TEST: {PluginSettings.RELATIVE_PATH: "app"},
            },
            ProjectType.CMS: {
                SettingsType.PRODUCTION: {PluginSettings.RELATIVE_PATH: "app"},
                SettingsType.AWS: {PluginSettings.RELATIVE_PATH: "app"},
                SettingsType.COMMON: {PluginSettings.RELATIVE_PATH: "app"},
                SettingsType.DEVSTACK: {PluginSettings.RELATIVE_PATH: "app"},
                SettingsType.TEST: {PluginSettings.RELATIVE_PATH: "app"},
            },
        },
    }


def plugin_settings(settings):
    pass
