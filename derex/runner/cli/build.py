from .utils import ensure_project
from derex.runner import __version__
from derex.runner.project import OpenEdXVersions
from derex.runner.project import Project
from derex.runner.utils import abspath_from_egg
from distutils.spawn import find_executable

import click
import os
import sys


@click.group()
def build():
    """Commands to build container images"""


@build.command()
@click.pass_obj
@ensure_project
def requirements(project):
    """Build the image that contains python requirements"""
    from derex.runner.build import build_requirements_image

    click.echo(
        f'Building docker image {project.requirements_image_name} ("{project.name}" requirements)'
    )
    build_requirements_image(project)


@build.command()
@click.pass_obj
@click.pass_context
@ensure_project
def themes(ctx, project: Project):
    """Build the image that includes compiled themes"""
    from derex.runner.build import build_themes_image

    ctx.forward(requirements)
    click.echo(
        f'Building docker image {project.themes_image_name} with "{project.name}" themes'
    )
    build_themes_image(project)
    click.echo(f"Built image {project.themes_image_name}")


@build.command()
@click.pass_obj
@click.pass_context
@ensure_project
def final(ctx, project: Project):
    """Build the final image for this project.
    For now this is the same as the final image"""
    ctx.forward(themes)


@build.command()
@click.pass_obj
@click.pass_context
@ensure_project
def final_refresh(ctx, project: Project):
    """Also pull base docker image before starting building"""
    from derex.runner.docker_utils import pull_images

    pull_images([project.base_image, project.final_base_image])
    ctx.forward(final)


@build.command()
@click.argument(
    "version",
    type=click.Choice(OpenEdXVersions.__members__),
    required=True,
    callback=lambda _, __, value: value and OpenEdXVersions[value],
)
@click.option(
    "-t",
    "--target",
    type=click.Choice(
        [
            "dev",
            "nostatic-dev",
            "nostatic",
            "libgeos",
            "base",
            "sourceonly",
            "wheels",
            "translations",
            "nodump",
        ]
    ),
    default="dev",
    help="Target to build (nostatic, dev, translations)",
)
@click.option(
    "--push/--no-push", default=False, help="Also push image to registry after building"
)
@click.option(
    "--only-print-image-name/--do-build",
    default=False,
    help="Only print image name for the given target",
)
@click.option(
    "-d",
    "--docker-opts",
    envvar="DOCKER_OPTS",
    default="--output type=image,name={docker_image_prefix}-{target}{push_arg}",
    help=(
        "Additional options to pass to the docker invocation.\n"
        "By default outputs the image to the local docker daemon."
    ),
)
def openedx(version, target, push, only_print_image_name, docker_opts):
    """Build openedx image using docker. Defaults to dev image target."""
    dockerdir = abspath_from_egg("derex.runner", "docker-definition/Dockerfile").parent
    git_repo = version.value["git_repo"]
    git_branch = version.value["git_branch"]
    alpine_version = version.value["alpine_version"]
    python_version = version.value["python_version"]
    pip_version = version.value["pip_version"]
    docker_image_prefix = version.value["docker_image_prefix"]
    image_name = f"{docker_image_prefix}-{target}:{__version__}"
    if only_print_image_name:
        click.echo(image_name)
        return
    push_arg = ",push=true" if push else ""
    command = [
        "docker",
        "buildx",
        "build",
        str(dockerdir),
        "-t",
        image_name,
        "--build-arg",
        f"ALPINE_VERSION={alpine_version}",
        "--build-arg",
        f"PYTHON_VERSION={python_version}",
        "--build-arg",
        f"PIP_VERSION={pip_version}",
        "--build-arg",
        f"EDX_PLATFORM_RELEASE={version.name}",
        "--build-arg",
        f"EDX_PLATFORM_VERSION={git_branch}",
        "--build-arg",
        f"EDX_PLATFORM_REPOSITORY={git_repo}",
        f"--target={target}",
    ]
    transifex_path = os.path.expanduser("~/.transifexrc")
    if os.path.exists(transifex_path):
        command.extend(["--secret", f"id=transifex,src={transifex_path}"])
    if docker_opts:
        command.extend(docker_opts.format(**locals()).split())
    print("Invoking\n" + " ".join(command), file=sys.stderr)
    os.execve(find_executable(command[0]), command, os.environ)
