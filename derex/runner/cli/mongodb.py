from derex.runner.cli.utils import ensure_project
from derex.runner.cli.utils import green
from derex.runner.cli.utils import red
from derex.runner.docker_utils import client as docker_client
from derex.runner.project import Project
from derex.runner.utils import get_rich_console
from derex.runner.utils import get_rich_table
from typing import Optional
from typing import Tuple

import click
import docker
import logging


logger = logging.getLogger(__name__)


@click.group(invoke_without_command=True)
@click.pass_context
def mongodb(context: click.core.Context):
    """Commands to operate on the mongodb database"""
    if context.invoked_subcommand is None:
        click.echo(mongodb.get_help(context))
        if isinstance(context.obj, Project):
            from derex.runner.mongodb import list_databases

            click.echo()
            project = context.obj
            try:
                for db in list_databases():
                    if db["name"] == project.mongodb_db_name:
                        click.echo(
                            f'Current MongoDB databases for project "{project.name}"'
                        )
                        console = get_rich_console()
                        table = get_rich_table(
                            "Database", "Tables", "Django users", show_lines=True
                        )
                        table.add_row(
                            db["name"],
                            str(db["sizeOnDisk"]),
                            str(db["empty"]),
                        )
                        console.print(table)
                        break
                else:
                    click.echo(
                        f'No MongoDB database "{project.mongodb_db_name}" found for project "{project.name}"'
                    )
            except TimeoutError as exception:
                click.echo(red(str(exception)))


@mongodb.command(name="shell")
@click.pass_obj
@ensure_project
@click.argument("command", type=str, required=False)
def shell(project: Project, command: Optional[str]):
    """Execute a root session of the MongoDB client"""
    from derex.runner.mongodb import execute_root_shell

    execute_root_shell(project, command)


@mongodb.group("list")
@click.pass_context
def listing(context: click.core.Context):
    """MongoDB list predicate"""


@mongodb.command(name="drop")
@click.pass_obj
@ensure_project
@click.argument("db_name", type=str, required=False)
def drop_mongodb(project: Project, db_name: str):
    """Drop a MongoDB database"""
    if not db_name:
        db_name = project.mongodb_db_name

    if click.confirm(
        f'Dropping database "{db_name}". Are you sure you want to continue?'
    ):
        from derex.runner.mongodb import drop_database

        drop_database(db_name)
    return 0


@listing.command(name="databases")
@click.pass_obj
@ensure_project
@click.argument("db_name", type=str, required=False)
def list_databases_cmd(project: Project, db_name: str):
    """List all MongoDB databases"""
    from derex.runner.mongodb import list_databases

    console = get_rich_console()
    table = get_rich_table("Database", "Size (bytes)", "Empty", show_lines=True)
    for database in list_databases():
        table.add_row(
            database["name"], str(database["sizeOnDisk"]), str(database["empty"])
        )
    console.print(table)
    return 0


@listing.command(name="users")
def list_users():
    """List all MongoDB users"""
    from derex.runner.mongodb import list_users

    console = get_rich_console()
    table = get_rich_table("User", "Db", "Roles", show_lines=True)
    for user in list_users():
        roles = []
        for role in user["roles"]:
            roles.append(f"\"{role['role']}\" on database \"{role['db']}\"")
        table.add_row(user["user"], user["db"], "\n".join(roles))
    console.print(table)
    return 0


@mongodb.command(name="create-user")
@click.argument("user", type=str)
@click.argument("password", type=str)
@click.option(
    "--role",
    type=str,
    multiple=True,
    help="Role to assign to the user",
)
def create_user_cmd(user: str, password: str, role: Optional[Tuple]):
    """Create a mongodb user."""
    from derex.runner.mongodb import create_user

    create_user(user, password, role)
    return 0


@mongodb.command("copy")
@click.argument("source_db_name", type=str, required=True)
@click.argument("destination_db_name", type=str)
@click.option("--drop", is_flag=True, default=False, help="Drop the source database")
@click.pass_obj
def copy_mongodb(
    project: Optional[Project],
    source_db_name: str,
    destination_db_name: Optional[str],
    drop: bool,
):
    """
    Copy an existing mongodb database. If no destination database is given defaults
    to the project mongodb database name.
    """
    if not any([project, destination_db_name]):
        raise click.exceptions.MissingParameter(
            param_hint="destination_db_name",
            param_type="str",
            message="Either specify a destination database name or run in a derex project.",
        )
    if not destination_db_name and project:
        destination_db_name = project.mongodb_db_name

    if click.confirm(
        f'Copying database "{source_db_name}" to "{destination_db_name}."'
        "Are you sure you want to continue?"
    ):
        from derex.runner.mongodb import copy_database

        copy_database(source_db_name, destination_db_name)
        if drop and click.confirm(
            f'Are you sure you want to drop database "{source_db_name}" ?'
        ):
            from derex.runner.mongodb import drop_database

            drop_database(source_db_name)
    return 0


@mongodb.command(name="reset-root-password")
@click.pass_obj
@ensure_project
@click.argument("current_password", type=str, required=False)
@click.option(
    "--force",
    is_flag=True,
    default=False,
    help="Do not ask for confirmation",
)
def reset_mongodb_password_cmd(
    project: Project, current_password: Optional[str], force: bool
):
    """Reset the mongodb root user password with the one derived
    from the Derex main secret."""
    if click.confirm(
        f'This is going to reset the password for the mongodb "{project.mongodb_user}" user'
        "with the one computed by derex.\n"
        "Are you sure you want to continue?"
    ):
        from derex.runner.mongodb import reset_mongodb_password

        reset_mongodb_password(project, current_password)
    return 0


@mongodb.group("upgrade")
@click.pass_context
def upgrade(context: click.core.Context):
    """MongoDB upgrade procedures"""


@upgrade.command(name="32-to-36")
@click.pass_obj
@ensure_project
@click.option(
    "--source",
    "source_data_volume",
    type=str,
    help="Source data volume",
)
@click.option(
    "--destination",
    "destination_data_volume",
    type=str,
    help="Destination data volume",
)
def upgrade_from_32_to_36(
    project: Project,
    source_data_volume: Optional[str],
    destination_data_volume: Optional[str],
):
    """Upgrades the mongodb data volume from version 3.2 to 3.4 to 3.6"""
    if not source_data_volume:
        source_data_volume = project.mongodb_docker_volume
    if not destination_data_volume:
        destination_project = project
        destination_project.openedx_version.value["mongodb_image"] = "mongo:3.6"
        destination_data_volume = destination_project.mongodb_docker_volume

    intermediary_data_volume = "derex_tmp_mongodb34"

    if source_data_volume == destination_data_volume:
        click.echo(red("Source and destination data volume are the same !"))
        click.echo(red("Please specify a different source or destination volume"))
        click.echo(red("Upgrade aborted"))
        return 0

    try:
        docker_client.volumes.get(source_data_volume)
    except docker.errors.NotFound:
        raise RuntimeError(f'Volume "{source_data_volume}" does not exists')
    try:
        docker_client.volumes.get(destination_data_volume)
        click.echo(
            red(
                f'Destination volume "{destination_data_volume}" already exists !\n'
                "Please specify a different destination volume."
            )
        )
        click.echo(red("Upgrade aborted"))
        return 0
    except docker.errors.NotFound:
        pass

    if click.confirm(
        f'This is going to copy the source MongoDB data volume "{source_data_volume}" '
        f'to a new data volume "{destination_data_volume}" and upgrade it '
        "from version 3.2 to 3.6\n"
        "Are you sure you want to continue?"
    ):
        from derex.runner.mongodb import run_mongodb_upgrade

        try:
            logger.info(f'Creating data volume "{destination_data_volume}"')
            docker_client.volumes.create(destination_data_volume)
            docker_client.volumes.create(intermediary_data_volume)

            click.echo("Running upgrade from mongodb 3.2 to 3.4")
            run_mongodb_upgrade(
                project, source_data_volume, intermediary_data_volume, "3.2", "3.4"
            )
            click.echo("Running upgrade from mongodb 3.4 to 3.6")
            run_mongodb_upgrade(
                project,
                intermediary_data_volume,
                destination_data_volume,
                "3.4",
                "3.6",
            )
            click.echo(
                green(
                    f'Successfully upgraded the mongodb data volume "{destination_data_volume}" to version 3.6'
                )
            )
        except Exception as exception:
            click.echo(red("Upgrade failed"))
            click.echo(red(exception))
            return 1
        finally:
            logger.info(
                f'Dropping intermediary data volume "{intermediary_data_volume}"'
            )
            try:
                docker_client.volumes.get(intermediary_data_volume).remove()
            except docker.errors.NotFound:
                pass
        return 0
    click.echo(red("Upgrade aborted"))
    return 0


@upgrade.command(name="36-to-44")
@click.pass_obj
@ensure_project
@click.option(
    "--source",
    "source_data_volume",
    type=str,
    help="Source data volume",
)
@click.option(
    "--destination",
    "destination_data_volume",
    type=str,
    help="Destination data volume",
)
def upgrade_from_36_to_44(
    project: Project,
    source_data_volume: Optional[str],
    destination_data_volume: Optional[str],
):
    """Upgrades the mongodb data volume from version 3.6 to 4.0 to 4.2 to 4.4"""
    if not source_data_volume:
        source_data_volume = project.mongodb_docker_volume
    if not destination_data_volume:
        destination_project = project
        destination_project.openedx_version.value["mongodb_image"] = "mongo:4.4"
        destination_data_volume = destination_project.mongodb_docker_volume

    intermediary_data_volume_40 = "derex_tmp_mongodb4.0"
    intermediary_data_volume_42 = "derex_tmp_mongodb4.2"

    if source_data_volume == destination_data_volume:
        click.echo(red("Source and destination data volume are the same !"))
        click.echo(red("Please specify a different source or destination volume"))
        click.echo(red("Upgrade aborted"))
        return 0

    try:
        docker_client.volumes.get(source_data_volume)
    except docker.errors.NotFound:
        raise RuntimeError(f'Volume "{source_data_volume}" does not exists')
    try:
        docker_client.volumes.get(destination_data_volume)
        click.echo(
            red(
                f'Destination volume "{destination_data_volume}" already exists !\n'
                "Please specify a different destination volume."
            )
        )
        click.echo(red("Upgrade aborted"))
        return 0
    except docker.errors.NotFound:
        pass

    if click.confirm(
        f'This is going to copy the source MongoDB data volume "{source_data_volume}" '
        f'to a new data volume "{destination_data_volume}" and upgrade it '
        "from version 3.6 to 4.4\n"
        "Are you sure you want to continue?"
    ):
        from derex.runner.mongodb import run_mongodb_upgrade

        try:
            logger.info(f'Creating data volume "{destination_data_volume}"')
            docker_client.volumes.create(destination_data_volume)
            docker_client.volumes.create(intermediary_data_volume_40)
            docker_client.volumes.create(intermediary_data_volume_42)

            click.echo("Running upgrade from mongodb 3.6 to 4.0")
            run_mongodb_upgrade(
                project, source_data_volume, intermediary_data_volume_40, "3.6", "4.0"
            )
            click.echo("Running upgrade from mongodb 4.0 to 4.2")
            run_mongodb_upgrade(
                project,
                intermediary_data_volume_40,
                intermediary_data_volume_42,
                "4.0",
                "4.2",
            )
            click.echo("Running upgrade from mongodb 4.2 to 4.4")
            run_mongodb_upgrade(
                project,
                intermediary_data_volume_42,
                destination_data_volume,
                "4.2",
                "4.4",
            )
            click.echo(
                green(
                    f'Successfully upgraded the mongodb data volume "{destination_data_volume}" to version 4.4'
                )
            )
        except Exception as exception:
            click.echo(red("Upgrade failed"))
            click.echo(red(exception))
            return 1
        finally:
            for intermediary_data_volume in [
                intermediary_data_volume_40,
                intermediary_data_volume_42,
            ]:
                logger.info(
                    f'Dropping intermediary data volume "{intermediary_data_volume}"'
                )
                try:
                    docker_client.volumes.get(intermediary_data_volume).remove()
                except docker.errors.NotFound:
                    pass
        return 0
    click.echo(red("Upgrade aborted"))
    return 0
