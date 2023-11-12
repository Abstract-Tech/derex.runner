from derex.runner.project import Project
from derex.runner.utils import get_rich_console
from derex.runner.utils import get_rich_table
from typing import Optional
from typing import Tuple

import click


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


@mongodb.command(name="shell")
@click.argument("command", type=str, required=False)
def shell(command: Optional[str]):
    """Execute a root session of the MongoDB client"""
    from derex.runner.mongodb import execute_root_shell

    execute_root_shell(command)


@mongodb.group("list")
@click.pass_context
def listing(context: click.core.Context):
    """MongoDB list predicate"""


@mongodb.command(name="drop")
@click.pass_obj
@click.argument("db_name", type=str, required=False)
def drop_mongodb(project: Optional[Project], db_name: str):
    """Drop a MongoDB database"""
    if not any([project, db_name]):
        raise click.exceptions.MissingParameter(
            param_hint="db_name",
            param_type="str",
            message="Either specify a destination database name or run in a derex project.",
        )
    if not db_name and project:
        db_name = project.mongodb_db_name

    if click.confirm(
        f'Dropping database "{db_name}". Are you sure you want to continue?'
    ):
        from derex.runner.mongodb import drop_database

        drop_database(db_name)
    return 0


@listing.command(name="databases")
@click.pass_obj
@click.argument("db_name", type=str, required=False)
def list_databases_cmd(project: Optional[Project], db_name: str):
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
@click.argument("current_password", type=str, required=False)
@click.option(
    "--force",
    is_flag=True,
    default=False,
    help="Do not ask for confirmation",
)
def reset_mongodb_password_cmd(current_password: Optional[str], force: bool):
    """Reset the mongodb root user password with the one derived
    from the Derex main secret."""
    from derex.runner.constants import MONGODB_ROOT_USER

    if click.confirm(
        f'This is going to reset the password for the mongodb "{MONGODB_ROOT_USER}" user'
        "with the one computed by derex.\n"
        "Are you sure you want to continue?"
    ):
        from derex.runner.mongodb import reset_mongodb_password

        reset_mongodb_password(current_password)
    return 0


@mongodb.command(name="dump")
@click.pass_obj
@click.argument("db_name", type=str)
def dump_database_cmd(project: Optional[Project], db_name: str):
    """Dump a mongodb database"""

    from derex.runner.mongodb import dump_database

    dump_database(db_name)
    return 0


@mongodb.command(name="restore")
@click.argument("db_name", type=str, nargs=1)
@click.argument("dump_file", type=click.Path(exists=True), nargs=1)
def restore_database_cmd(db_name: str, dump_file: str):
    """Restore a mysql database from a file"""

    from derex.runner.mongodb import restore_database

    restore_database(db_name, dump_file)
    return 0
