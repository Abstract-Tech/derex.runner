# -coding: utf8-
"""Utility functions to deal with docker.
"""
from pathlib import Path
from requests.exceptions import RequestException
from typing import Iterable
from typing import List

import docker
import io
import json
import logging
import pkg_resources
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
}


def is_docker_working() -> bool:
    """Check if we can successfully connect to the docker daemon.
    """
    try:
        client.ping()
        return True
    except RequestException:
        return False


def ensure_volumes_present():
    """Make sure the derex network necessary for our docker-compose files to
    work is in place.
    """
    missing = VOLUMES - {el.name for el in client.volumes.list()}
    for volume in missing:
        logger.warning("Creating docker volume '%s'", volume)
        client.volumes.create(volume)


def check_services(services: Iterable[str] = ("mysql")) -> bool:
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


def execute_mysql_query(query: str):
    """Create the given database in mysql.
    """
    container = client.containers.get("mysql")
    res = container.exec_run(f'mysql -psecret -e "{query}"')
    assert res.exit_code == 0, f"Error running {query}"


def reset_mysql():
    """Run script from derex/openedx image to reset the mysql db.
    """
    logger.warning("Resetting mysql database")
    output = client.containers.run(
        "derex/openedx-ironwood", "restore_dump.py", network="derex", remove=True
    )
    logger.warning(output.decode("utf8").strip())


def wait_for_mysql(max_seconds: int = 20):
    """With a freshly created container mysql might need a bit of time to prime
    its files. This functions waits up to max_seconds seconds
    """
    container = client.containers.get("mysql")
    for i in range(max_seconds):
        res = container.exec_run('mysql -psecret -e "SHOW DATABASES"')
        if res.exit_code == 0:
            break
        time.sleep(1)
        logger.warning("Waiting for mysql database to be ready")


def load_dump(relpath):
    """Loads a mysql dump into the derex mysql database.
    """
    dump_path = Path(pkg_resources.resource_filename(__name__, relpath))
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


def build_image(dockerfile_text: str, paths: List[str], tag: str):
    dockerfile = io.BytesIO(dockerfile_text.encode())
    context = io.BytesIO()
    context_tar = tarfile.open(fileobj=context, mode="w:gz")
    info = tarfile.TarInfo(name="Dockerfile")
    info.size = len(dockerfile_text)
    context_tar.addfile(info, fileobj=dockerfile)
    for path in paths:
        context_tar.add(path, arcname=Path(path).name)
    context_tar.close()
    context.seek(0)
    docker_client = docker.APIClient()
    output = docker_client.build(
        fileobj=context, custom_context=True, encoding="gzip", tag=tag
    )
    for line in output:
        line_decoded = json.loads(line)
        print(line_decoded.get("stream", ""), end="")
        if "error" in line_decoded:
            print(line_decoded.get("error", ""))
        if "aux" in line_decoded:
            print(f'Built image: {line_decoded["aux"]["ID"]}')
