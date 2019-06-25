# -coding: utf8-
"""Utility functions to deal with docker.
"""
import docker
import logging


client = docker.from_env()


def ensure_network_present():
    """Make sure the derex network necessary for our docker-compose files to
    work is in place.
    """
    try:
        client.networks.get("derex")
    except docker.errors.NotFound:
        logging.getLogger(__name__).warn("Creating docker network 'derex'")
        client.networks.create("derex")
