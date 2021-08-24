"""This file holds functions that generate docker-compose configuration
files from templates, interpolating variables according to the derex
project configuration.

They are invoked thanks to the `@hookimpl` call to the pluggy plugin system.

The functions have to be reachable under the common name `ddc_project_options`
so a class is put in place to hold each of them.
"""
from derex.runner import hookimpl
from derex.runner.constants import CADDY_DEVELOPMENT_HOST_CADDYFILE_TEMPLATE
from derex.runner.constants import CADDY_PRODUCTION_HOST_CADDYFILE_TEMPLATE
from derex.runner.constants import CADDY_PRODUCTION_PROJECT_CADDYFILE_TEMPLATE
from derex.runner.constants import DDC_PROJECT_DEVELOPMENT_ENVIRONMENT_TEMPLATE_PATH
from derex.runner.constants import DDC_PROJECT_PRODUCTION_ENVIRONMENT_TEMPLATE_PATH
from derex.runner.constants import DDC_SERVICES_DEVELOPMENT_ENVIRONMENT_TEMPLATE_PATH
from derex.runner.constants import DDC_SERVICES_PRODUCTION_ENVIRONMENT_TEMPLATE_PATH
from derex.runner.constants import DDC_TEST_TEMPLATE_PATH
from derex.runner.constants import DEREX_DJANGO_PATH
from derex.runner.constants import MAILSLURPER_CONFIG_TEMPLATE
from derex.runner.constants import ProjectEnvironment
from derex.runner.constants import WSGI_PY_PATH
from derex.runner.docker_utils import image_exists
from derex.runner.local_appdir import DEREX_DIR
from derex.runner.local_appdir import ensure_dir
from derex.runner.project import Project
from derex.runner.utils import asbool
from derex.runner.utils import compile_jinja_template
from pathlib import Path
from typing import Any
from typing import Dict
from typing import List
from typing import Union

import logging


logger = logging.getLogger(__name__)


class BaseServices:
    @staticmethod
    @hookimpl
    def ddc_services_options(project: Project) -> Dict[str, Union[str, List[str]]]:
        """See derex.runner.plugin_spec.ddc_services_options docstring."""
        if project.environment is ProjectEnvironment.development:
            project_name = "derex_services"
        else:
            project_name = project.name

        options = [
            "--project-name",
            project_name,
            "-f",
            str(generate_ddc_services_compose(project)),
        ]
        # Move this into a separate pluign
        # if asbool(os.environ.get("DEREX_ADMIN_SERVICES", True)):
        #     options += ["-f", str(DDC_ADMIN_PATH)]
        return {
            "options": options,
            "name": "base-services",
            "priority": "_begin",
        }


class BaseProject:
    @staticmethod
    @hookimpl
    def ddc_project_options(project: Project) -> Dict[str, Union[str, List[str]]]:
        """See derex.runner.plugin_spec.ddc_project_options docstring"""
        project_compose_path = generate_ddc_project_compose(project)
        options = ["--project-name", project.name, "-f", str(project_compose_path)]
        return {"options": options, "name": "base-project", "priority": "_begin"}


class LocalServices:
    @staticmethod
    @hookimpl
    def ddc_services_options(project: Project) -> Dict[str, Union[str, List[str]]]:
        """See derex.runner.plugin_spec.ddc_services_options docstring."""
        local_path = project.etc_path / "docker-compose-services.yml"
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
    def ddc_project_options(project: Project) -> Dict[str, Union[str, List[str]]]:
        """See derex.runner.plugin_spec.ddc_project_options docstring"""
        options: List[str] = []
        if project.local_compose:
            options = ["-f", str(project.local_compose)]
        return {
            "options": options,
            "name": "local-project",
            "priority": "_end",
        }


class LocalProjectEnvironment:
    @staticmethod
    @hookimpl
    def ddc_project_options(project: Project) -> Dict[str, Union[str, List[str]]]:
        """See derex.runner.plugin_spec.ddc_project_options docstring"""
        local_path = (
            project.root / f"docker-compose-env-{project.environment.value}.yml"
        )
        options: List[str] = []
        if local_path.is_file():
            options = ["-f", str(local_path)]
        return {
            "options": options,
            "name": "local-project-environment",
            "priority": "_end",
        }


class LocalProjectRunmode:
    @staticmethod
    @hookimpl
    def ddc_project_options(project: Project) -> Dict[str, Union[str, List[str]]]:
        """See derex.runner.plugin_spec.ddc_project_options docstring"""
        local_path = (
            project.root / f"docker-compose-runmode-{project.runmode.value}.yml"
        )
        options: List[str] = []
        if local_path.is_file():
            options = ["-f", str(local_path)]
        return {"options": options, "name": "local-project-runmode", "priority": "_end"}


def generate_ddc_project_compose(project: Project) -> Path:
    """This function is called every time ddc-project is run.
    It assembles a docker-compose file from the given configuration.
    It should execute as fast as possible.
    """
    if project.environment is ProjectEnvironment.development:
        template_path = DDC_PROJECT_DEVELOPMENT_ENVIRONMENT_TEMPLATE_PATH
    else:
        template_path = DDC_PROJECT_PRODUCTION_ENVIRONMENT_TEMPLATE_PATH

    final_image = None
    if image_exists(project.image_name):
        final_image = project.image_name
    if not image_exists(project.requirements_image_name):
        logger.warning(
            f"Image {project.requirements_image_name} not found\n"
            "Run\nderex build requirements\n to build it"
        )

    openedx_customizations = project.get_openedx_customizations()

    context = {
        "project": project,
        "final_image": final_image,
        "wsgi_py_path": WSGI_PY_PATH,
        "derex_django_path": DEREX_DJANGO_PATH,
        "openedx_customizations": openedx_customizations,
    }
    project_compose_path = compile_jinja_template(
        template_path,
        project.private_filepath("docker-compose.yml"),
        context=context,
    )

    if (
        not project.project_caddy_dir
        and project.environment is ProjectEnvironment.production
    ):
        project_caddy_config = generate_project_caddy_config(project)
        context.update({"project_caddy_dir": project_caddy_config.parent})
    else:
        context.update({"project_caddy_dir": project.project_caddy_dir})

    return project_compose_path


def generate_ddc_test_compose(project: Project) -> Path:
    """This function assembles a docker-compose with test services for
    the given project.
    It should execute as fast as possible.
    """
    test_compose_path = compile_jinja_template(
        DDC_TEST_TEMPLATE_PATH,
        project.private_filepath("docker-compose-test.yml"),
        context={"project": project},
    )
    return test_compose_path


def generate_ddc_services_compose(project: Project) -> Path:
    """Generate the global docker-compose config file that will drive
    ddc-services and return its path.
    """
    context: Dict[str, Any] = {}
    if project.environment is ProjectEnvironment.development:
        ddc_services_template_path = DDC_SERVICES_DEVELOPMENT_ENVIRONMENT_TEMPLATE_PATH
        # Mailslurper config file generation should be moved elsewhere,
        # ddc-services should not be responsible for it to be generated.
        # Probably a client interface like we are already doing
        # with `derex reset mailslurper`
        templates_paths = [MAILSLURPER_CONFIG_TEMPLATE, ddc_services_template_path]
    else:
        ddc_services_template_path = DDC_SERVICES_PRODUCTION_ENVIRONMENT_TEMPLATE_PATH
        templates_paths = [ddc_services_template_path]

    if asbool(project.enable_host_caddy):
        context.update({"enable_host_caddy": True})
        if not project.host_caddy_dir:
            host_caddy_config_path = generate_host_caddy_config(project)
            context.update(
                {
                    "host_caddy_dir": host_caddy_config_path.parent,
                    "host_caddy_config_path": host_caddy_config_path,
                }
            )
        else:
            context.update({"host_caddy_dir": project.host_caddy_dir})

    # Add the project object to the template context
    context.update({"project": project})
    local_path = DEREX_DIR / "compose_files"
    ensure_dir(local_path)
    for template_path in templates_paths:
        destination = local_path / template_path.name.replace(".j2", "")
        compile_jinja_template(template_path, destination, context=context)
    return destination


def generate_project_caddy_config(project: Project) -> Path:
    """Generate Caddyfile needed to serve the project through a Caddy HTTP server.
    In a development environment there is a single caddy server running on the host
    serving all projects.
    """
    if project.environment is ProjectEnvironment.development:
        raise RuntimeError(
            "In a development environment we don't need a project caddy server !"
        )
    else:
        # In a production environment configure an internal caddy server for every project.
        # This will be the only entry point to the project internal network.
        template_path = CADDY_PRODUCTION_PROJECT_CADDYFILE_TEMPLATE
        if project.project_caddy_dir:
            template_path = project.project_caddy_dir / "Caddyfile"
            if not template_path.exists():
                raise RuntimeError(
                    f"No caddyfile exists at {template_path}."
                    "Add one or delete {project.caddy_dir}."
                )
    context = {"project": project}
    destination = project.private_filepath("Caddyfile")
    ensure_dir(destination.parent)
    compile_jinja_template(template_path, destination, context=context)
    return destination


def generate_host_caddy_config(project: Project) -> Path:
    """Generate Caddyfile needed for the host Caddy HTTP server.
    In a development environment this will be Caddy server serving all projects
    and will route requests directly to docker containers.

    In a production environment this server will route
    requests to an internally facing Caddy server specific to every project.
    """
    if project.environment is ProjectEnvironment.development:
        template_path = CADDY_DEVELOPMENT_HOST_CADDYFILE_TEMPLATE
    else:
        template_path = CADDY_PRODUCTION_HOST_CADDYFILE_TEMPLATE

    local_path = DEREX_DIR / "caddy" / "host"
    ensure_dir(local_path)
    destination = local_path / template_path.name.replace(".j2", "")
    compile_jinja_template(template_path, destination)
    return destination
