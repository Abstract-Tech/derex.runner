"""This file holds functions that generate docker-compose configuration
files from templates, interpolating variables according to the derex
project configuration.

They are invoked thanks to the `@hookimpl` call to the pluggy plugin system.

The functions have to be reachable under the common name `ddc_project_options`
so a class is put in place to hold each of them.
"""
from derex.runner import hookimpl
from derex.runner.constants import DDC_ADMIN_PATH
from derex.runner.constants import DDC_PROJECT_TEMPLATE_PATH
from derex.runner.constants import DDC_SERVICES_YML_PATH
from derex.runner.constants import DEREX_DJANGO_PATH
from derex.runner.constants import DEREX_ETC_PATH
from derex.runner.constants import DEREX_OPENEDX_CUSTOMIZATIONS_PATH
from derex.runner.constants import MAILSLURPER_JSON_TEMPLATE
from derex.runner.constants import MONGODB_ROOT_USER
from derex.runner.constants import WSGI_PY_PATH
from derex.runner.docker_utils import image_exists
from derex.runner.local_appdir import DEREX_DIR
from derex.runner.local_appdir import ensure_dir
from derex.runner.project import Project
from derex.runner.secrets import DerexSecrets
from derex.runner.secrets import get_secret
from derex.runner.utils import asbool
from distutils import dir_util
from jinja2 import Template
from pathlib import Path
from typing import Dict
from typing import List
from typing import Union

import logging
import os


logger = logging.getLogger(__name__)


class BaseServices:
    @staticmethod
    @hookimpl
    def ddc_services_options() -> Dict[str, Union[str, List[str]]]:
        """See derex.runner.plugin_spec.ddc_services_options docstring.
        """
        options = [
            "--project-name",
            "derex_services",
            "-f",
            generate_ddc_services_file(),
        ]
        if asbool(os.environ.get("DEREX_ADMIN_SERVICES", True)):
            options += ["-f", str(DDC_ADMIN_PATH)]
        return {
            "options": options,
            "name": "base-services",
            "priority": "_begin",
        }


class BaseProject:
    @staticmethod
    @hookimpl
    def ddc_project_options(project: Project,) -> Dict[str, Union[str, List[str]]]:
        """See derex.runner.plugin_spec.ddc_project_options docstring
        """
        local_path = generate_ddc_project_file(project)
        options = ["--project-name", project.name, "-f", str(local_path)]
        return {"options": options, "name": "base-project", "priority": "_begin"}


class LocalServices:
    @staticmethod
    @hookimpl
    def ddc_services_options() -> Dict[str, Union[str, List[str]]]:
        """See derex.runner.plugin_spec.ddc_services_options docstring.
        """
        local_path = (
            Path(os.getenv("DEREX_ETC_PATH", DEREX_ETC_PATH))
            / "docker-compose-services.yml"
        )
        options: List[str] = []
        if local_path.is_file():
            options = ["-f", str(local_path)]
        return {
            "options": options,
            "name": "local-services",
            "priority": "_end",
        }


class LocalProject:
    @staticmethod
    @hookimpl
    def ddc_project_options(project: Project,) -> Dict[str, Union[str, List[str]]]:
        """See derex.runner.plugin_spec.ddc_project_options docstring
        """
        options: List[str] = []
        if project.local_compose:
            options = ["-f", str(project.local_compose)]
        return {
            "options": options,
            "name": "local-project",
            "priority": "_end",
        }


class LocalProjectRunmode:
    @staticmethod
    @hookimpl
    def ddc_project_options(project: Project,) -> Dict[str, Union[str, List[str]]]:
        """See derex.runner.plugin_spec.ddc_project_options docstring
        """
        local_path = project.root / f"docker-compose-{project.runmode.value}.yml"
        options: List[str] = []
        if local_path.is_file():
            options = ["-f", str(local_path)]
        return {"options": options, "name": "local-project-runmode", "priority": "_end"}


def generate_ddc_project_file(project: Project) -> Path:
    """This function is called every time ddc-project is run.
    It assembles a docker-compose file from the given configuration.
    It should execute as fast as possible.
    """
    project_compose_path = project.private_filepath("docker-compose.yml")
    template_path = DDC_PROJECT_TEMPLATE_PATH
    final_image = None
    if image_exists(project.image_name):
        final_image = project.image_name
    if not image_exists(project.requirements_image_name):
        logger.warning(
            f"Image {project.requirements_image_name} not found\n"
            "Run\nderex build requirements\n to build it"
        )

    openedx_customizations = []
    for openedx_customizations_dir in [
        DEREX_OPENEDX_CUSTOMIZATIONS_PATH / project.openedx_version.name,
        project.openedx_customizations_dir,
    ]:
        if openedx_customizations_dir and openedx_customizations_dir.exists():
            for python_file_path in openedx_customizations_dir.rglob("*.py"):
                openedx_customizations.append(
                    (
                        str(python_file_path),
                        str(python_file_path).replace(
                            str(openedx_customizations_dir), "/openedx/edx-platform"
                        ),
                    )
                )

    tmpl = Template(template_path.read_text())
    text = tmpl.render(
        project=project,
        final_image=final_image,
        wsgi_py_path=WSGI_PY_PATH,
        derex_django_path=DEREX_DJANGO_PATH,
        openedx_customizations=openedx_customizations,
    )
    project_compose_path.write_text(text)
    return project_compose_path


def generate_ddc_services_file() -> str:
    """Generate the global docker-compose config file that will drive
    ddc-services and return its path.
    """
    local_path = DEREX_DIR / "services" / DDC_SERVICES_YML_PATH.name
    # Copy all files
    dir_util.copy_tree(
        str(DDC_SERVICES_YML_PATH.parent),
        str(local_path.parent),
        update=1,  # Do not copy files more than once
        verbose=1,
    )
    # Compile the mailslurper template to include the mysql password
    tmpl = Template(MAILSLURPER_JSON_TEMPLATE.read_text())
    MYSQL_ROOT_PASSWORD = get_secret(DerexSecrets.mysql)
    text = tmpl.render(MYSQL_ROOT_PASSWORD=MYSQL_ROOT_PASSWORD)
    (local_path.parent / MAILSLURPER_JSON_TEMPLATE.name.replace(".j2", "")).write_text(
        text
    )

    # Compile the docker compose yaml template
    ensure_dir(local_path)
    tmpl = Template(DDC_SERVICES_YML_PATH.read_text())
    text = tmpl.render(
        MINIO_SECRET_KEY=get_secret(DerexSecrets.minio),
        MONGODB_ROOT_USERNAME=MONGODB_ROOT_USER,
        MONGODB_ROOT_PASSWORD=get_secret(DerexSecrets.mongodb),
        MYSQL_ROOT_PASSWORD=MYSQL_ROOT_PASSWORD,
    )
    local_path.write_text(text)
    return str(local_path)
