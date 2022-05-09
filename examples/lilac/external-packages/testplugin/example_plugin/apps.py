from django.apps import AppConfig
from openedx.core.djangoapps.plugins.constants import PluginURLs
from openedx.core.djangoapps.plugins.constants import ProjectType


class ExampleConfig(AppConfig):
    name = "example_plugin"
    plugin_app = {
        PluginURLs.CONFIG: {
            ProjectType.LMS: {
                PluginURLs.NAMESPACE: "example_plugin",
                PluginURLs.REGEX: "^",
                PluginURLs.RELATIVE_PATH: "urls",
            }
        }
    }
