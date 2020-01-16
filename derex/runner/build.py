from derex.runner.docker import build_image
from derex.runner.project import Project

import os


def docker_commands_to_install_requirements(project: Project):
    dockerfile_contents = []
    if project.requirements_dir:
        dockerfile_contents.append(f"COPY requirements /openedx/derex.requirements/")
        for requirments_file in os.listdir(project.requirements_dir):
            if requirments_file.endswith(".txt"):
                dockerfile_contents.append(
                    f"RUN pip install -r /openedx/derex.requirements/{requirments_file} --no-cache"
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
    compile_command = (
        # Remove files from the previous image
        "rm -rf /openedx/staticfiles;"
        "cd /openedx/edx-platform;"
        "export PATH=/openedx/edx-platform/node_modules/.bin:${PATH}; "
        # The rmlint optmization breaks the build process.
        # We clean the repo files
        "git checkout HEAD -- common;"
        "git clean -fdx common/static;"
        # Make sure ./manage.py sets the SERVICE_VARIANT variable each time it's invoked
        "unset SERVICE_VARIANT;"
        # XXX we only compile the `open-edx` theme. We could make this configurable per-project
        # but probably most people are only interested in their own theme
        "paver update_assets --settings derex.assets --themes open-edx;"
        'rmlint -g -c sh:symlink -o json:stderr /openedx/staticfiles 2> /dev/null && sed "/# empty /d" -i rmlint.sh && ./rmlint.sh -d > /dev/null'
    )
    if project.config.get("compile_assets", False):
        dockerfile_contents.append(f"RUN sh -c '{compile_command}'")
    dockerfile_text = "\n".join(dockerfile_contents)

    paths_to_copy = [str(project.requirements_dir)]
    build_image(dockerfile_text, paths_to_copy, tag=project.requirements_image_tag)


def build_themes_image(project: Project):
    """Build the docker image the includes themes and requirements for the given project.
    The image will be lightweight, containing only things needed to run edX.
    """
    if project.themes_dir is None:
        return
    dockerfile_contents = [
        f"FROM {project.requirements_image_tag} as static",
        f"FROM {project.final_base_image}",
        "COPY --from=static /openedx/staticfiles /openedx/staticfiles",
        f"COPY themes/ /openedx/themes/",
        # It would be nice to run the following here, but docker immediately commits a layer after COPY,
        # so the files we'd like to remove are already final.
        # rmlint -g -c sh:symlink -o json:stderr /openedx/ 2> /dev/null && sed "/# empty /d" -i rmlint.sh && ./rmlint.sh -d > /dev/null
    ]
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
    paths_to_copy = [str(project.themes_dir)]
    build_image(
        dockerfile_text, paths_to_copy, tag=project.themes_image_tag, tag_final=True
    )
