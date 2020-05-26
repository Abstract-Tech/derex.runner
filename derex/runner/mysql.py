from derex.runner.ddc import run_ddc_project
from derex.runner.ddc import run_ddc_services
from derex.runner.docker import check_services
from derex.runner.docker import client as docker_client
from derex.runner.docker import wait_for_service
from derex.runner.project import Project
from derex.runner.utils import abspath_from_egg
from typing import cast
from typing import List
from typing import Optional
from typing import Tuple

import logging
import pymysql


logger = logging.getLogger(__name__)


def wait_for_mysql(max_seconds: int = 20):
    """With a freshly created container mysql might need a bit of time to prime
    its files. This functions waits up to max_seconds seconds.
    """
    return wait_for_service("mysql", 'mysql -psecret -e "SHOW DATABASES"', max_seconds)


def get_mysql_client(
    user: str = "root", password: str = "secret", database: Optional[str] = "", **kwargs
) -> pymysql.cursors.Cursor:
    """Return a cursor on the mysql server. If the connection object is needed
    it can be accessed from the cursor object:

    .. code-block:: python

        mysql_client = get_mysql_client()
        mysql_client.connection.autocommit(True)
    """

    if not check_services(["mysql"]):
        raise RuntimeError(
            "Mysql service not found.\nMaybe you forgot to run\nddc-services up -d"
        )

    wait_for_mysql()
    container = docker_client.containers.get("mysql")
    mysql_host = container.attrs["NetworkSettings"]["Networks"]["derex"]["IPAddress"]

    connection = pymysql.connect(
        host=mysql_host, port=3306, user=user, passwd=password, db=database, **kwargs
    )
    return connection.cursor()


def show_databases() -> List[Tuple[str, int, int]]:
    """List all existing databases together with some
    useful infos (number of tables, number of Django users).
    """
    client = get_mysql_client()
    try:
        databases_tuples = []
        client.execute("SHOW DATABASES;")
        query_result = cast(Tuple[Tuple[str]], client.fetchall())
        databases_names = [row[0] for row in query_result]
        for database_name in databases_names:
            client.execute(f"USE {database_name}")
            table_count = client.execute("SHOW TABLES;")
            try:
                client.execute("SELECT COUNT(*) FROM auth_user;")
                query_result = cast(Tuple[Tuple[str]], client.fetchall())
                django_users_count = int(query_result[0][0])
            except (pymysql.err.InternalError, pymysql.err.ProgrammingError):
                django_users_count = 0
            databases_tuples.append((database_name, table_count, django_users_count))
    finally:
        client.connection.close()
    return databases_tuples


def show_users() -> Optional[Tuple[Tuple[str, str, str]]]:
    """List all mysql users.
    """
    client = get_mysql_client()
    client.execute("SELECT user, host, password FROM mysql.user;")
    users = cast(Tuple[Tuple[str, str, str]], client.fetchall())
    return users


def create_database(database_name: str):
    """Create a database if doesn't exists"""
    client = get_mysql_client()
    logger.info(f'Creating database "{database_name}"...')
    client.execute(f"CREATE DATABASE `{database_name}` CHARACTER SET utf8")
    logger.info(f'Successfully created database "{database_name}"')


def create_user(user: str, password: str, host: str):
    """Create a user if doesn't exists"""
    client = get_mysql_client()
    logger.info(f"Creating user '{user}'@'{host}'...")
    client.execute(f"CREATE USER '{user}'@'{host}' IDENTIFIED BY '{password}';")
    logger.info(f"Successfully created user '{user}'@'{host}'")


def drop_database(database_name: str):
    """Drops the selected database"""
    client = get_mysql_client()
    logger.info(f'Dropping database "{database_name}"...')
    client.execute(f"DROP DATABASE IF EXISTS `{database_name}`;")
    logger.info(f'Successfully dropped database "{database_name}"')


def drop_user(user: str, host: str):
    """Drops the selected user"""
    client = get_mysql_client()
    logger.info(f"Dropping user '{user}'@'{host}'...")
    client.execute(f"DROP USER '{user}'@'{host}';")
    logger.info(f"Successfully dropped user '{user}'@'{host}'")


def copy_database(source_db_name: str, destination_db_name: str):
    """
    Copy an existing MySQL database. This actually involves exporting and importing back
    the database with a different name.
    """
    create_database(destination_db_name)
    logger.info(f"Copying database {source_db_name} to {destination_db_name}")
    run_ddc_services(
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
    logger.info(
        f"Successfully copied database {source_db_name} to {destination_db_name}"
    )


def reset_mysql_openedx(project: Project, dry_run: bool = False):
    """Run script from derex/openedx image to reset the mysql db.
    """
    restore_dump_path = abspath_from_egg(
        "derex.runner", "derex/runner/restore_dump.py.source"
    )
    assert (
        restore_dump_path
    ), "Could not find restore_dump.py in derex.runner distribution"
    run_ddc_project(
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
