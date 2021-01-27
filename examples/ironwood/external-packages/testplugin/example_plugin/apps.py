from django.apps import AppConfig
from openedx.core.djangoapps.plugins.constants import PluginURLs
from openedx.core.djangoapps.plugins.constants import ProjectType


class ExampleConfig(AppConfig):
    name = u"example_plugin"
    plugin_app = {
        PluginURLs.CONFIG: {
            ProjectType.LMS: {
                PluginURLs.NAMESPACE: u"example_plugin",
                PluginURLs.REGEX: u"^",
                PluginURLs.RELATIVE_PATH: u"urls",
            }
        }
    }
