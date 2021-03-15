from derex.runner.constants import DEREX_OPENEDX_CUSTOMIZATIONS_PATH
from derex.runner.docker_utils import build_image
from derex.runner.docker_utils import docker_has_experimental
from derex.runner.project import Project

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


def build_requirements_image(project: Project):
    """Build the docker image the includes project requirements for the given project.
    The requirements are installed in a container based on the dev image, and assets
    are compiled there.
    """
    if project.requirements_dir is None:
        return
    paths_to_copy = [str(project.requirements_dir)]
    dockerfile_contents = [f"FROM {project.base_image}"]
    dockerfile_contents.extend(docker_commands_to_install_requirements(project))

    openedx_customizations = project.get_openedx_customizations()
    if openedx_customizations:
        openedx_customizations_paths = [DEREX_OPENEDX_CUSTOMIZATIONS_PATH]
        if project.openedx_customizations_dir:
            openedx_customizations_paths.append(project.openedx_customizations_dir)

        for openedx_customization_path in openedx_customizations_paths:
            paths_to_copy.append(openedx_customization_path)

        for destination, source in openedx_customizations.items():
            docker_build_context_source = None
            for openedx_customization_path in openedx_customizations_paths:
                docker_build_context_source = source.replace(
                    str(openedx_customization_path), "openedx_customizations"
                )
            dockerfile_contents.append(
                f"COPY {docker_build_context_source} {destination}"
            )

    compile_command = ("; \\\n").join(
        (
            # Remove files from the previous image
            "rm -rf /openedx/staticfiles",
            "cd /openedx/edx-platform",
            "export PATH=/openedx/edx-platform/node_modules/.bin:${PATH}",
            "export ENV NO_PREREQ_INSTALL=True",
            "export ENV NO_PYTHON_UNINSTALL=True",
            # The rmlint optmization breaks the build process.
            # We clean the repo files
            "git checkout HEAD -- common",
            "git clean -fdx common/static",
            # Make sure ./manage.py sets the SERVICE_VARIANT variable each time it's invoked
            "unset SERVICE_VARIANT",
            # If DJANGO_SETTINGS_MODULE is defined settings will be initialized twice
            # leading to a `RuntimeError: Settings already configured.` when paver
            # calls `process_xmodule_assets`
            "unset DJANGO_SETTINGS_MODULE",
            # XXX we only compile the `open-edx` theme. We could make this configurable per-project
            # but probably most people are only interested in their own theme
            "paver update_assets --settings derex.assets --themes open-edx",
            'rmlint -c sh:symlink -o sh:rmlint.sh /openedx/staticfiles > /dev/null 2> /dev/null && sed "/# empty /d" -i rmlint.sh && ./rmlint.sh -d > /dev/null',
        )
    )
    if project.config.get("compile_assets", False):
        dockerfile_contents.append(f"RUN sh -c '{compile_command}'")
    dockerfile_text = "\n".join(dockerfile_contents)
    build_image(dockerfile_text, paths_to_copy, tag=project.requirements_image_name)


def build_themes_image(project: Project):
    """Build the docker image the includes themes and requirements for the given project.
    The image will be lightweight, containing only things needed to run edX.
    """
    if project.themes_dir is None:
        return
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
        dockerfile_contents.append(
            'RUN rmlint -g -c sh:symlink -o sh:rmlint.sh /openedx/ > /dev/null 2> /dev/null && sed "/# empty /d" -i rmlint.sh && ./rmlint.sh -d > /dev/null'
        )
    paths_to_copy = [str(project.themes_dir)]
    if project.requirements_dir is not None:
        dockerfile_contents.extend(docker_commands_to_install_requirements(project))
        paths_to_copy.append(str(project.requirements_dir))
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


__all__ = ["build_requirements_image", "build_themes_image"]
