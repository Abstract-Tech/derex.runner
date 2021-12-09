from .utils import ensure_project
from derex.runner import __version__
from derex.runner.build import build_project_image
from derex.runner.cli.utils import red
from derex.runner.constants import ProjectBuildTargets
from derex.runner.project import OpenEdXVersions
from derex.runner.project import Project
from derex.runner.utils import abspath_from_egg
from distutils.spawn import find_executable
from typing import Optional

import click
import os
import sys


@click.group()
def build():
    """Commands to build container images"""


@build.command()
@click.pass_obj
@ensure_project
@click.option(
    "-T",
    "--target",
    type=click.Choice(ProjectBuildTargets.__members__),
    default="final",
    help="Target to build",
)
@click.option(
    "-o",
    "--output",
    type=click.Choice(["docker", "registry"]),
    default="docker",
    help="Where to push the resulting image",
)
@click.option("-r", "--registry", type=str)
@click.option("-t", "--tag", type=str)
@click.option("--latest", "tag_latest", is_flag=True, default=False)
@click.option(
    "--only-print-image-name",
    is_flag=True,
    default=False,
    help="Only print the name which will be assigned to the image",
)
@click.option(
    "--pull",
    is_flag=True,
    default=False,
    help="Always try to pull the newer version of the image",
)
@click.option("--no-cache", is_flag=True, default=False)
@click.option("--cache-from", is_flag=True, default=False)
@click.option("--cache-to", is_flag=True, default=False)
def project(
    project: Project,
    target: str,
    output: str,
    registry: Optional[str],
    tag: Optional[str],
    tag_latest: bool,
    only_print_image_name: bool,
    pull: bool,
    no_cache: bool,
    cache_from: bool,
    cache_to: bool,
):
    """
    Build the project specific openedx image.

    Images will be built using Buildkit (https://docs.docker.com/develop/develop-images/build_enhancements/).

    A target image can be specified.
    Available targets for openedx include:

        * requirements: include all project requirements (system dependencies, python packages)\n
        * openedx_customizations: include all project customizations to the openedx source code\n
        * scripts: include bash and python scripts\n
        * settings: include Django settings\n
        * translations: include project specific compiled translations\n
        * themes: include the project compiled themes and staticfiles\n
        * final: include everything needed for this project\n

    The image tag, if not specified, will be derived from the project `image_prefix`,
    the target image computed tag and the registry (from option or from project
    config).
    """
    if not project.get_project_hash():
        click.echo("No customizations found for this project, nothing to build.")
        return 0

    target_enum = ProjectBuildTargets[target]
    image_tag = tag or project.get_build_target_image_name(target_enum)
    if only_print_image_name:
        click.echo(image_tag)
        return 0

    if cache_from or cache_to or output == "registry":
        if not registry:
            if project.docker_registry:
                registry = project.docker_registry
            else:
                raise click.exceptions.MissingParameter(
                    param_hint="registry",
                    param_type="str",
                    message="You need to define a registry to push or import/export the cache",
                )

    click.echo(
        f'Building docker image {image_tag} ("{project.name}" {target_enum.name})'
    )
    try:
        build_project_image(
            project,
            target=target_enum,
            output=output,
            registry=registry,
            tag=image_tag,
            tag_latest=tag_latest,
            pull=pull,
            no_cache=no_cache,
            cache_from=cache_from,
            cache_to=cache_to,
        )
    except Exception as e:
        click.echo(red(e))
        return 1


@build.command()
@click.pass_obj
@ensure_project
def requirements(project):
    """Build the image that contains python requirements"""
    from derex.runner.build import build_requirements_image

    click.echo(
        f'Building docker image {project.get_build_target_image_name(ProjectBuildTargets.requirements)} ("{project.name}" requirements)'
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
        f'Building docker image {project.get_build_target_image_name(ProjectBuildTargets.themes)} with "{project.name}" themes'
    )
    build_themes_image(project)
    click.echo(
        f"Built image {project.get_build_target_image_name(ProjectBuildTargets.themes)}"
    )


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

    pull_images([project.base_image, project.nostatic_base_image])
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
            "notranslations",
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
    build_arguments = []
    for spec in version.value.items():
        build_arguments.append("--build-arg")
        build_arguments.append(f"{spec[0].upper()}={spec[1]}")
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
        *build_arguments,
        f"--target={target}",
    ]
    transifex_path = os.path.expanduser("~/.transifexrc")
    if os.path.exists(transifex_path):
        command.extend(["--secret", f"id=transifex,src={transifex_path}"])
    if docker_opts:
        command.extend(docker_opts.format(**locals()).split())
    print("Invoking\n" + " ".join(command), file=sys.stderr)
    os.execve(find_executable(command[0]), command, os.environ)
