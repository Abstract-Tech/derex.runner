from derex.runner.docker import check_services
from derex.runner.docker import wait_for_service
from pymongo import MongoClient
from typing import List

import logging


logger = logging.getLogger(__name__)


def wait_for_mongodb(max_seconds: int = 20):
    """With a freshly created container mongodb might need a bit of time to prime
    its files. This functions waits up to max_seconds seconds.
    """
    return wait_for_service("mongodb", "mongo", max_seconds)


def get_mongodb_client() -> MongoClient:
    """Return a client interface to the mongodb server"""
    from derex.runner.docker import client as docker_client

    if not check_services(["mongodb"]):
        raise RuntimeError(
            "MongoDB service not found.\nMaybe you forgot to run\nddc-services up -d"
        )

    wait_for_mongodb()
    container = docker_client.containers.get("mongodb")
    mongo_address = container.attrs["NetworkSettings"]["Networks"]["derex"]["IPAddress"]

    return MongoClient(f"mongodb://{mongo_address}:27017/")


def list_databases() -> List[dict]:
    """List all existing databases"""
    client = get_mongodb_client()
    databases = [database for database in client.list_databases()]
    client.close()
    return databases


def drop_database(database_name: str):
    """Drop the selected database"""
    client = get_mongodb_client()
    logger.info(f'Dropping database "{database_name}"...')
    client.drop_database(database_name)
    client.close()


def copy_database(source_db_name: str, destination_db_name: str):
    """Copy an existing database"""
    client = get_mongodb_client()
    logger.info(f'Copying database "{source_db_name}" to "{destination_db_name}...')
    client.admin.command("copydb", fromdb=source_db_name, todb=destination_db_name)
    client.close()
