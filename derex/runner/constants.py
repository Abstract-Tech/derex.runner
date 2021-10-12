from derex.runner.utils import derex_path
from enum import IntEnum
from pathlib import Path


DEREX_ETC_PATH = Path("/etc/derex")

WSGI_PY_PATH = derex_path("derex/runner/compose_files/wsgi.py")
DDC_SERVICES_YML_PATH = derex_path(
    "derex/runner/compose_files/docker-compose-services.yml"
)
DDC_ADMIN_PATH = derex_path("derex/runner/compose_files/docker-compose-admin.yml")
DDC_PROJECT_TEMPLATE_PATH = derex_path(
    "derex/runner/templates/docker-compose-project.yml.j2"
)
DDC_TEST_TEMPLATE_PATH = derex_path("derex/runner/templates/docker-compose-test.yml.j2")
MAILSLURPER_JSON_TEMPLATE = derex_path("derex/runner/compose_files/mailslurper.json.j2")
DEREX_DJANGO_PATH = derex_path("derex/django/__init__.py").parent
DEREX_DJANGO_SETTINGS_PATH = DEREX_DJANGO_PATH / "settings"

CONF_FILENAME = "derex.config.yaml"
SECRETS_CONF_FILENAME = "derex.secrets.yaml"

MYSQL_ROOT_USER = "root"
MONGODB_ROOT_USER = "root"

DEREX_TEMPLATES_DIR = derex_path("derex/runner/templates/README.rst").parent

assert all(
    (
        WSGI_PY_PATH,
        DDC_SERVICES_YML_PATH,
        DDC_ADMIN_PATH,
        DDC_PROJECT_TEMPLATE_PATH,
        DDC_TEST_TEMPLATE_PATH,
        MAILSLURPER_JSON_TEMPLATE,
        DEREX_DJANGO_PATH,
        DEREX_DJANGO_SETTINGS_PATH,
    )
), "Some distribution files were not found"


class ProjectBuildTargets(IntEnum):
    requirements = 1
    openedx_customizations = 2
    scripts = 3
    settings = 4
    translations = 5
    themes = 6
    final = 7
