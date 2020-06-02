from derex.runner.docker_utils import check_services
from derex.runner.docker_utils import client as docker_client
from derex.runner.docker_utils import wait_for_service
from functools import wraps
from pymongo import MongoClient
from typing import cast
from typing import List

import logging


logger = logging.getLogger(__name__)


def wait_for_mongodb(max_seconds: int = 20):
    """With a freshly created container mongodb might need a bit of time to prime
    its files. This functions waits up to max_seconds seconds.
    """
    return wait_for_service("mongodb", "mongo", max_seconds)


if not check_services(["mongodb"]):
    MONGODB_CLIENT = None
else:
    wait_for_mongodb()
    container = docker_client.containers.get("mongodb")
    mongo_address = container.attrs["NetworkSettings"]["Networks"]["derex"]["IPAddress"]
    MONGODB_CLIENT = MongoClient(f"mongodb://{mongo_address}:27017/")


def ensure_mongodb(func):
    """Decorator to raise an exception before running a function in case the mongodb
    server is not available.
    """

    @wraps(func)
    def inner(*args, **kwargs):
        if MONGODB_CLIENT is None:
            raise RuntimeError(
                "MongoDB service not found.\nMaybe you forgot to run\nddc-services up -d"
            )
        return func(*args, **kwargs)

    return inner


@ensure_mongodb
def list_databases() -> List[dict]:
    """List all existing databases"""
    logger.info("Listing MongoDB databases...")
    databases = [
        database for database in cast(MongoClient, MONGODB_CLIENT).list_databases()
    ]
    return databases


@ensure_mongodb
def drop_database(database_name: str):
    """Drop the selected database"""
    logger.info(f'Dropping database "{database_name}"...')
    cast(MongoClient, MONGODB_CLIENT).drop_database(database_name)


@ensure_mongodb
def copy_database(source_db_name: str, destination_db_name: str):
    """Copy an existing database"""
    logger.info(f'Copying database "{source_db_name}" to "{destination_db_name}...')
    cast(MongoClient, MONGODB_CLIENT).admin.command(
        "copydb", fromdb=source_db_name, todb=destination_db_name
    )
