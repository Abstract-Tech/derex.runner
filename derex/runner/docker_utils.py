# -coding: utf8-
"""Utility functions to deal with docker.
"""
from derex.runner.secrets import DerexSecrets
from derex.runner.secrets import get_secret
from derex.runner.utils import abspath_from_egg
from derex.runner.utils import copydir
from jinja2 import Environment
from jinja2 import FileSystemLoader
from pathlib import Path
from python_on_whales import docker as pow_docker
from requests.exceptions import RequestException
from shutil import copyfile
from shutil import copytree
from shutil import rmtree
from tempfile import mkdtemp
from tempfile import mkstemp
from typing import Dict
from typing import Iterable
from typing import List
from typing import Optional

import docker
import io
import json
import logging
import os
import re
import tarfile
import time


client = docker.from_env()
logger = logging.getLogger(__name__)
VOLUMES = {
    "derex_elasticsearch",
    "derex_elasticsearch7",
    "derex_mongodb",
    "derex_mongodb4",
    "derex_mysql",
    "derex_mysql57",
    "derex_rabbitmq",
    "derex_portainer_data",
    "derex_minio",
}


def is_docker_working() -> bool:
    """Check if we can successfully connect to the docker daemon."""
    try:
        client.ping()
        return True
    except RequestException:
        return False


def docker_has_experimental() -> bool:
    """Return True if the docker daemon has experimental mode enabled.
    We use this to produce squashed images.
    """
    return bool(client.api.info().get("ExperimentalBuild"))


def ensure_volumes_present():
    """Make sure the derex network necessary for our docker-compose files to
    work is in place.
    """
    missing = VOLUMES - {el.name for el in client.volumes.list()}
    for volume in missing:
        logger.warning("Creating docker volume '%s'", volume)
        client.volumes.create(volume)


def wait_for_service(service: str, max_seconds: int = 35) -> int:
    """With a freshly created container services might need a bit of time to start.
    This functions waits up to max_seconds seconds for the healthcheck on the container
    to report as healthy.
    Returns an exit code 0 or raises an exception:

    * RuntimeError is raised if the service container cannot be found or is not in a running state
    * NotImplementedError is raised if the service doesn't define any healthcheck
    * TimeoutError is raised if the healtcheck doesn't report as healthy in the `max_seconds` amount of time
    """
    for i in range(max_seconds):
        try:
            container_info = client.api.inspect_container(service)
        except docker.errors.NotFound:
            raise RuntimeError(
                f"{service} service not found.\n"
                "Maybe you forgot to run\n"
                "ddc-services up -d"
            )
        container_status = container_info.get("State").get("Status")
        if container_status not in ["running", "restarting"]:
            raise RuntimeError(
                f'Service {service} is not running (status="{container_status}")\n'
                "Maybe you forgot to run\n"
                "ddc-services up -d"
            )
        try:
            healthcheck = container_info.get("State").get("Health").get("Status")
        except AttributeError:
            raise NotImplementedError(
                f"{service} service doesn't declare any healthcheck.\n"
            )
        if healthcheck == "healthy":
            return 0
        time.sleep(1)
        logger.warning(f"Waiting for {service} to be ready")
    raise TimeoutError(f"Can't connect to {service} service")


def check_services(services: Iterable[str], max_seconds: int = 1) -> bool:
    """Check if the specified services are running and healthy.
    For every service it will retry for a `max_seconds` amount of time.
    Returns False if any of the service is unhealthy, True otherwise.
    """
    try:
        for service in services:
            wait_for_service(service, max_seconds)
    except (TimeoutError, RuntimeError, NotImplementedError):
        return False
    return True


def load_dump(relpath):
    """Loads a mysql dump into the derex mysql database."""
    from derex.runner.ddc import run_ddc_services
    from derex.runner.mysql import MYSQL_ROOT_PASSWORD

    wait_for_service("mysql", 30)
    dump_path = abspath_from_egg("derex.runner", relpath)
    logger.info(f"Loading mysql dump from {dump_path}")
    compose_args = [
        "run",
        "--rm",
        "-v",
        f"{dump_path.parent}:/dump",
        "-T",
        "mysql",
        "sh",
        "-c",
        f"mysql -h mysql -p{MYSQL_ROOT_PASSWORD} < /dump/{dump_path.name}",
    ]
    run_ddc_services(compose_args)


def build_image(
    dockerfile_text: str,
    paths: List[str],
    tag: str,
    tag_final: bool = False,
    extra_options: Dict = {},
):
    """Build a docker image. Prepares a build context (a tar stream)
    based on the `paths` argument and includes the Dockerfile text passed
    in `dockerfile_text`.
    """
    dockerfile = io.BytesIO(dockerfile_text.encode())
    context = io.BytesIO()
    context_tar = tarfile.open(fileobj=context, mode="w:gz", dereference=True)
    info = tarfile.TarInfo(name="Dockerfile")
    info.size = len(dockerfile_text)
    context_tar.addfile(info, fileobj=dockerfile)
    for path in paths:
        context_tar.add(path, arcname=Path(path).name)
    context_tar.close()
    context.seek(0)

    if docker_has_experimental():
        extra_options.update(dict(squash=True))
    else:
        logger.warning(
            "To build a smaller image enable the --experimental flag in the docker server"
        )

    output = client.api.build(
        fileobj=context, custom_context=True, encoding="gzip", tag=tag, **extra_options
    )
    for lines in output:
        for line in re.split(rb"\r\n|\n", lines):
            if not line:  # Split empty lines
                continue
            line_decoded = json.loads(line)
            if "error" in line_decoded:
                raise BuildError(line_decoded["error"])
            print(line_decoded.get("stream", ""), end="")
            if "error" in line_decoded:
                print(line_decoded.get("error", ""))
            if "aux" in line_decoded:
                print(f'Built image: {line_decoded["aux"]["ID"]}')
    if tag_final:
        final_tag = tag.rpartition(":")[0] + ":latest"
        for image in client.api.images():
            if image.get("RepoTags") and tag in image["RepoTags"]:
                client.api.tag(image["Id"], final_tag)


def buildx_image(
    dockerfile_text: str,
    paths: List[Path],
    target: str,
    output: str,
    tags: List[str],
    pull: bool,
    cache: bool,
    cache_from: bool,
    cache_to: bool,
    cache_tag: bool,
    build_args: Dict = {},
):
    # This gets imported here to avoid a circular import
    from derex.runner.project import Project

    tempdir = Path(mkdtemp(prefix="derex-build-"))
    try:
        _, dockerfile_str_path = mkstemp(prefix="Dockerfile-", dir=tempdir)
        dockerfile = Path(dockerfile_str_path)
        dockerfile.write_text(dockerfile_text)

        for path in paths:
            destination_tmp_dir_path = Path(tempdir / path.name)
            if path.is_dir():
                try:
                    copytree(path, destination_tmp_dir_path)
                except FileExistsError:
                    copydir(str(path), str(destination_tmp_dir_path))
            if path.is_file():
                copyfile(path, destination_tmp_dir_path)

                if path.name.endswith(".j2") and not path.name == "Dockerfile.j2":
                    jinja_environment = Environment(
                        loader=FileSystemLoader(destination_tmp_dir_path.parent)
                    )
                    template = jinja_environment.get_template(
                        destination_tmp_dir_path.name
                    )
                    rendered_template = template.render(
                        project=Project(),
                    )
                    Path(
                        destination_tmp_dir_path.parent
                        / destination_tmp_dir_path.name.replace(".j2", "")
                    ).write_text(rendered_template)

        cache_from_arg: Optional[Dict] = None
        cache_to_arg: Optional[Dict] = None
        if cache_from and cache_tag:
            cache_from_arg = {"type": "registry", "src": cache_tag}
        if cache_to and cache_tag:
            cache_to_arg = {"type": "registry", "dest": cache_tag, "mode": "max"}
        if cache:
            build_args.update({"BUILDKIT_INLINE_CACHE": "1"})

        pow_docker.buildx.build(
            context_path=tempdir,
            file=dockerfile,
            target=target,
            output={"type": output},
            tags=tags,
            pull=pull,
            cache=cache,
            cache_from=cache_from_arg,
            cache_to=cache_to_arg,
            build_args=build_args,
        )
    finally:
        rmtree(tempdir)


def pull_images(image_names: List[str]):
    """Pull the given image to the local docker daemon."""
    # digest = client.api.inspect_distribution(image_name)["Descriptor"]["digest"]
    for image_name in image_names:
        print(f"Pulling image {image_name}")
        for out in client.api.pull(image_name, stream=True, decode=True):
            if "progress" in out:
                print(f'{out["id"]}: {out["progress"]}', end="\r")
            else:
                print(out["status"])


def image_exists(needle: str) -> bool:
    """If the given image tag exist in the local docker repository, return True."""
    images = client.api.images()
    images.sort(key=lambda el: el["Created"], reverse=True)
    for image in images:
        if "RepoTags" not in image or not image["RepoTags"]:
            continue
        if needle in image["RepoTags"]:
            return True
    return False


class BuildError(RuntimeError):
    """An error occurred while building a docker image"""


def get_running_containers() -> Dict:
    if "derex" in [network.name for network in client.networks.list()]:
        return {
            container.name: client.api.inspect_container(container.name)
            for container in client.networks.get("derex").containers
        }
    return {}


def get_exposed_container_names() -> List:
    result = []
    for container in get_running_containers().values():
        names = container["NetworkSettings"]["Networks"]["derex"]["Aliases"]
        matching_names = list(filter(lambda el: el.endswith("localhost.derex"), names))
        if matching_names:
            matching_names.append(
                container["NetworkSettings"]["Networks"]["derex"]["IPAddress"]
            )
            result.append(
                tuple(
                    map(
                        lambda el: "http://" + re.sub(".derex$", "", el), matching_names
                    )
                )
            )
    return result


def run_minio_shell(command: str = "sh", tty: bool = True):
    """Invoke a minio shell"""
    minio_key = get_secret(DerexSecrets.minio)
    os.system(
        f"docker run {'-ti ' if tty else ''}--rm --network derex --entrypoint /bin/sh minio/mc -c '"
        f'mc config host add local http://minio:80 minio_derex "{minio_key}" --api s3v4 ; set -ex; {command}\''
    )
