from derex.runner import hookimpl
from derex.runner.build import build_requirements_image
from derex.runner.project import Project
from derex.runner.utils import asbool
from derex.runner.utils import compose_path
from jinja2 import Template
from pathlib import Path
from typing import Dict
from typing import List
from typing import Union

import click
import docker
import os
import pkg_resources


class BaseServices:
    @staticmethod
    @hookimpl
    def compose_options() -> Dict[str, Union[str, List[str]]]:
        """See derex.runner.plugin_spec.compose_options docstring.
        """
        options = [
            "--project-name",
            "derex_services",
            "-f",
            compose_path("services.yml"),
        ]
        if asbool(os.environ.get("DEREX_ADMIN_SERVICES", True)):
            options += ["-f", compose_path("admin.yml")]
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
        if project.local_compose is not None:
            options += ["-f", str(project.local_compose)]
        return {"options": options, "name": "base", "priority": "_begin"}


def generate_local_docker_compose(project: Project) -> Path:
    """This function is called every time ddc-project is run.
    It assembles a docker-compose file from the given configuration.
    It should execute as fast as possible.
    """
    local_compose_path = project.private_filepath("docker-compose.yml")
    template_path = Path(
        pkg_resources.resource_filename(__name__, "templates/local.yml.j2")
    )
    final_image = None
    if image_exists(project.image_tag):
        final_image = project.image_tag
    if not image_exists(project.requirements_image_tag):
        click.echo("Building requirements image")
        build_requirements_image(project)
    tmpl = Template(template_path.read_text())
    text = tmpl.render(project=project, final_image=final_image)
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
