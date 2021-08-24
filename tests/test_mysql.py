from .conftest import assert_result_ok
from .conftest import DEREX_TEST_USER
from click.testing import CliRunner
from derex.runner.mysql import get_project_mysql_client
from derex.runner.mysql import show_databases
from derex.runner.project import Project
from itertools import repeat
from types import SimpleNamespace

import pytest
import uuid


runner = CliRunner(mix_stderr=False)


# @pytest.fixture(autouse=True)
# def cleanup_mysql(minimal_project):
#     """Ensure no test database or user is left behind"""
#     yield

#     with minimal_project:
#         project = Project()
#         mysql_client = get_project_mysql_client(project)
#         mysql_client.execute("SHOW DATABASES;")
#         for database in mysql_client.fetchall():
#             if "derex_test_db_" in database[0]:
#                 mysql_client.execute(f"DROP DATABASE {database[0]};")

#         mysql_client.execute("SELECT user,host from mysql.user;")
#         for user in mysql_client.fetchall():
#             if DEREX_TEST_USER in user[0]:
#                 mysql_client.execute(f"DROP USER '{user[0]}'@'{user[1]}'")

#         mysql_client.connection.close()


@pytest.mark.slowtest
def test_derex_mysql(minimal_project):
    """Test the `derex mysql copy` cli command"""
    from derex.runner.cli.mysql import copy_database_cmd
    from derex.runner.cli.mysql import create_database_cmd
    from derex.runner.cli.mysql import drop_database_cmd

    with minimal_project:
        project = Project()

        test_db_name = f"derex_test_db_{uuid.uuid4().hex[:20]}"
        test_db_copy_name = f"derex_test_db_copy_{uuid.uuid4().hex[:20]}"
        random_value = uuid.uuid4().hex[:20]

        runner.invoke(create_database_cmd, test_db_name)
        assert test_db_name in [database[0] for database in show_databases(project)]

        mysql_client = get_project_mysql_client(project=project)
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

        assert test_db_name not in [database[0] for database in show_databases(project)]
        assert test_db_copy_name not in [
            database[0] for database in show_databases(project)
        ]


@pytest.mark.slowtest
def test_derex_mysql_reset(mocker, minimal_project):
    """Test the `derex mysql reset` cli command"""
    from derex.runner.cli.mysql import reset_mysql_cmd

    mocker.patch("derex.runner.ddc.wait_for_container", return_value=0)
    client = mocker.patch("derex.runner.docker_utils.client")
    client.containers.get.return_value.exec_run.side_effect = [
        SimpleNamespace(exit_code=-1)
    ] + list(repeat(SimpleNamespace(exit_code=0), 10))

    with minimal_project:
        result = runner.invoke(reset_mysql_cmd, input="y")
    assert_result_ok(result)
    assert result.exit_code == 0


@pytest.mark.slowtest
def test_derex_mysql_reset_password(mocker, minimal_project):
    """Test the `derex mysql copy` cli command"""
    from derex.runner.cli.mysql import create_user_cmd
    from derex.runner.cli.mysql import reset_mysql_password_cmd
    from derex.runner.cli.mysql import shell

    with minimal_project:
        for host in ["localhost", "%"]:
            runner.invoke(create_user_cmd, [DEREX_TEST_USER, "secret", host])
            result = runner.invoke(
                shell,
                [
                    f"GRANT ALL ON *.* TO '{DEREX_TEST_USER}'@'{host}' WITH GRANT OPTION;"
                    "FLUSH PRIVILEGES;"
                ],
            )

        mocker.patch("derex.runner.project.MYSQL_ROOT_USER", new=DEREX_TEST_USER)

        # This is expected to fail since we set a custom password for the root user
        result = runner.invoke(shell, ["SHOW DATABASES;"])
        assert result.exit_code == 1

        # We reset the password to the derex generated one
        assert_result_ok(runner.invoke(reset_mysql_password_cmd, ["secret"], input="y"))

        # Now this should be
        assert_result_ok(result=runner.invoke(shell, ["SHOW DATABASES;"]))
