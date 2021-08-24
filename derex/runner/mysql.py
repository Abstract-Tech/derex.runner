from derex.runner import abspath_from_egg
from derex.runner.ddc import run_ddc
from derex.runner.docker_utils import client as docker_client
from derex.runner.docker_utils import wait_for_container
from derex.runner.project import Project
from functools import wraps
from typing import cast
from typing import List
from typing import Optional
from typing import Tuple

import logging
import pymysql


logger = logging.getLogger(__name__)


def ensure_mysql(func):
    """Decorator to raise an exception before running a function in case the MySQL
    server is not available.
    """

    @wraps(func)
    def inner(*args, **kwargs):
        wait_for_container(Project().mysql_host)
        return func(*args, **kwargs)

    return inner


@ensure_mysql
def get_project_mysql_client(project: Project) -> pymysql.cursors.Cursor:
    container = docker_client.containers.get(project.mysql_host)
    mysql_host_ip = container.attrs["NetworkSettings"]["Networks"]["derex"]["IPAddress"]
    return get_mysql_client(
        host=mysql_host_ip,
        user=project.mysql_user,
        password=project.mysql_password,
    )


@ensure_mysql
def get_mysql_client(
    host: str,
    user: str,
    password: str,
    port: int = 3306,
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


def show_databases(project: Project) -> List[Tuple[str, int, int]]:
    """List all existing databases together with some
    useful infos (number of tables, number of Django users).
    """
    client = get_project_mysql_client(project)
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


def list_users(project: Project) -> Optional[Tuple[Tuple[str, str, str]]]:
    """List all mysql users."""
    client = get_project_mysql_client(project)
    client.execute("SELECT user, host, password FROM mysql.user;")
    users = cast(Tuple[Tuple[str, str, str]], client.fetchall())
    return users


def create_database(project: Project, database_name: str):
    """Create a database if doesn't exists."""
    client = get_project_mysql_client(project)
    logger.info(f'Creating database "{database_name}"...')
    client.execute(f"CREATE DATABASE `{database_name}` CHARACTER SET utf8")
    logger.info(f'Successfully created database "{database_name}"')


def create_user(project: Project, user: str, password: str, host: str):
    """Create a user if doesn't exists."""
    client = get_project_mysql_client(project)
    logger.info(f"Creating user '{user}'@'{host}'...")
    client.execute(f"CREATE USER '{user}'@'{host}' IDENTIFIED BY '{password}';")
    logger.info(f"Successfully created user '{user}'@'{host}'")


def drop_database(project: Project, database_name: str):
    """Drops the selected database."""
    client = get_project_mysql_client(project)
    logger.info(f'Dropping database "{database_name}"...')
    client.execute(f"DROP DATABASE IF EXISTS `{database_name}`;")
    logger.info(f'Successfully dropped database "{database_name}"')


def drop_user(project: Project, user: str, host: str):
    """Drops the selected user."""
    client = get_project_mysql_client(project)
    logger.info(f"Dropping user '{user}'@'{host}'...")
    client.execute(f"DROP USER '{user}'@'{host}';")
    logger.info(f"Successfully dropped user '{user}'@'{host}'")


@ensure_mysql
def execute_root_shell(project: Project, command: Optional[str]):
    """Open a root shell on the mysql database. If a command is given
    it is executed."""
    compose_args = [
        "exec",
        project.mysql_host,
        "mysql",
        "-u",
        project.mysql_user,
        f"-p{project.mysql_password}",
    ]
    if command:
        compose_args.insert(1, "-T")
        compose_args.extend(["-e", command])
    run_ddc(compose_args, "services", exit_afterwards=True)


@ensure_mysql
def copy_database(project: Project, source_db_name: str, destination_db_name: str):
    """Copy an existing MySQL database. This actually involves exporting and importing back
    the database with a different name."""
    create_database(project, destination_db_name)
    logger.info(f"Copying database {source_db_name} to {destination_db_name}")
    run_ddc(
        [
            "exec",
            "-T",
            project.mysql_host,
            "sh",
            "-c",
            f"""set -ex
                mysqldump -u root -p{project.mysql_password} {source_db_name} --no-create-db |
                mysql --user=root -p{project.mysql_password} {destination_db_name}
            """,
        ],
        "services",
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
    run_ddc(
        [
            "run",
            "--rm",
            "-v",
            f"{restore_dump_path}:/restore_dump.py",
            "lms",
            "python",
            "/restore_dump.py",
        ],
        "project",
        project,
        dry_run=dry_run,
    )


@ensure_mysql
def reset_mysql_password(project: Project, current_password: str):
    """Reset the mysql root user password."""
    logger.info(f'Resetting password for mysql user "{project.mysql_user}"')

    run_ddc(
        [
            "exec",
            project.mysql_host,
            "mysql",
            "-u",
            project.mysql_user,
            f"-p{current_password}",
            "-e",
            f"""SET PASSWORD FOR '{project.mysql_user}'@'localhost' = PASSWORD('{project.mysql_password}');
            SET PASSWORD FOR '{project.mysql_user}'@'%' = PASSWORD('{project.mysql_password}');
            GRANT ALL PRIVILEGES ON *.* TO '{project.mysql_user}'@'%' WITH GRANT OPTION;
            FLUSH PRIVILEGES;""",
        ],
        "services",
        exit_afterwards=True,
    )
