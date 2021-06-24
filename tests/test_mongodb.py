from .conftest import assert_result_ok
from .conftest import DEREX_TEST_USER
from click.testing import CliRunner
from derex.runner.ddc import ddc_services
from importlib import reload

import pytest
import uuid


runner = CliRunner(mix_stderr=False)


@pytest.fixture(scope="session")
def start_mongodb(sys_argv):
    """Ensure the mongodb service is up"""
    with sys_argv(["ddc-services", "up", "-d", "mongodb"]):
        ddc_services()


@pytest.fixture(autouse=True)
def cleanup_mongodb(start_mongodb):
    """Ensure no test database is left behind"""
    from derex.runner.mongodb import MONGODB_CLIENT

    yield

    for database_name in [
        database["name"]
        for database in MONGODB_CLIENT.list_databases()
        if "derex_test_db_" in database["name"]
    ]:
        MONGODB_CLIENT.drop_database(database_name)

    for user in MONGODB_CLIENT.admin.command("usersInfo").get("users"):
        if DEREX_TEST_USER in user["user"]:
            MONGODB_CLIENT.admin.command("dropUser", DEREX_TEST_USER)


def test_derex_mongodb(start_mongodb):
    from derex.runner.cli.mongodb import copy_mongodb
    from derex.runner.cli.mongodb import drop_mongodb
    from derex.runner.mongodb import list_databases

    import derex.runner.mongodb

    reload(derex.runner.mongodb)
    MONGODB_CLIENT = derex.runner.mongodb.MONGODB_CLIENT

    test_db_name = f"derex_test_db_{uuid.uuid4().hex[:20]}"
    test_db_copy_name = f"derex_test_db_copy_{uuid.uuid4().hex[:20]}"
    random_value = uuid.uuid4().hex[:20]
    test_data = {"data": random_value}

    MONGODB_CLIENT[test_db_name]["test_collection"].insert_one(test_data)
    assert test_db_name in [database["name"] for database in list_databases()]

    runner.invoke(copy_mongodb, f"{test_db_name} {test_db_copy_name}", input="y")
    assert test_db_copy_name in [database["name"] for database in list_databases()]
    assert MONGODB_CLIENT[test_db_copy_name]["test_collection"].find_one(test_data)

    runner.invoke(drop_mongodb, test_db_name, input="y")
    runner.invoke(drop_mongodb, test_db_copy_name, input="y")
    assert test_db_name not in [database["name"] for database in list_databases()]
    assert test_db_copy_name not in [database["name"] for database in list_databases()]


def test_derex_mongodb_reset_password(mocker, start_mongodb):
    from derex.runner.cli.mongodb import create_user_cmd
    from derex.runner.cli.mongodb import reset_mongodb_password_cmd
    from derex.runner.cli.mongodb import shell

    assert_result_ok(
        runner.invoke(create_user_cmd, [DEREX_TEST_USER, "secret", "--role=root"])
    )
    mocker.patch("derex.runner.mongodb.MONGODB_ROOT_USER", new=DEREX_TEST_USER)

    # This is expected to fail since we set a custom password for the root user
    result = runner.invoke(shell)
    assert result.exit_code == 1

    # We reset the password to the derex generated one
    assert_result_ok(runner.invoke(reset_mongodb_password_cmd, ["secret"], input="y"))

    # If the password is still not resetted to the value of the derex generated password
    # but still set to "secret" the next test will fail
    assert_result_ok(runner.invoke(shell))
