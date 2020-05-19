from django.apps import AppConfig
from openedx.core.djangoapps.plugins.constants import PluginSettings
from openedx.core.djangoapps.plugins.constants import ProjectType
from openedx.core.djangoapps.plugins.constants import SettingsType


class DerexAppConfig(AppConfig):
    name = "derex_django"

    def ready(self):
        monkey_patch_course_default_image()

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


def monkey_patch_course_default_image():
    """When a user creates a new course they will by default get a broken image
    on vanilla Open edX.
    A comment in xmodule.course_module:CourseFields.course_image states this:
    # Ensure that courses imported from XML keep their image
    """
    from xmodule.course_module import CourseFields

    CourseFields.course_image._default = None
    CourseFields.banner_image._default = None
