from click.testing import CliRunner
from derex.runner.cli_modules.mongodb import copy_mongodb
from derex.runner.cli_modules.mongodb import drop_mongodb
from derex.runner.ddc import ddc_services
from derex.runner.mongodb import list_databases
from derex.runner.mongodb import mongodb_client

import pytest
import uuid


runner = CliRunner(mix_stderr=False)


@pytest.fixture(scope="session")
def start_mongodb(sys_argv):
    """Start the mongodb container on setup,
    stop and remove it on teardown.
    """
    with sys_argv(["ddc-services", "up", "-d", "mongodb"]):
        ddc_services()


@pytest.fixture(autouse=True)
def cleanup_mongodb(start_mongodb):
    """Ensure no test database is left behind"""
    yield

    for database_name in [
        database
        for database in mongodb_client.list_databases()
        if "derex_test_db_" in database["name"]
    ]:
        mongodb_client.drop_database(database_name)


def test_derex_mongodb(start_mongodb):
    """Test the `derex mysql copy` cli command """
    test_db_name = f"derex_test_db_{uuid.uuid4().hex[:20]}"
    test_db_copy_name = f"derex_test_db_copy_{uuid.uuid4().hex[:20]}"
    random_value = uuid.uuid4().hex[:20]
    test_data = {"data": random_value}

    mongodb_client[test_db_name]["test_collection"].insert_one(test_data)
    assert test_db_name in [database["name"] for database in list_databases()]

    runner.invoke(copy_mongodb, f"{test_db_name} {test_db_copy_name}", input="y")
    assert test_db_copy_name in [database["name"] for database in list_databases()]
    assert mongodb_client[test_db_copy_name]["test_collection"].find_one(test_data)

    runner.invoke(drop_mongodb, test_db_name, input="y")
    runner.invoke(drop_mongodb, test_db_copy_name, input="y")
    assert test_db_name not in [database["name"] for database in list_databases()]
    assert test_db_copy_name not in [database["name"] for database in list_databases()]
