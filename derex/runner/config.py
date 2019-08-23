import os
import pkg_resources
from derex.runner import hookimpl
from derex.runner.utils import asbool
from derex.runner.utils import compose_path
from derex.runner.utils import get_project_config
from derex.runner.utils import get_project_dir
from derex.runner.utils import get_requirements_tag
from derex.runner.utils import get_themes_tag
from jinja2 import Template
from pathlib import Path
from typing import List, Dict, Callable, Union
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


class BaseOpenEdX:
    @staticmethod
    @hookimpl
    def compose_options() -> Dict[str, Union[str, List[str]]]:
        """See derex.runner.plugin_spec.compose_options docstring
        """
        return {
            "options": [
                "--project-name",
                "derex_ironwood",
                "-f",
                compose_path("ironwood.yml"),
            ],
            "name": "base",
            "priority": "_begin",
            "variant": "openedx",
        }


class LocalOpenEdX:
    @staticmethod
    @hookimpl
    def local_compose_options(
        project_root: Union[Path, str]
    ) -> Dict[str, Union[str, List[str]]]:
        """See derex.runner.plugin_spec.compose_options docstring
        """
        local_path = generate_local_docker_compose(project_root)
        project_config = get_project_config()
        return {
            "options": [
                "--project-name",
                project_config["project_name"],
                "-f",
                str(local_path),
            ],
            "name": "base",
            "priority": "_begin",
            "variant": "local",
        }


def generate_local_docker_compose(project_root: Union[Path, str]) -> Path:
    project_root = Path(project_root)
    project_config = get_project_config()
    derex_dir = project_root / ".derex"
    if not derex_dir.is_dir():
        derex_dir.mkdir()
    local_compose_path = derex_dir / "docker-compose.yml"
    template_path = Path(
        pkg_resources.resource_filename(__name__, "templates/local.yml.j2")
    )
    tmpl = Template(template_path.read_text())
    themes_image = get_themes_tag(project_root)
    requirements_image = get_themes_tag(project_root)
    text = tmpl.render(
        themes_image=themes_image,
        project_name=project_config["project_name"],
        project_root=str(project_root),
        requirements_image=requirements_image,
    )
    local_compose_path.write_text(text)
    return local_compose_path
