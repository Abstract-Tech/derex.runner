# -coding: utf8-
"""Utility functions to deal with docker.
"""
import docker
import logging
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


def check_services() -> bool:
    """Check if the services needed for running Open edX are running.
    """
    try:
        container = client.containers.get("mysql")
        return container.status == "running"
    except docker.errors.NotFound:
        return False


def create_database(dbname: str):
    """Create the given database in mysql.
    """
    container = client.containers.get("mysql")
    res = container.exec_run(
        f'mysql -psecret -e "CREATE DATABASE IF NOT EXISTS {dbname}"'
    )
    assert res.exit_code == 0


def reset_mysql():
    """Run script from derex/openedx image to reset the mysql db.
    """
    logger.warn("Resetting mysql database")
    output = client.containers.run(
        "derex/openedx-ironwood", "restore_dump.py", network="derex", remove=True
    )
    logger.warn(output.decode("utf8").strip())


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
        logger.warn("Waiting for mysql database to be ready")
