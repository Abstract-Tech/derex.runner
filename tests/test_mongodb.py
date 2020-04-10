from click.testing import CliRunner

import pytest
import uuid


runner = CliRunner(mix_stderr=False)


# TODO: if this test fails after test data have been created
# it won't be cleaned up
# TODO: --drop option should be tested too
@pytest.mark.slowtest
def test_derex_mongodb(start_services):
    """Test the `derex mysql copy` cli command """
    from derex.runner.cli import drop_mongodb, copy_mongodb
    from derex.runner.mongodb import get_mongodb_client, list_databases

    test_db_name = uuid.uuid4().hex[:20]
    test_copy_db_name = uuid.uuid4().hex[:20]
    random_value = uuid.uuid4().hex[:20]

    test_data = {"data": random_value}

    mongodb_client = get_mongodb_client()
    mongodb_client[test_db_name]["test_collection"].insert_one(test_data)

    assert test_db_name in [database["name"] for database in list_databases()]

    runner.invoke(copy_mongodb, f"{test_db_name} {test_copy_db_name}", input="y")

    assert test_copy_db_name in [database["name"] for database in list_databases()]
    assert mongodb_client[test_copy_db_name]["test_collection"].find_one(test_data)

    runner.invoke(drop_mongodb, test_db_name, input="y")
    runner.invoke(drop_mongodb, test_copy_db_name, input="y")

    assert test_db_name not in [database["name"] for database in list_databases()]
    assert test_copy_db_name not in [database["name"] for database in list_databases()]
