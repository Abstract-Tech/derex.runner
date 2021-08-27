from derex.runner.ddc import run_ddc
from derex.runner.docker_utils import check_containers
from derex.runner.docker_utils import client as docker_client
from derex.runner.docker_utils import wait_for_container
from derex.runner.project import Project
from functools import wraps
from pymongo import MongoClient
from typing import cast
from typing import List
from typing import Optional

import logging
import time
import urllib.parse


logger = logging.getLogger(__name__)


def get_mongodb_client(project: Project):
    wait_for_container(project.mongodb_host)
    container = docker_client.containers.get(project.mongodb_host)
    mongo_address = container.attrs["NetworkSettings"]["Networks"]["derex"]["IPAddress"]
    user = urllib.parse.quote_plus(project.mongodb_user)
    password = urllib.parse.quote_plus(project.mongodb_password)
    return MongoClient(
        f"mongodb://{user}:{password}@{mongo_address}:27017/", authSource="admin"
    )


def ensure_mongodb(func):
    """Decorator to raise an exception before running a function in case the mongodb
    server is not available.
    """

    @wraps(func)
    def inner(*args, **kwargs):
        project = Project()
        wait_for_container(project.mongodb_host, 0)
        return func(*args, **kwargs)

    return inner


@ensure_mongodb
def execute_root_shell(project: Project, command: Optional[str]):
    """Open a root shell on the MongoDB database. If a command is given
    it is executed."""
    compose_args = [
        "exec",
        project.mongodb_host,
        "mongo",
        "--authenticationDatabase",
        "admin",
        "-u",
        project.mongodb_user,
        f"-p{project.mongodb_password}",
    ]
    if command:
        compose_args.insert(1, "-T")
        compose_args.extend(["--eval", command])
    run_ddc(compose_args, "services", exit_afterwards=True)


@ensure_mongodb
def list_databases(project: Project) -> List[dict]:
    """List all existing databases"""
    logger.info("Listing MongoDB databases...")
    databases = [
        database
        for database in cast(MongoClient, get_mongodb_client(project)).list_databases()
    ]
    return databases


@ensure_mongodb
def list_users(project: Project) -> List[dict]:
    """List all existing users"""
    logger.info("Listing MongoDB users...")
    return (
        cast(MongoClient, get_mongodb_client(project))
        .admin.command("usersInfo")
        .get("users")
    )


@ensure_mongodb
def create_user(project: Project, user: str, password: str, roles: List[str]):
    """Create a new user"""
    logger.info(f'Creating user "{user}"...')
    cast(MongoClient, get_mongodb_client(project)).admin.command(
        "createUser", user, pwd=password, roles=roles
    )


@ensure_mongodb
def drop_database(project: Project, database_name: str):
    """Drop the selected database"""
    logger.info(f'Dropping database "{database_name}"...')
    cast(MongoClient, get_mongodb_client(project)).drop_database(database_name)


@ensure_mongodb
def copy_database(project: Project, source_db_name: str, destination_db_name: str):
    """Copy an existing database"""
    logger.info(f'Copying database "{source_db_name}" to "{destination_db_name}...')
    cast(MongoClient, get_mongodb_client(project)).admin.command(
        "copydb", fromdb=source_db_name, todb=destination_db_name
    )


@ensure_mongodb
def create_root_user(project: Project):
    """Create the root user"""
    create_user(project.mongodb_user, project.mongodb_password, ["root"])


@ensure_mongodb
def reset_mongodb_password(project: Project, current_password: str = None):
    """Reset the mongodb root user password"""
    mongo_command_args = [
        "mongo",
        "--authenticationDatabase",
        "admin",
        "admin",
        "--eval",
        f'"db.changeUserPassword(\\"{project.mongodb_user}\\",'
        f'\\"{project.mongodb_password}\\");"',
    ]
    if current_password:
        mongo_command_args.extend(["-u", project.mongodb_user, f"-p{current_password}"])

    mongo_command = " ".join(mongo_command_args)
    compose_args = [
        "exec",
        "-T",
        project.mongodb_host,
        "bash",
        "-c",
        f"{mongo_command}",
    ]

    run_ddc(compose_args, "services", exit_afterwards=True)
    return 0


def run_mongodb_upgrade(
    project: Project,
    data_volume: str,
    upgrade_volume: str,
    from_version: str,
    to_version: str,
):
    if check_containers(project.mongodb_host):
        logger.info(f"Stopping running mongodb service {project.mongodb_host}")
        run_ddc(["stop", project.mongodb_host], "services")

    version_map = {
        "mongodb34": "mongo:3.4.24",
        "mongodb36": "mongo:3.6.23",
        "mongodb40": "mongo:4.0.26",
        "mongodb42": "mongo:4.2.15",
        "mongodb44": "mongo:4.4.8",
    }
    logger.info(f'Copying data volume "{data_volume}" to "{upgrade_volume}"')
    output = docker_client.containers.run(
        "alpine",
        'sh -c "cd /source; cp -av . /destination"',
        auto_remove=True,
        volumes={
            data_volume: {"bind": "/source", "mode": "ro"},
            upgrade_volume: {"bind": "/destination", "mode": "rw"},
        },
    )
    logger.debug(output)
    logger.info(
        f'Running mongodb upgrade for volume "{upgrade_volume}" from version {from_version} to version {to_version}'
    )
    container = docker_client.containers.run(
        version_map[f"mongodb{to_version.replace('.', '')}"],
        "mongod",
        auto_remove=True,
        detach=True,
        volumes={upgrade_volume: {"bind": "/data/db", "mode": "rw"}},
    )
    # We are being lazy here.
    # We should probably implement an healthcheck in the container and wait for it
    # to become healthy. Or abort the operation if a timeout is reached.
    time.sleep(5)
    try:
        exit_code, output = container.exec_run(
            f"mongo --eval 'db.adminCommand({{setFeatureCompatibilityVersion:\"{to_version}\"}})'"
        )
        output = output.decode("utf-8")
        if exit_code or "errmsg" in output:
            raise Exception(output)
    finally:
        container.stop()
    return 0
