from derex.runner.constants import DEREX_TEMPLATES_DIR
from derex.runner.constants import ProjectBuildTargets
from derex.runner.docker_utils import build_image
from derex.runner.docker_utils import buildx_image
from derex.runner.docker_utils import docker_has_experimental
from derex.runner.project import Project
from jinja2 import Environment
from jinja2 import FileSystemLoader
from pathlib import Path
from typing import List
from typing import Optional

import logging
import os


logger = logging.getLogger(__name__)


def docker_commands_to_install_requirements(project: Project):
    dockerfile_contents = []
    if project.requirements_dir:
        dockerfile_contents.append("COPY requirements /openedx/derex.requirements/\n")
        for requirments_file in os.listdir(project.requirements_dir):
            if requirments_file.endswith(".txt"):
                dockerfile_contents.append(
                    "RUN cd /openedx/derex.requirements && "
                    f"pip install -r {requirments_file} -c /openedx/requirements/openedx_constraints.txt\n"
                )
    return dockerfile_contents


def generate_legacy_requirements_dockerfile(project):
    dockerfile_contents = [f"FROM {project.base_image}"]
    dockerfile_contents.extend(docker_commands_to_install_requirements(project))

    openedx_customizations = project.get_openedx_customizations()
    if openedx_customizations:
        for destination, source in openedx_customizations.items():
            docker_build_context_source = source
            docker_build_context_source = docker_build_context_source.replace(
                str(project.openedx_customizations_dir), "openedx_customizations"
            )
            dockerfile_contents.append(
                f"COPY {docker_build_context_source} {destination}"
            )

    compile_command = ("; \\\n").join(
        (
            # Remove files from the previous image
            "rm -rf /openedx/staticfiles",
            "derex_update_assets",
            "derex_cleanup_assets",
        )
    )
    if project.config.get("update_assets", False):
        dockerfile_contents.append(f"RUN sh -c '{compile_command}'")
    dockerfile_text = "\n".join(dockerfile_contents)
    return dockerfile_text


def build_requirements_image(project: Project):
    """Build the docker image the includes project requirements for the given project.
    The requirements are installed in a container based on the dev image, and assets
    are compiled there.
    """
    if project.requirements_dir is None:
        return
    paths_to_copy = [str(project.requirements_dir)]

    if project.openedx_customizations_dir:
        paths_to_copy.append(project.openedx_customizations_dir)

    dockerfile_text = generate_legacy_requirements_dockerfile(project)
    build_image(dockerfile_text, paths_to_copy, tag=project.requirements_image_name)


def generate_legacy_themes_dockerfile(project):
    dockerfile_contents = [
        f"FROM {project.requirements_image_name} as static",
        f"FROM {project.final_base_image}",
        "COPY --from=static /openedx/staticfiles /openedx/staticfiles",
        "COPY themes/ /openedx/themes/",
        "COPY --from=static /openedx/edx-platform/common/static /openedx/edx-platform/common/static",
        "COPY --from=static /openedx/empty_dump.sql.bz2 /openedx/",
    ]
    if docker_has_experimental():
        # When experimental is enabled we have the `squash` option: we can remove duplicates
        # so they won't end up in our layer.
        dockerfile_contents.append("RUN derex_cleanup_assets")
    if project.requirements_dir is not None:
        dockerfile_contents.extend(docker_commands_to_install_requirements(project))
    cmd = []
    if project.themes_dir is not None:
        for dir in project.themes_dir.iterdir():
            for variant, destination in (("lms", ""), ("cms", "/studio")):
                if (dir / variant).is_dir():
                    cmd.append(
                        f"mkdir -p /openedx/staticfiles{destination}/{dir.name}/"
                    )
                    cmd.append(
                        f"ln -s /openedx/themes/{dir.name}/{variant}/static/* /openedx/staticfiles{destination}/{dir.name}/"
                    )
    if cmd:
        dockerfile_contents.append(f"RUN sh -c '{';'.join(cmd)}'")

    dockerfile_text = "\n".join(dockerfile_contents)
    return dockerfile_text


def build_themes_image(project: Project):
    """Build the docker image the includes themes and requirements for the given project.
    The image will be lightweight, containing only things needed to run Open edX.
    """
    if project.themes_dir is None:
        return

    paths_to_copy = [str(project.themes_dir)]
    if project.requirements_dir is not None:
        paths_to_copy.append(str(project.requirements_dir))

    dockerfile_text = generate_legacy_themes_dockerfile(project)
    if docker_has_experimental():
        build_image(
            dockerfile_text,
            paths_to_copy,
            tag=project.themes_image_name,
            tag_final=True,
            extra_opts=dict(squash=True),
        )
    else:
        build_image(
            dockerfile_text,
            paths_to_copy,
            tag=project.themes_image_name,
            tag_final=True,
        )
        logger.warning(
            "To build a smaller image enable the --experimental flag in the docker server"
        )


def build_project_image(
    project: Project,
    target: ProjectBuildTargets,
    output: str,
    registry: Optional[str],
    tag: str,
    tag_latest: bool,
    pull: bool,
    no_cache: bool,
    cache_from: bool,
    cache_to: bool,
):
    """Compile a Dockerfile, create the build context and build a docker image for a projects"""
    if not registry and project.docker_registry:
        registry = project.docker_registry
    if registry:
        tag = f"{registry}/{tag}"
    tags: List[str] = [tag]
    image_name: str = tag.split(":")[0]
    if tag_latest:
        latest_tag = f"{image_name}:latest"
        tags.append(latest_tag)

    cache: bool = False if no_cache else True
    cache_tag: Optional[str] = None
    if cache:
        if registry:
            cache_tag = f"{registry}/{image_name}:cache"
        else:
            cache_tag = f"{image_name}:cache"

    paths_to_copy: List[Path] = []
    for build_target in ProjectBuildTargets.__members__:
        if target.value >= ProjectBuildTargets[build_target].value:
            directory = getattr(
                project, f"{ProjectBuildTargets[build_target].name}_dir"
            )
            if directory and directory.is_dir():
                paths_to_copy.append(directory)

    jinja_environment = Environment(loader=FileSystemLoader(DEREX_TEMPLATES_DIR))
    dockerfile_template = jinja_environment.get_template("Dockerfile-project.j2")
    dockerfile_text = dockerfile_template.render(
        project=project,
    )

    buildx_image(
        dockerfile_text,
        paths_to_copy,
        target.name,
        output,
        tags,
        pull,
        cache,
        cache_from,
        cache_to,
        cache_tag,
    )


__all__ = ["build_requirements_image", "build_themes_image"]
