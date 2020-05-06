from derex.runner.docker import build_image
from derex.runner.docker import docker_has_experimental
from derex.runner.project import Project

import logging
import os


logger = logging.getLogger(__name__)


def docker_commands_to_install_requirements(project: Project):
    dockerfile_contents = []
    if project.requirements_dir:
        dockerfile_contents.append(
            f"RUN pip install pip==20.0.2\n"
            # Constrain edx version, but omit the relative paths: we run this from our
            # requirements dir so that the derex user can use `./` in their requirements files
            f"RUN grep == /openedx/edx-platform/requirements/edx/base.txt |grep -v ^git+https > /tmp/base.txt\n"
            f"COPY requirements /openedx/derex.requirements/\n"
        )
        for requirments_file in os.listdir(project.requirements_dir):
            if requirments_file.endswith(".txt"):
                dockerfile_contents.append(
                    f"RUN cd /openedx/derex.requirements && pip install -c /tmp/base.txt -r {requirments_file}\n"
                )
    return dockerfile_contents


def build_requirements_image(project: Project):
    """Build the docker image the includes project requirements for the given project.
    The requirements are installed in a container based on the dev image, and assets
    are compiled there.
    """
    if project.requirements_dir is None:
        return
    dockerfile_contents = [f"FROM {project.base_image}"]
    dockerfile_contents.extend(docker_commands_to_install_requirements(project))
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
            # XXX we only compile the `open-edx` theme. We could make this configurable per-project
            # but probably most people are only interested in their own theme
            "paver update_assets --settings derex.assets --themes open-edx",
            'rmlint -c sh:symlink -o sh:rmlint.sh /openedx/staticfiles > /dev/null 2> /dev/null && sed "/# empty /d" -i rmlint.sh && ./rmlint.sh -d > /dev/null',
        )
    )
    if project.config.get("compile_assets", False):
        dockerfile_contents.append(f"RUN sh -c '{compile_command}'")
    dockerfile_text = "\n".join(dockerfile_contents)
    paths_to_copy = [str(project.requirements_dir)]
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
