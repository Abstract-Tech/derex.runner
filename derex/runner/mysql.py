from derex.runner.compose_utils import run_compose
from derex.runner.docker import check_services
from derex.runner.docker import wait_for_service
from derex.runner.project import Project
from derex.runner.utils import abspath_from_egg
from MySQLdb.cursors import Cursor
from typing import Optional

import logging
import MySQLdb as mysqlclient


logger = logging.getLogger(__name__)


def wait_for_mysql(max_seconds: int = 20):
    """With a freshly created container mysql might need a bit of time to prime
    its files. This functions waits up to max_seconds seconds.
    """
    return wait_for_service("mysql", 'mysql -psecret -e "SHOW DATABASES"', max_seconds)


def get_mysql_client(
    user: str = "root", password: str = "secret", database: Optional[str] = "", **kwargs
) -> Cursor:
    """Return a cursor on the mysql server"""
    from derex.runner.docker import client as docker_client

    if not check_services(["mysql"]):
        raise RuntimeError(
            "Mysql service not found.\nMaybe you forgot to run\nddc-services up -d"
        )

    wait_for_mysql()
    container = docker_client.containers.get("mysql")
    mysql_host = container.attrs["NetworkSettings"]["Networks"]["derex"]["IPAddress"]

    connection = mysqlclient.connect(
        host=mysql_host, port=3306, user=user, passwd=password, db=database, **kwargs
    )
    return connection.cursor()


def list_databases():
    """List all existing databases"""
    client = get_mysql_client()
    client.execute("SHOW DATABASES;")
    databases = [database[0] for database in client.fetchall()]
    client.close()
    return databases


def create_database(database_name):
    """Create a database if doesn't exists"""
    client = get_mysql_client()
    logger.info(f'Creating database "{database_name}"...')
    client.execute(f"CREATE DATABASE IF NOT EXISTS {database_name}")
    client.close()


def drop_database(database_name):
    """Drop the selected database"""
    client = get_mysql_client()
    logger.info(f'Dropping database "{database_name}"...')
    client.execute(f"DROP DATABASE {database_name}")
    client.close()


def copy_database(source_db_name: str, destination_db_name: str):
    """
    Copy an existing mysql database. This actually involves exporting and importing back
    the database with a different name.
    """
    logger.info(f"Copying database {source_db_name} to {destination_db_name}")
    create_database(destination_db_name)
    run_compose(
        [
            "run",
            "--rm",
            "mysql",
            "sh",
            "-c",
            f"""set -ex
                mysqldump -h mysql -u root -psecret {source_db_name} --no-create-db |
                mysql -h mysql --user=root -psecret {destination_db_name}
            """,
        ]
    )


def reset_mysql_openedx(project: Project, dry_run: bool = False):
    """Run script from derex/openedx image to reset the mysql db.
    """
    create_database(project.mysql_db_name)
    restore_dump_path = abspath_from_egg(
        "derex.runner", "derex/runner/restore_dump.py.source"
    )
    assert (
        restore_dump_path
    ), "Could not find restore_dump.py in derex.runner distribution"
    run_compose(
        [
            "run",
            "--rm",
            "-v",
            f"{restore_dump_path}:/restore_dump.py",
            "lms",
            "python",
            "/restore_dump.py",
        ],
        project=project,
        dry_run=dry_run,
    )
