# -coding: utf8-
"""Utility functions to deal with docker.
"""
from derex.runner.secrets import DerexSecrets
from derex.runner.secrets import get_secret
from derex.runner.utils import abspath_from_egg
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
logger = logging.getLogger(__name__)
VOLUMES = {
    "derex_elasticsearch",
    "derex_mongodb",
    "derex_mysql",
    "derex_rabbitmq",
    "derex_portainer_data",
    "derex_minio",
}


def is_docker_working() -> bool:
    """Check if we can successfully connect to the docker daemon.
    """
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


def check_services(services: Iterable[str]) -> bool:
    """Check if the services needed for running Open edX are running.
    """
    result = True
    try:
        for service in services:
            container = client.containers.get(service)
            result *= container.status == "running"
        return result
    except docker.errors.NotFound:
        return False


def wait_for_service(service: str, check_command: str, max_seconds: int = 20):
    """With a freshly created container services might need a bit of time to start.
    This functions waits up to max_seconds seconds.
    """
    container = client.containers.get(service)
    for i in range(max_seconds):
        res = container.exec_run(check_command)
        if res.exit_code == 0:
            return 0
        time.sleep(1)
        logger.warning(f"Waiting for {service} to be ready")
    raise TimeoutError(f"Can't connect to {service} service")


def load_dump(relpath):
    """Loads a mysql dump into the derex mysql database.
    """
    dump_path = abspath_from_egg("derex.runner", relpath)
    image = client.containers.get("mysql").image
    logger.info("Resetting email database")
    try:
        client.containers.run(
            image.tags[0],
            ["sh", "-c", f"mysql -h mysql -psecret < /dump/{dump_path.name}"],
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
    """Pull the given image to the local docker daemon.
    """
    # digest = client.api.inspect_distribution(image_name)["Descriptor"]["digest"]
    for image_name in image_names:
        print(f"Pulling image {image_name}")
        for out in client.api.pull(image_name, stream=True, decode=True):
            if "progress" in out:
                print(f'{out["id"]}: {out["progress"]}', end="\r")
            else:
                print(out["status"])


def image_exists(needle: str) -> bool:
    """If the given image tag exist in the local docker repository, return True.
    """
    docker_client = docker.APIClient()
    images = docker_client.images()
    images.sort(key=lambda el: el["Created"], reverse=True)
    for image in images:
        if "RepoTags" not in image or not image["RepoTags"]:
            continue
        if needle in image["RepoTags"]:
            return True
    return False


class BuildError(RuntimeError):
    """An error occurred while building a docker image
    """


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


def run_minio_shell(command="sh"):
    """Invoke a minio shell
    """
    minio_key = get_secret(DerexSecrets.minio)
    os.system(
        "docker run -ti --rm --network derex --entrypoint /bin/sh minio/mc -c '"
        f'mc config host add local http://minio:80 minio_derex "{minio_key}" --api s3v4 ; set -ex; {command}\''
    )
