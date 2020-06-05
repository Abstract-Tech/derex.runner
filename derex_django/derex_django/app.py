from django.apps import AppConfig
from openedx.core.djangoapps.plugins.constants import PluginSettings
from openedx.core.djangoapps.plugins.constants import ProjectType
from openedx.core.djangoapps.plugins.constants import SettingsType

import os


class DerexAppConfig(AppConfig):
    name = "derex_django"

    def ready(self):
        # monkey_patch_course_default_image()
        write_boto_config_file()

    plugin_app = {
        PluginSettings.CONFIG: {
            ProjectType.LMS: {
                SettingsType.COMMON: {PluginSettings.RELATIVE_PATH: "app"},
            },
            ProjectType.CMS: {
                SettingsType.COMMON: {PluginSettings.RELATIVE_PATH: "app"},
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


def write_boto_config_file():
    """Hack lifted from tutor-minio
    Configuring boto is required for ora2 because ora2 does not read
    host/port/ssl settings from django. Hence this hack.
    See http://docs.pythonboto.org/en/latest/boto_config_tut.html"""
    from django.conf import settings

    os.environ["AWS_CREDENTIAL_FILE"] = "/tmp/boto.cfg"
    with open("/tmp/boto.cfg", "w") as f:
        f.write(
            BOTO_CONFIG_TEMPLATE.format(
                host=settings.AWS_S3_HOST, is_secure=str(settings.AWS_S3_USE_SSL)
            )
        )


BOTO_CONFIG_TEMPLATE = """[Boto]
is_secure = {is_secure}
[s3]
host = {host}
calling_format = boto.s3.connection.OrdinaryCallingFormat"""
