from .conftest import assert_result_ok
from click.testing import CliRunner
from derex.runner.mysql import get_mysql_client
from derex.runner.mysql import show_databases
from itertools import repeat
from pathlib import Path
from types import SimpleNamespace

import pytest
import uuid


MINIMAL_PROJ = Path(__file__).parent.with_name("examples") / "minimal"
runner = CliRunner(mix_stderr=False)


@pytest.fixture(scope="session")
def start_mysql(sys_argv):
    """Start the mysql container on setup,
    stop and remove it on teardown.
    """
    from derex.runner.ddc import ddc_services

    with sys_argv(["ddc-services", "up", "-d", "mysql"]):
        ddc_services()


@pytest.fixture(autouse=True)
def cleanup_mysql(start_mysql):
    """Ensure no test database is left behind"""
    yield

    client = get_mysql_client()
    client.execute("SHOW DATABASES;")
    to_delete = []
    for database in client.fetchall():
        if "derex_test_db_" in database[0]:
            to_delete.append(database)

    for database in to_delete:
        client.execute(f"DROP DATABASE {database[0]};")

    client.connection.close()


def test_derex_mysql(start_mysql):
    """Test the `derex mysql copy` cli command """
    from derex.runner.cli.mysql import copy_database_cmd
    from derex.runner.cli.mysql import create_database_cmd
    from derex.runner.cli.mysql import drop_database_cmd

    test_db_name = f"derex_test_db_{uuid.uuid4().hex[:20]}"
    test_db_copy_name = f"derex_test_db_copy_{uuid.uuid4().hex[:20]}"
    random_value = uuid.uuid4().hex[:20]

    runner.invoke(create_database_cmd, test_db_name)
    assert test_db_name in [database[0] for database in show_databases()]

    mysql_client = get_mysql_client()
    mysql_client.connection.autocommit(True)
    mysql_client.execute(f"USE {test_db_name};")
    mysql_client.execute("CREATE TABLE test (field VARCHAR(255) NOT NULL);")
    mysql_client.execute(f"INSERT INTO test (field) VALUES ('{random_value}');")

    runner.invoke(copy_database_cmd, [test_db_name, test_db_copy_name], input="y")
    mysql_client.execute(f"USE {test_db_copy_name};")
    mysql_client.execute("SELECT * from test;")
    assert mysql_client.fetchone()[0] == random_value

    runner.invoke(drop_database_cmd, test_db_name, input="y")
    runner.invoke(drop_database_cmd, test_db_copy_name, input="y")

    assert test_db_name not in [database[0] for database in show_databases()]
    assert test_db_copy_name not in [database[0] for database in show_databases()]


def test_derex_reset_mysql(sys_argv, mocker, workdir_copy):
    """Test the open edx ironwood docker compose shortcut."""
    from derex.runner.cli.mysql import reset_mysql_cmd
    from derex.runner.ddc import ddc_services

    mocker.patch("derex.runner.ddc.check_services", return_value=True)
    client = mocker.patch("derex.runner.docker.client")
    client.containers.get.return_value.exec_run.side_effect = [
        SimpleNamespace(exit_code=-1)
    ] + list(repeat(SimpleNamespace(exit_code=0), 10))

    with sys_argv(["ddc-services", "up", "-d"]):
        ddc_services()
    with workdir_copy(MINIMAL_PROJ):
        result = runner.invoke(reset_mysql_cmd, input="y")
    assert_result_ok(result)
    assert result.exit_code == 0
