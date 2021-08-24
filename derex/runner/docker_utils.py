# -coding: utf8-
"""Utility functions to deal with docker.
"""
from derex.runner import abspath_from_egg
from derex.runner.constants import DerexSecrets
from derex.runner.exceptions import BuildError
from derex.runner.project import Project
from pathlib import Path
from requests.exceptions import RequestException
from typing import Dict
from typing import Iterable
from typing import List

import docker
import io
import json
import logging
import os
import re
import tarfile
import time


client = docker.from_env()
api_client = docker.APIClient()
logger = logging.getLogger(__name__)


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


def ensure_volumes_present(project: Project):
    """Make sure the derex network necessary for our docker-compose files to
    work is in place.
    """
    missing = project.docker_volumes - {el.name for el in client.volumes.list()}
    for volume in missing:
        logger.warning("Creating docker volume '%s'", volume)
        client.volumes.create(volume)


def wait_for_container(container_name: str, max_seconds: int = 35) -> int:
    """A freshly created container might need a bit of time to start.
    This functions waits up to max_seconds seconds for the healthcheck on the container
    to report as healthy.
    Returns an exit code 0 or raises an exception:

    * RuntimeError is raised if the service container cannot be found or is not in a running state
    * NotImplementedError is raised if the service doesn't define any healthcheck
    * TimeoutError is raised if the healtcheck doesn't report as healthy in the `max_seconds` amount of time
    """
    for i in range(max_seconds):
        try:
            container_info = api_client.inspect_container(container_name)
        except docker.errors.NotFound:
            raise RuntimeError(
                f"{container_name} container not found.\n"
                "Maybe you forgot to run\n"
                "ddc-services up -d"
            )
        container_status = container_info.get("State").get("Status")
        if container_status not in ["running", "restarting"]:
            raise RuntimeError(
                f'{container_name} container is not running (status="{container_status}")\n'
                "Maybe you forgot to run\n"
                "ddc-services up -d"
            )
        try:
            healthcheck = container_info.get("State").get("Health").get("Status")
        except AttributeError:
            raise NotImplementedError(
                f"{container_name} container doesn't declare any healthcheck.\n"
            )
        if healthcheck == "healthy":
            return 0
        time.sleep(1)
        logger.warning(f"Waiting for {container_name} to be ready")
    raise TimeoutError(f"Can't connect to {container_name} container")


def check_containers(containers: Iterable[str], max_seconds: int = 1) -> bool:
    """Check if the specified containers are running and healthy.
    For every container it will retry for a `max_seconds` amount of time.
    Returns False if any of the container is unhealthy, True otherwise.
    """
    try:
        for container in containers:
            wait_for_container(container, max_seconds)
    except (TimeoutError, RuntimeError, NotImplementedError):
        return False
    return True


def load_dump(project: Project, relative_path: Path):
    """Loads a mysql dump into the derex mysql database."""
    dump_path = abspath_from_egg("derex.runner", relative_path)
    image = client.containers.get(project.mysql_host).image
    logger.info("Resetting email database")
    try:
        client.containers.run(
            image.tags[0],
            [
                "sh",
                "-c",
                f"mysql -h {project.mysql_host} -p{project.mysql_password} < /dump/{dump_path.name}",
            ],
            network="derex",
            volumes={dump_path.parent: {"bind": "/dump"}},
            auto_remove=True,
        )
    except docker.errors.ContainerError as exc:
        logger.exception(exc)


def build_image(
    dockerfile_text: str,
    paths: List[str],
    tag: str,
    tag_final: bool = False,
    extra_opts: Dict = {},
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
    output = client.api.build(
        fileobj=context, custom_context=True, encoding="gzip", tag=tag, **extra_opts
    )
    for lines in output:
        for line in re.split(br"\r\n|\n", lines):
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
    docker_client = docker.APIClient()
    images = docker_client.images()
    images.sort(key=lambda el: el["Created"], reverse=True)
    for image in images:
        if "RepoTags" not in image or not image["RepoTags"]:
            continue
        if needle in image["RepoTags"]:
            return True
    return False


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


def run_minio_shell(project: Project, command: str = "sh", tty: bool = True):
    """Invoke a minio shell"""
    minio_key = project.get_secret(DerexSecrets.minio)
    os.system(
        f"docker run {'-ti ' if tty else ''}--rm --network derex --entrypoint /bin/sh minio/mc -c '"
        f'mc config host add local http://minio:80 minio_derex "{minio_key}" --api s3v4 ; set -ex; {command}\''
    )
