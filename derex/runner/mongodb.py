from derex.runner.docker import check_services
from derex.runner.docker import client as docker_client
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


if not check_services(["mongodb"]):
    raise RuntimeError(
        "MongoDB service not found.\nMaybe you forgot to run\nddc-services up -d"
    )
wait_for_mongodb()
container = docker_client.containers.get("mongodb")
mongo_address = container.attrs["NetworkSettings"]["Networks"]["derex"]["IPAddress"]
mongodb_client = MongoClient(f"mongodb://{mongo_address}:27017/")


def list_databases() -> List[dict]:
    """List all existing databases"""
    logger.info("Listing MongoDB databases...")
    databases = [database for database in mongodb_client.list_databases()]
    return databases


def drop_database(database_name: str):
    """Drop the selected database"""
    logger.info(f'Dropping database "{database_name}"...')
    mongodb_client.drop_database(database_name)


def copy_database(source_db_name: str, destination_db_name: str):
    """Copy an existing database"""
    logger.info(f'Copying database "{source_db_name}" to "{destination_db_name}...')
    mongodb_client.admin.command(
        "copydb", fromdb=source_db_name, todb=destination_db_name
    )
