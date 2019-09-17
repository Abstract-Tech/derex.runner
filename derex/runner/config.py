from derex.runner import hookimpl
from derex.runner.project import Project
from derex.runner.utils import asbool
from derex.runner.utils import compose_path
from jinja2 import Template
from pathlib import Path
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

import docker
import os
import pkg_resources
import pluggy


class BaseServices:
    @staticmethod
    @hookimpl
    def compose_options() -> Dict[str, Union[str, List[str]]]:
        """See derex.runner.plugin_spec.compose_options docstring
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
        return {
            "options": ["--project-name", project.name, "-f", str(local_path)],
            "name": "base",
            "priority": "_begin",
        }


def generate_local_docker_compose(project: Project) -> Path:
    derex_dir = project.root / ".derex"
    if not derex_dir.is_dir():
        derex_dir.mkdir()
    local_compose_path = derex_dir / "docker-compose.yml"
    template_path = Path(
        pkg_resources.resource_filename(__name__, "templates/local.yml.j2")
    )
    final_image = get_final_image(project)
    tmpl = Template(template_path.read_text())
    text = tmpl.render(project=project, final_image=final_image)
    local_compose_path.write_text(text)
    return local_compose_path


def get_final_image(project: Project) -> Optional[str]:
    """If the final image for the project is available, return it.
    If not, return the most recent image available.
    """
    needle, _, _ = project.image_tag.rpartition(":")
    docker_client = docker.APIClient()
    images = docker_client.images()
    images.sort(key=lambda el: el["Created"], reverse=True)
    for image in images:
        for tag in image["RepoTags"]:
            if needle in tag:
                return tag
    return None
