"""This file holds functions that generate docker-compose configuration
files from templates, interpolating variables according to the derex
project configuration.

They are invoked thanks to the `@hookimpl` call to the pluggy plugin system.

The functions have to be reachable under the common name `ddc_project_options`
so a class is put in place to hold each of them.
"""
from derex.runner import hookimpl
from derex.runner.docker import image_exists
from derex.runner.local_appdir import DEREX_DIR
from derex.runner.local_appdir import ensure_dir
from derex.runner.project import Project
from derex.runner.secrets import DerexSecrets
from derex.runner.secrets import get_secret
from derex.runner.utils import abspath_from_egg
from derex.runner.utils import asbool
from distutils import dir_util
from functools import partial
from jinja2 import Template
from pathlib import Path
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

import logging
import os


logger = logging.getLogger(__name__)

DEREX_ETC_PATH = Path("/etc/derex")
derex_path = partial(abspath_from_egg, "derex.runner")

WSGI_PY_PATH = derex_path("derex/runner/compose_files/wsgi.py")

DDC_SERVICES_YML_PATH = derex_path(
    "derex/runner/compose_files/docker-compose-services.yml"
)
DDC_ADMIN_PATH = derex_path("derex/runner/compose_files/docker-compose-admin.yml")
DDC_PROJECT_TEMPLATE_PATH = derex_path(
    "derex/runner/templates/docker-compose-project.yml.j2"
)
assert all(
    (WSGI_PY_PATH, DDC_SERVICES_YML_PATH, DDC_ADMIN_PATH, DDC_PROJECT_TEMPLATE_PATH,)
), "Some distribution files were not found"


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


class BaseOpenEdx:
    @staticmethod
    @hookimpl
    def ddc_project_options(project: Project,) -> Dict[str, Union[str, List[str]]]:
        """See derex.runner.plugin_spec.ddc_project_options docstring
        """
        local_path = generate_ddc_project_file(project)
        options = ["--project-name", project.name, "-f", str(local_path)]
        return {"options": options, "name": "base-openedx", "priority": "_begin"}


class LocalServices:
    @staticmethod
    @hookimpl
    def ddc_services_options() -> Optional[Dict[str, Union[str, List[str]]]]:
        """See derex.runner.plugin_spec.ddc_services_options docstring.
        """
        local_path = (
            Path(os.getenv("DEREX_ETC_PATH", DEREX_ETC_PATH))
            / "docker-compose-services.yml"
        )
        if not local_path.is_file():
            return None
        return {
            "options": ["-f", str(local_path)],
            "name": "local-services",
            "priority": "_end",
        }


class LocalOpenEdx:
    @staticmethod
    @hookimpl
    def ddc_project_options(
        project: Project,
    ) -> Optional[Dict[str, Union[str, List[str]]]]:
        """See derex.runner.plugin_spec.ddc_project_options docstring
        """
        if project.local_compose is None:
            return None
        return {
            "options": ["-f", str(project.local_compose)],
            "name": "local-openedx",
            "priority": "_end",
        }


class LocalRunmodeOpenEdx:
    @staticmethod
    @hookimpl
    def ddc_project_options(
        project: Project,
    ) -> Optional[Dict[str, Union[str, List[str]]]]:
        """See derex.runner.plugin_spec.ddc_project_options docstring
        """
        local_path = project.root / f"docker-compose-{project.runmode.value}.yml"
        if not local_path.is_file():
            return None
        options = ["-f", str(local_path)]
        return {"options": options, "name": "local-runmode-openedx", "priority": "_end"}


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
    tmpl = Template(template_path.read_text())
    text = tmpl.render(
        project=project, final_image=final_image, wsgi_py_path=WSGI_PY_PATH
    )
    project_compose_path.write_text(text)
    return project_compose_path


def generate_ddc_services_file() -> str:
    """Generate the global docker-compose config file that will drive
    ddc-services and return its path.
    """
    local_path = DEREX_DIR / "services" / DDC_SERVICES_YML_PATH.name
    dir_util.copy_tree(
        str(DDC_SERVICES_YML_PATH.parent),
        str(local_path.parent),
        update=1,  # Do not copy files more than once
        verbose=1,
    )
    ensure_dir(local_path)
    tmpl = Template(DDC_SERVICES_YML_PATH.read_text())
    minio_secret_key = get_secret(DerexSecrets.minio)
    text = tmpl.render(MINIO_SECRET_KEY=minio_secret_key)
    local_path.write_text(text)
    return str(local_path)
