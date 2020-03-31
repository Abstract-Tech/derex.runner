from derex.runner import hookimpl
from derex.runner.project import Project
from derex.runner.utils import abspath_from_egg
from derex.runner.utils import asbool
from functools import partial
from jinja2 import Template
from pathlib import Path
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

import docker
import logging
import os


logger = logging.getLogger(__name__)

d_r_path = partial(abspath_from_egg, "derex.runner")
WSGI_PY_PATH = d_r_path("derex/runner/compose_files/wsgi.py")
SERVICES_YML_PATH = d_r_path("derex/runner/compose_files/services.yml")
ADMIN_YML_PATH = d_r_path("derex/runner/compose_files/admin.yml")
LOCAL_YML_J2_PATH = d_r_path("derex/runner/templates/local.yml.j2")
assert all(
    (WSGI_PY_PATH, SERVICES_YML_PATH, ADMIN_YML_PATH, LOCAL_YML_J2_PATH)
), "Some distribution files were not found"


class BaseServices:
    @staticmethod
    @hookimpl
    def compose_options() -> Dict[str, Union[str, List[str]]]:
        """See derex.runner.plugin_spec.compose_options docstring.
        """
        options = ["--project-name", "derex_services", "-f", str(SERVICES_YML_PATH)]
        if asbool(os.environ.get("DEREX_ADMIN_SERVICES", True)):
            options += ["-f", str(ADMIN_YML_PATH)]
        return {
            "options": options,
            "name": "base",
            "priority": "_begin",
            "variant": "services",
        }


class LocalOpenEdX:
    @staticmethod
    @hookimpl
    def local_compose_options(project: Project) -> Dict[str, Union[str, List[str]]]:
        """See derex.runner.plugin_spec.compose_options docstring
        """
        local_path = generate_local_docker_compose(project)
        options = ["--project-name", project.name, "-f", str(local_path)]
        return {"options": options, "name": "local-derex", "priority": "_begin"}


class LocalUser:
    @staticmethod
    @hookimpl
    def local_compose_options(
        project: Project,
    ) -> Optional[Dict[str, Union[str, List[str]]]]:
        """See derex.runner.plugin_spec.compose_options docstring
        """
        if project.local_compose is None:
            return None
        return {
            "options": ["-f", str(project.local_compose)],
            "name": "local-user",
            "priority": "_end",
        }


class LocalRunmodeOpenEdX:
    @staticmethod
    @hookimpl
    def local_compose_options(
        project: Project,
    ) -> Optional[Dict[str, Union[str, List[str]]]]:
        """See derex.runner.plugin_spec.compose_options docstring
        """
        local_path = project.root / f"docker-compose-{project.runmode.value}.yml"
        if not local_path.is_file():
            return None
        options = ["-f", str(local_path)]
        return {"options": options, "name": "local-runmode", "priority": "_end"}


def generate_local_docker_compose(project: Project) -> Path:
    """This function is called every time ddc-project is run.
    It assembles a docker-compose file from the given configuration.
    It should execute as fast as possible.
    """
    local_compose_path = project.private_filepath("docker-compose.yml")
    template_path = LOCAL_YML_J2_PATH
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
    local_compose_path.write_text(text)
    return local_compose_path


def image_exists(needle: str) -> bool:
    """If the given image tag exist in the local docker repository, return True.
    """
    docker_client = docker.APIClient()
    images = docker_client.images()
    images.sort(key=lambda el: el["Created"], reverse=True)
    for image in images:
        if "RepoTags" not in image or not image["RepoTags"]:
            continue
        if needle in image["RepoTags"]:
            return True
    return False
