from derex.runner.constants import MYSQL_ROOT_USER
from derex.runner.ddc import run_ddc_project
from derex.runner.ddc import run_ddc_services
from derex.runner.docker_utils import client as docker_client
from derex.runner.docker_utils import wait_for_service
from derex.runner.project import Project
from derex.runner.secrets import DerexSecrets
from derex.runner.secrets import get_secret
from derex.runner.utils import abspath_from_egg
from functools import wraps
from typing import cast
from typing import List
from typing import Optional
from typing import Tuple

import logging
import pymysql


logger = logging.getLogger(__name__)
MYSQL_ROOT_PASSWORD = get_secret(DerexSecrets.mysql)


def wait_for_mysql(max_seconds: int = 20):
    """With a freshly created container mysql might need a bit of time to prime
    its files. This functions waits up to max_seconds seconds.
    """
    # We use "mysqladmin ping" here since it doesn't depend on authentication.
    # From mysqladmin docs:
    #
    #   Check whether the server is available. The return status from mysqladmin is 0
    #   if the server is running, 1 if it is not. This is 0 even in case of an error
    #   such as Access denied, because this means that the server is running but
    #   refused the connection, which is different from the server not running.
    return wait_for_service("mysql", "mysqladmin ping", max_seconds)


def ensure_mysql(func):
    """Decorator to raise an exception before running a function in case the MySQL
    server is not available.
    """

    @wraps(func)
    def inner(*args, **kwargs):
        try:
            wait_for_mysql(5)
            return func(*args, **kwargs)
        except TimeoutError:
            raise RuntimeError(
                "MySQL service not found.\nMaybe you forgot to run\nddc-services up -d"
            )

    return inner


@ensure_mysql
def get_system_mysql_client() -> pymysql.cursors.Cursor:
    container = docker_client.containers.get("mysql")
    mysql_host = container.attrs["NetworkSettings"]["Networks"]["derex"]["IPAddress"]
    return get_mysql_client(
        host=mysql_host, user=MYSQL_ROOT_USER, password=MYSQL_ROOT_PASSWORD
    )


@ensure_mysql
def get_project_mysql_client(project: Project) -> pymysql.cursors.Cursor:
    return get_mysql_client(
        host=project.mysql_db_host,
        user=project.mysql_db_user,
        password=project.mysql_db_password,
        database=project.mysql_db_name,
    )


@ensure_mysql
def get_mysql_client(
    host: str,
    user: str,
    password: str,
    port: Optional[int] = 3306,
    database: Optional[str] = None,
    **kwargs,
) -> pymysql.cursors.Cursor:
    """Return a cursor on the mysql server. If the connection object is needed
    it can be accessed from the cursor object:

    .. code-block:: python

        mysql_client = get_mysql_client()
        mysql_client.connection.autocommit(True)
    """
    connection = pymysql.connect(
        host=host, port=port, user=user, passwd=password, db=database, **kwargs
    )
    return connection.cursor()


def show_databases() -> List[Tuple[str, int, int]]:
    """List all existing databases together with some
    useful infos (number of tables, number of Django users).
    """
    client = get_system_mysql_client()
    try:
        databases_tuples = []
        client.execute("SHOW DATABASES;")
        query_result = cast(Tuple[Tuple[str]], client.fetchall())
        databases_names = [row[0] for row in query_result]
        for database_name in databases_names:
            client.execute(f"USE `{database_name}`")
            table_count = client.execute("SHOW TABLES;")
            try:
                client.execute("SELECT COUNT(*) FROM auth_user;")
                query_result = cast(Tuple[Tuple[str]], client.fetchall())
                django_users_count = int(query_result[0][0])
            except (
                pymysql.err.InternalError,
                pymysql.err.ProgrammingError,
                pymysql.err.OperationalError,
            ):
                django_users_count = 0
            databases_tuples.append((database_name, table_count, django_users_count))
    finally:
        client.connection.close()
    return databases_tuples


def list_users() -> Optional[Tuple[Tuple[str, str, str]]]:
    """List all mysql users."""
    client = get_system_mysql_client()
    client.execute("SELECT user, host, password FROM mysql.user;")
    users = cast(Tuple[Tuple[str, str, str]], client.fetchall())
    return users


def create_database(database_name: str):
    """Create a database if doesn't exists."""
    client = get_system_mysql_client()
    logger.info(f'Creating database "{database_name}"...')
    client.execute(f"CREATE DATABASE `{database_name}` CHARACTER SET utf8")
    logger.info(f'Successfully created database "{database_name}"')


def create_user(user: str, password: str, host: str):
    """Create a user if doesn't exists."""
    client = get_system_mysql_client()
    logger.info(f"Creating user '{user}'@'{host}'...")
    client.execute(f"CREATE USER '{user}'@'{host}' IDENTIFIED BY '{password}';")
    logger.info(f"Successfully created user '{user}'@'{host}'")


def drop_database(database_name: str):
    """Drops the selected database."""
    client = get_system_mysql_client()
    logger.info(f'Dropping database "{database_name}"...')
    client.execute(f"DROP DATABASE IF EXISTS `{database_name}`;")
    logger.info(f'Successfully dropped database "{database_name}"')


def drop_user(user: str, host: str):
    """Drops the selected user."""
    client = get_system_mysql_client()
    logger.info(f"Dropping user '{user}'@'{host}'...")
    client.execute(f"DROP USER '{user}'@'{host}';")
    logger.info(f"Successfully dropped user '{user}'@'{host}'")


@ensure_mysql
def execute_root_shell(command: Optional[str]):
    """Open a root shell on the mysql database. If a command is given
    it is executed."""
    compose_args = [
        "exec",
        "mysql",
        "mysql",
        "-u",
        MYSQL_ROOT_USER,
        f"-p{MYSQL_ROOT_PASSWORD}",
    ]
    if command:
        compose_args.insert(1, "-T")
        compose_args.extend(["-e", command])
    run_ddc_services(compose_args, exit_afterwards=True)


@ensure_mysql
def copy_database(source_db_name: str, destination_db_name: str):
    """Copy an existing MySQL database. This actually involves exporting and importing back
    the database with a different name."""
    create_database(destination_db_name)
    logger.info(f"Copying database {source_db_name} to {destination_db_name}")
    run_ddc_services(
        [
            "exec",
            "-T",
            "mysql",
            "sh",
            "-c",
            f"""set -ex
                mysqldump -u root -p{MYSQL_ROOT_PASSWORD} {source_db_name} --no-create-db |
                mysql --user=root -p{MYSQL_ROOT_PASSWORD} {destination_db_name}
            """,
        ]
    )
    logger.info(
        f"Successfully copied database {source_db_name} to {destination_db_name}"
    )


@ensure_mysql
def reset_mysql_openedx(project: Project, dry_run: bool = False):
    """Run script from derex/openedx image to reset the mysql db."""
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


@ensure_mysql
def reset_mysql_password(current_password: str):
    """Reset the mysql root user password."""
    logger.info(f'Resetting password for mysql user "{MYSQL_ROOT_USER}"')

    run_ddc_services(
        [
            "exec",
            "mysql",
            "mysql",
            "-u",
            MYSQL_ROOT_USER,
            f"-p{current_password}",
            "-e",
            f"""SET PASSWORD FOR '{MYSQL_ROOT_USER}'@'localhost' = PASSWORD('{MYSQL_ROOT_PASSWORD}');
            SET PASSWORD FOR '{MYSQL_ROOT_USER}'@'%' = PASSWORD('{MYSQL_ROOT_PASSWORD}');
            GRANT ALL PRIVILEGES ON *.* TO '{MYSQL_ROOT_USER}'@'%' WITH GRANT OPTION;
            FLUSH PRIVILEGES;""",
        ],
        exit_afterwards=True,
    )
