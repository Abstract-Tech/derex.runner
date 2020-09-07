from derex.runner.constants import MONGODB_ROOT_USER
from derex.runner.ddc import run_ddc_services
from derex.runner.docker_utils import check_services
from derex.runner.docker_utils import client as docker_client
from derex.runner.docker_utils import wait_for_service
from derex.runner.secrets import DerexSecrets
from derex.runner.secrets import get_secret
from functools import wraps
from pymongo import MongoClient
from typing import cast
from typing import List
from typing import Optional

import logging
import urllib.parse


logger = logging.getLogger(__name__)
MONGODB_ROOT_PASSWORD = get_secret(DerexSecrets.mongodb)


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
    user = urllib.parse.quote_plus(MONGODB_ROOT_USER)
    password = urllib.parse.quote_plus(MONGODB_ROOT_PASSWORD)
    MONGODB_CLIENT = MongoClient(
        f"mongodb://{user}:{password}@{mongo_address}:27017/", authSource="admin"
    )


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


def execute_root_shell(command: Optional[str]):
    """Open a root shell on the MongoDB database. If a command is given
    it is executed."""
    args = [
        "run",
        "--rm",
        "mongodb",
        "mongo",
        "--host",
        "mongodb",
        "--authenticationDatabase",
        "admin",
        "-u",
        MONGODB_ROOT_USER,
        f"-p{MONGODB_ROOT_PASSWORD}",
    ]
    if command:
        args.extend(["--eval", command])
    run_ddc_services(args)


@ensure_mongodb
def list_databases() -> List[dict]:
    """List all existing databases"""
    logger.info("Listing MongoDB databases...")
    databases = [
        database for database in cast(MongoClient, MONGODB_CLIENT).list_databases()
    ]
    return databases


@ensure_mongodb
def list_users() -> List[dict]:
    """List all existing users"""
    logger.info("Listing MongoDB users...")
    return cast(MongoClient, MONGODB_CLIENT).admin.command("usersInfo").get("users")


@ensure_mongodb
def create_user(user: str, password: str, roles: List[str]):
    """Create a new user"""
    logger.info(f'Creating user "{user}"...')
    cast(MongoClient, MONGODB_CLIENT).admin.command(
        "createUser", user, pwd=password, roles=roles
    )


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


@ensure_mongodb
def create_root_user():
    """Create the root user"""
    create_user(MONGODB_ROOT_USER, MONGODB_ROOT_PASSWORD, ["root"])


@ensure_mongodb
def reset_mongodb_password(current_password: str = None):
    """Reset the mongodb root user password"""
    mongo_command_args = [
        "mongo",
        "--host",
        "mongodb",
        "--authenticationDatabase",
        "admin",
        "admin",
        "--eval",
        f'"db.changeUserPassword(\\"{MONGODB_ROOT_USER}\\",'
        f'\\"{MONGODB_ROOT_PASSWORD}\\");"',
    ]
    if current_password:
        mongo_command_args.extend(["-u", MONGODB_ROOT_USER, f"-p{current_password}"])

    mongo_command = " ".join(mongo_command_args)
    args = ["run", "--rm", "mongodb", "bash", "-c", f"{mongo_command}"]

    run_ddc_services(args)
    return 0
