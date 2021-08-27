# from .conftest import assert_result_ok
# from .conftest import DEREX_TEST_USER
# from click.testing import CliRunner
# from derex.runner.docker_utils import wait_for_container
# from derex.runner.ddc import run_ddc
# from importlib import reload

# from derex.runner.project import Project
# from derex.runner.mongodb import get_mongodb_client

# import pytest
# import uuid


# runner = CliRunner(mix_stderr=False)


# def start_mongodb(project):
#     """Ensure the mongodb service is up"""
#     run_ddc(["up", "-d", project.mongodb_host], "services", project)
#     wait_for_container(project.mongodb_host)


# def stop_mongodb(project):
#     with minimal_project:
#         run_ddc(
#             ["down"],
#             "services",
#             project
#         )


# def cleanup_mongodb(project):
#     """Ensure no test database is left behind"""
#     start_mongodb(project)
#     project = Project()
#     mongodb_client = get_mongodb_client(project)
#     for database_name in [
#         database["name"]
#         for database in mongodb_client.list_databases()
#         if "derex_test_db_" in database["name"]
#     ]:
#         mongodb_client.drop_database(database_name)

#     for user in mongodb_client.admin.command("usersInfo").get("users"):
#         if DEREX_TEST_USER in user["user"]:
#             mongodb_client.admin.command("dropUser", DEREX_TEST_USER)


# def test_derex_mongodb(minimal_project):
#     from derex.runner.cli.mongodb import copy_mongodb
#     from derex.runner.cli.mongodb import drop_mongodb
#     from derex.runner.mongodb import list_databases

#     with minimal_project:
#         project = Project()
#         start_mongodb(project)

#         mongodb_client = get_mongodb_client(project)

#         test_db_name = f"derex_test_db_{uuid.uuid4().hex[:20]}"
#         test_db_copy_name = f"derex_test_db_copy_{uuid.uuid4().hex[:20]}"
#         random_value = uuid.uuid4().hex[:20]
#         test_data = {"data": random_value}

#         mongodb_client[test_db_name]["test_collection"].insert_one(test_data)
#         assert test_db_name in [database["name"] for database in list_databases()]

#         runner.invoke(copy_mongodb, f"{test_db_name} {test_db_copy_name}", input="y")
#         assert test_db_copy_name in [database["name"] for database in list_databases()]
#         assert mongodb_client[test_db_copy_name]["test_collection"].find_one(test_data)

#         runner.invoke(drop_mongodb, test_db_name, input="y")
#         runner.invoke(drop_mongodb, test_db_copy_name, input="y")
#         assert test_db_name not in [database["name"] for database in list_databases()]
#         assert test_db_copy_name not in [database["name"] for database in list_databases()]

#         cleanup_mongodb(project)
#         stop_mongodb(project)

# def test_derex_mongodb_reset_password(mocker, start_mongodb, minimal_project):
#     from derex.runner.cli.mongodb import create_user_cmd
#     from derex.runner.cli.mongodb import reset_mongodb_password_cmd
#     from derex.runner.cli.mongodb import shell

#     with minimal_project:
#         assert_result_ok(
#             runner.invoke(create_user_cmd, [DEREX_TEST_USER, "secret", "--role=root"])
#         )
#         mocker.patch("derex.runner.project.MONGODB_ROOT_USER", new=DEREX_TEST_USER)

#         # This is expected to fail since we set a custom password for the root user
#         result = runner.invoke(shell)
#         assert result.exit_code == 1

#         # We reset the password to the derex generated one
#         assert_result_ok(runner.invoke(reset_mongodb_password_cmd, ["secret"], input="y"))

#         # If the password is still not resetted to the value of the derex generated password
#         # but still set to "secret" the next test will fail
#         assert_result_ok(runner.invoke(shell))
