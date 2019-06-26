# -coding: utf8-
"""Utility functions to deal with docker.
"""
import docker
import logging


client = docker.from_env()
logger = logging.getLogger(__name__)
VOLUMES = {
    "derex_elasticsearch",
    "derex_mongodb",
    "derex_mysql",
    "derex_rabbitmq",
    "derex_portainer_data",
}


def ensure_network_present():
    """Make sure the derex network necessary for our docker-compose files to
    work is in place.
    """
    try:
        client.networks.get("derex")
    except docker.errors.NotFound:
        logger.warning("Creating docker network 'derex'")
        client.networks.create("derex")


def ensure_volumes_present():
    """Make sure the derex network necessary for our docker-compose files to
    work is in place.
    """
    missing = VOLUMES - {el.name for el in client.volumes.list()}
    for volume in missing:
        logger.warning("Creating docker volume '%s'", volume)
        client.volumes.create(volume)


def create_deps():
    """Make sure the resources we depened on (network and volumes) are present.
    Create them if not.
    """
    ensure_network_present()
    ensure_volumes_present()
