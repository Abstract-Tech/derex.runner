from derex.runner import derex_path
from enum import Enum
from pathlib import Path


DEREX_ETC_PATH = Path("/etc/derex")

WSGI_PY_PATH = derex_path("derex/runner/compose_files/common/wsgi.py")
DDC_SERVICES_DEVELOPMENT_ENVIRONMENT_TEMPLATE_PATH = derex_path(
    "derex/runner/compose_files/development/docker-compose-services.yml.j2"
)
DDC_SERVICES_PRODUCTION_ENVIRONMENT_TEMPLATE_PATH = derex_path(
    "derex/runner/compose_files/production/docker-compose-services.yml.j2"
)
DDC_ADMIN_PATH = derex_path(
    "derex/runner/compose_files/production/docker-compose-admin.yml.j2"
)
DDC_PROJECT_DEVELOPMENT_ENVIRONMENT_TEMPLATE_PATH = derex_path(
    "derex/runner/compose_files/development/docker-compose-project.yml.j2"
)
DDC_PROJECT_PRODUCTION_ENVIRONMENT_TEMPLATE_PATH = derex_path(
    "derex/runner/compose_files/production/docker-compose-project.yml.j2"
)
DDC_TEST_TEMPLATE_PATH = derex_path(
    "derex/runner/compose_files/common/docker-compose-test.yml.j2"
)

MAILSLURPER_CONFIG_TEMPLATE = derex_path(
    "derex/runner/compose_files/development/mailslurper.json.j2"
)

DEREX_DJANGO_PATH = derex_path("derex/django/__init__.py").parent
DEREX_DJANGO_SETTINGS_PATH = DEREX_DJANGO_PATH / "settings"

DEREX_OPENEDX_CUSTOMIZATIONS_PATH = derex_path(
    "derex/runner/compose_files/common/openedx_customizations/README.rst"
).parent

CADDY_DEVELOPMENT_HOST_CADDYFILE_TEMPLATE = derex_path(
    "derex/runner/compose_files/development/host_caddy/Caddyfile.j2"
)
CADDY_PRODUCTION_PROJECT_CADDYFILE_TEMPLATE = derex_path(
    "derex/runner/compose_files/production/project_caddy/Caddyfile.j2"
)
CADDY_PRODUCTION_HOST_CADDYFILE_TEMPLATE = derex_path(
    "derex/runner/compose_files/production/host_caddy/Caddyfile.j2"
)

CONF_FILENAME = "derex.config.yaml"
SECRETS_CONF_FILENAME = "derex.secrets.yaml"

MYSQL_ROOT_USER = "root"
MONGODB_ROOT_USER = "root"
MINIO_ROOT_USER = "minio_derex"

DEREX_MAIN_SECRET_DEFAULT_MAX_SIZE = 1024
DEREX_MAIN_SECRET_DEFAULT_MIN_SIZE = 8
DEREX_MAIN_SECRET_DEFAULT_MIN_ENTROPY = 128
DEREX_MAIN_SECRET_DEFAULT_PATH = "/etc/derex/main_secret"

assert all(
    (
        WSGI_PY_PATH,
        CADDY_DEVELOPMENT_HOST_CADDYFILE_TEMPLATE,
        CADDY_PRODUCTION_PROJECT_CADDYFILE_TEMPLATE,
        CADDY_PRODUCTION_HOST_CADDYFILE_TEMPLATE,
        DDC_SERVICES_DEVELOPMENT_ENVIRONMENT_TEMPLATE_PATH,
        DDC_SERVICES_PRODUCTION_ENVIRONMENT_TEMPLATE_PATH,
        DDC_ADMIN_PATH,
        DDC_PROJECT_DEVELOPMENT_ENVIRONMENT_TEMPLATE_PATH,
        DDC_PROJECT_PRODUCTION_ENVIRONMENT_TEMPLATE_PATH,
        DDC_TEST_TEMPLATE_PATH,
        MAILSLURPER_CONFIG_TEMPLATE,
        DEREX_DJANGO_PATH,
        DEREX_DJANGO_SETTINGS_PATH,
        DEREX_OPENEDX_CUSTOMIZATIONS_PATH,
    )
), "Some distribution files were not found"


class OpenEdXVersions(Enum):
    # Values will be passed as uppercased named arguments to the docker build
    # e.g. --build-arg EDX_PLATFORM_RELEASE=koa
    ironwood = {
        "edx_platform_repository": "https://github.com/edx/edx-platform.git",
        "edx_platform_version": "open-release/ironwood.master",
        "edx_platform_release": "ironwood",
        "docker_image_prefix": "derex/openedx-ironwood",
        "alpine_version": "alpine3.11",
        "python_version": "2.7",
        "pip_version": "20.3.4",
        # The latest node release does not work on ironwood
        # (node-sass version fails to compile)
        "node_version": "v10.22.1",
        "mysql_image": "mysql:5.6.36",
        "mongodb_image": "mongo:3.2.21",
        "elasticsearch_image": "elasticsearch:1.5.2",
    }
    juniper = {
        "edx_platform_repository": "https://github.com/edx/edx-platform.git",
        "edx_platform_version": "open-release/juniper.master",
        "edx_platform_release": "juniper",
        "docker_image_prefix": "derex/openedx-juniper",
        "alpine_version": "alpine3.11",
        "python_version": "3.6",
        "pip_version": "21.0.1",
        "node_version": "v12.19.0",
        "mysql_image": "mysql:5.6.36",
        "mongodb_image": "mongo:3.6.23",
        "elasticsearch_image": "elasticsearch:1.5.2",
    }
    koa = {
        "edx_platform_repository": "https://github.com/edx/edx-platform.git",
        # We set koa.3 since as today (20 may 2021) koa.master codebase is broken
        "edx_platform_version": "open-release/koa.3",
        "edx_platform_release": "koa",
        "docker_image_prefix": "derex/openedx-koa",
        # We are stuck on alpine3.12 since SciPy won't build
        # on gcc>=10 due to fortran incompatibility issues.
        # See more at https://gcc.gnu.org/gcc-10/porting_to.html
        "alpine_version": "alpine3.12",
        "python_version": "3.8",
        "pip_version": "21.0.1",
        "node_version": "v12.19.0",
        "mysql_image": "mysql:5.7.34",
        "mongodb_image": "mongo:3.6.23",
        "elasticsearch_image": "elasticsearch:1.5.2",
    }


class ProjectRunMode(Enum):
    debug = "debug"  # The first is the default
    production = "production"


class ProjectEnvironment(Enum):
    development = "development"  # The first is the default
    staging = "staging"
    production = "production"


class DerexSecrets(Enum):
    minio = "minio"
    mysql = "mysql"
    mongodb = "mongodb"
