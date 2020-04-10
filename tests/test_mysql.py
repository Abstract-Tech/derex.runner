from .conftest import assert_result_ok
from click.testing import CliRunner
from itertools import repeat
from pathlib import Path
from time import sleep
from types import SimpleNamespace

import pytest
import uuid


MINIMAL_PROJ = Path(__file__).with_name("fixtures") / "minimal"
runner = CliRunner(mix_stderr=False)


# TODO: if this test fails after test data have been created
# it won't be cleaned up
def test_derex_mysql(start_services):
    """Test the `derex mysql copy` cli command """
    from derex.runner.cli import create_mysql, drop_mysql, copy_mysql
    from derex.runner.mysql import get_mysql_client
    from derex.runner.mysql import list_databases

    test_db = uuid.uuid4().hex[:20]
    test_db_copy = uuid.uuid4().hex[:20]
    random_value = uuid.uuid4().hex[:20]

    runner.invoke(create_mysql, test_db)
    sleep(1)
    assert test_db in list_databases()

    mysql_client = get_mysql_client()
    mysql_client.connection.autocommit(True)
    mysql_client.execute(
        f"""
        USE {test_db};
        CREATE TABLE test (field VARCHAR(255) NOT NULL);
        INSERT INTO test (field) VALUES ('{random_value}');
    """
    )
    runner.invoke(copy_mysql, [test_db, test_db_copy], input="y")
    sleep(1)
    mysql_client.execute(f"USE {test_db_copy};")
    mysql_client.execute("SELECT * from test;")
    assert mysql_client.fetchone()[0] == random_value

    runner.invoke(drop_mysql, test_db, input="y")
    runner.invoke(drop_mysql, test_db_copy, input="y")

    assert test_db not in list_databases()
    assert test_db_copy not in list_databases()


@pytest.mark.slowtest
def test_derex_reset_mysql(sys_argv, mocker, workdir_copy):
    """Test the open edx ironwood docker compose shortcut."""
    from derex.runner.cli import reset_mysql
    from derex.runner.ddc import ddc_services

    mocker.patch("derex.runner.ddc.check_services", return_value=True)
    client = mocker.patch("derex.runner.docker.client")
    client.containers.get.return_value.exec_run.side_effect = [
        SimpleNamespace(exit_code=-1)
    ] + list(repeat(SimpleNamespace(exit_code=0), 10))

    with sys_argv(["ddc-services", "up", "-d"]):
        ddc_services()
    with workdir_copy(MINIMAL_PROJ):
        result = runner.invoke(reset_mysql)
    assert_result_ok(result)
    assert result.exit_code == 0
