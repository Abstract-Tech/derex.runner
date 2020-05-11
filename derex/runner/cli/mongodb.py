from derex.runner.project import Project
from tabulate import tabulate
from typing import Optional

import click


@click.group(invoke_without_command=True)
@click.pass_context
def mongodb(context: click.core.Context):
    """Commands to operate on the mongodb database"""
    if context.invoked_subcommand is None:
        from derex.runner.mongodb import list_databases

        click.echo(mongodb.get_help(context))
        databases = [
            (database["name"], database["sizeOnDisk"], database["empty"])
            for database in list_databases()
        ]
        if isinstance(context.obj, Project):
            project = context.obj
            database = [
                database
                for database in databases
                if database[0] == project.mongodb_db_name
            ]
            click.echo()
            if database:
                databases = database
                click.echo(f'Current MongoDB databases for project "{project.name}"')
            else:
                click.echo(
                    f'No MongoDB database "{project.mongodb_db_name}" found for project "{project.name}"'
                )
        click.echo()
        click.echo(tabulate(databases, headers=["Database", "Size", "Empty"]))


@mongodb.command(name="drop")
@click.pass_obj
@click.argument("db_name", type=str, required=False)
def drop_mongodb(project: Optional[Project], db_name: str):
    """Drop a mongodb database"""
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


@mongodb.command(name="list")
@click.pass_obj
@click.argument("db_name", type=str, required=False)
def list_mongodb(project: Optional[Project], db_name: str):
    """List all mongodb databases"""
    from derex.runner.mongodb import list_databases

    databases = [
        (database["name"], database["sizeOnDisk"], database["empty"])
        for database in list_databases()
    ]
    click.echo(tabulate(databases, headers=["Database", "Size", "Empty"]))
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
