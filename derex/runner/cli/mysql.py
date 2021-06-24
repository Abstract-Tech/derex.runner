from derex.runner.project import DebugBaseImageProject
from derex.runner.project import Project
from derex.runner.project import ProjectRunMode
from derex.runner.utils import get_rich_console
from derex.runner.utils import get_rich_table
from typing import Optional

import click


@click.group(invoke_without_command=True)
@click.pass_context
def mysql(context: click.core.Context):
    """Commands to operate on the mysql database"""
    if context.invoked_subcommand is None:
        from derex.runner.mysql import show_databases

        click.echo(mysql.get_help(context))
        if isinstance(context.obj, Project):
            click.echo()
            project = context.obj
            for db in show_databases():
                if db[0] == project.mysql_db_name:
                    click.echo(f'Current MySQL databases for project "{project.name}"')
                    console = get_rich_console()
                    table = get_rich_table(
                        "Database", "Tables", "Django users", show_lines=True
                    )
                    table.add_row(db[0], str(db[1]), str(db[2]))
                    console.print(table)
                    break
            else:
                click.echo(
                    f'No MySQL database "{project.mysql_db_name}" found for project "{project.name}"'
                )
                click.echo('You can prime it with "derex mysql reset"')


@mysql.command(name="shell")
@click.argument("command", type=str, required=False)
def shell(command: Optional[str]):
    """Execute a root session of the mysql client"""
    from derex.runner.mysql import execute_root_shell

    execute_root_shell(command)


@mysql.group("create")
@click.pass_context
def create(context: click.core.Context):
    """MySQL CREATE predicate"""


@mysql.group("drop")
@click.pass_context
def drop(context: click.core.Context):
    """MySQL DROP predicate"""


@mysql.group("list")
@click.pass_context
def show(context: click.core.Context):
    """MySQL SHOW predicate"""


@create.command(name="database")
@click.pass_obj
@click.argument("db_name", type=str, required=False)
def create_database_cmd(project: Optional[Project], db_name: str):
    """Create a mysql database."""
    if not any([project, db_name]):
        raise click.exceptions.MissingParameter(
            param_hint="db_name",
            param_type="str",
            message="Either specify a database name or run in a derex project.",
        )
    if not db_name and project:
        db_name = project.mysql_db_name

    from derex.runner.mysql import create_database

    create_database(db_name)
    return 0


@create.command(name="user")
@click.argument("user", type=str)
@click.argument("password", type=str)
@click.argument("host", type=str, default="localhost")
def create_user_cmd(user: str, password: str, host: str):
    """Create a mysql user"""
    from derex.runner.mysql import create_user

    create_user(user, password, host)
    return 0


@drop.command(name="database")
@click.pass_obj
@click.argument("db_name", type=str, required=False)
def drop_database_cmd(project: Optional[Project], db_name: str):
    """Drop a mysql database"""
    if not any([project, db_name]):
        raise click.exceptions.MissingParameter(
            param_hint="db_name",
            param_type="str",
            message="Either specify a database name or run in a derex project.",
        )
    if not db_name and project:
        db_name = project.mysql_db_name

    if click.confirm(f'Are you sure you want to drop database "{db_name}" ?'):
        from derex.runner.mysql import drop_database

        drop_database(db_name)
    return 0


@drop.command(name="user")
@click.argument("user", type=str)
@click.argument("host", type=str, default="localhost")
def drop_user_cmd(user: str, host: str):
    """Drop a mysql user"""
    if click.confirm(f"Are you sure you want to drop user '{user}'@'{host}' ?"):
        from derex.runner.mysql import drop_user

        drop_user(user, host)
    return 0


@show.command(name="databases")
def show_databases_cmd():
    """List all MySQL databases"""
    from derex.runner.mysql import show_databases

    console = get_rich_console()
    table = get_rich_table("Database", "Tables", "Django users", show_lines=True)
    for database in show_databases():
        table.add_row(database[0], str(database[1]), str(database[2]))
    console.print(table)
    return 0


@show.command(name="users")
def show_users_cmd():
    """List all MySQL users"""
    from derex.runner.mysql import list_users

    console = get_rich_console()
    table = get_rich_table("User", "Host", "Password", show_lines=True)
    for user in list_users():
        table.add_row(user[0], user[1], user[2])
    console.print(table)
    return 0


@mysql.command("copy-database")
@click.argument("source_db_name", type=str, required=True)
@click.argument("destination_db_name", type=str)
@click.pass_obj
def copy_database_cmd(
    project: Optional[Project], source_db_name: str, destination_db_name: Optional[str]
):
    """
    Copy an existing mysql database. If no destination database is given it defaults
    to the project mysql database name.
    """
    if not any([project, destination_db_name]):
        raise click.exceptions.MissingParameter(
            param_hint="destination_db_name",
            param_type="str",
            message="Either specify a destination database name or run in a derex project.",
        )

    if not destination_db_name and project:
        destination_db_name = project.mysql_db_name

    if click.confirm(
        f'Copying database "{source_db_name}" to "{destination_db_name}."'
        "Are you sure you want to continue?"
    ):
        from derex.runner.mysql import copy_database

        copy_database(source_db_name, destination_db_name)
    return 0


@mysql.command(name="reset")
@click.pass_context
@click.option(
    "--force",
    is_flag=True,
    default=False,
    help="Do not ask for confirmation and allow resetting mysql database if runmode is production",
)
def reset_mysql_cmd(context, force):
    """Reset MySQL database for the current project"""

    if context.obj is None:
        click.echo("This command needs to be run inside a derex project")
        return 1
    project = context.obj

    from derex.runner.mysql import reset_mysql_openedx

    if project.runmode is not ProjectRunMode.debug and not force:
        # Safety belt: we don't want people to run this in production
        context.fail(
            "The command mysql reset can only be run in `debug` runmode.\n"
            "Use --force to override"
        )

    if not force:
        if not click.confirm(
            "Are you sure you want to delete all data on MySQL database "
            f'"{project.mysql_db_name}" and restore it to the project '
            f'"{project.name}" default state ?'
        ):
            return 1
    reset_mysql_openedx(DebugBaseImageProject())
    return 0


@mysql.command(name="reset-root-password")
@click.argument("current_password", type=str, required=True)
@click.option(
    "--force",
    is_flag=True,
    default=False,
    help="Do not ask for confirmation",
)
def reset_mysql_password_cmd(current_password: str, force: bool):
    """Reset the mysql root user password with the one derived from
    the Derex main secret."""
    from derex.runner.constants import MYSQL_ROOT_USER

    if click.confirm(
        f'This is going to reset the password for the mysql "{MYSQL_ROOT_USER}" user '
        "with the one computed by derex.\n"
        "Are you sure you want to continue?"
    ):
        from derex.runner.mysql import reset_mysql_password

        reset_mysql_password(current_password)
    return 0
