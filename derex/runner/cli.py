# -*- coding: utf-8 -*-

"""Console script for derex.runner."""
from ansi_colours import AnsiColours as Colour
from click_plugins import with_plugins
from derex.runner import __version__
from derex.runner.logging_utils import setup_logging_decorator
from derex.runner.project import DebugBaseImageProject
from derex.runner.project import OpenEdXVersions
from derex.runner.project import Project
from derex.runner.project import ProjectRunMode
from derex.runner.secrets import HAS_MASTER_SECRET
from derex.runner.utils import abspath_from_egg
from distutils.spawn import find_executable
from functools import wraps
from terminal_table import Table
from typing import Any
from typing import Optional

import click
import importlib_metadata
import logging
import os
import sys


logger = logging.getLogger(__name__)


def ensure_project(func):
    """Decorator that checks if the current command was invoked from inside a project,
    (i.e. if the click context has a project) and prints a nice message if it's not.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        if click.get_current_context().obj is None:
            click.echo("This command needs to be run inside a derex project")
            return 1
        func(*args, **kwargs)

    return wrapper


@with_plugins(importlib_metadata.entry_points().get("derex.runner.cli_plugins", []))
@click.group(invoke_without_command=True)
@click.pass_context
@setup_logging_decorator
def derex(ctx):
    """Derex directs edX: commands to manage an Open edX installation
    """
    # Optimize --help and bash completion by importing
    from derex.runner.project import Project

    try:
        ctx.obj = Project()
    except ValueError:
        pass

    if ctx.invoked_subcommand:
        return

    click.echo(derex.get_help(ctx))

    from .docker import get_exposed_container_names

    containers = "\n".join(get_exposed_container_names())
    click.echo(
        f"\nThese containers are running and exposing an HTTP server on port 80:\n\n{containers}"
    )


@derex.group()
@click.pass_context
def debug(ctx):
    """Debugging utilities
    """


@derex.command()
@click.pass_obj
def reset_mailslurper(project):
    """Reset the mailslurper database.
    """
    from derex.runner.mysql import drop_database
    from derex.runner.docker import load_dump

    drop_database("mailslurper")
    click.echo("Priming mailslurper database")
    load_dump("derex/runner/fixtures/mailslurper.sql")
    return 0


@derex.command()
@click.pass_obj
@ensure_project
def compile_theme(project):
    """Compile theme sass files"""
    from derex.runner.compose_utils import run_compose

    if project.themes_dir is None:
        click.echo("No theme directory present in this project")
        return
    themes = ",".join(el.name for el in project.themes_dir.iterdir())
    uid = os.getuid()
    args = [
        "run",
        "--rm",
        "lms",
        "sh",
        "-c",
        f"""set -ex
            export PATH=/openedx/edx-platform/node_modules/.bin:$PATH  # FIXME: this should not be necessary
            paver compile_sass --theme-dirs /openedx/themes --themes {themes}
            chown {uid}:{uid} /openedx/themes/* -R""",
    ]
    run_compose(args, project=DebugBaseImageProject(), exit_afterwards=True)


@derex.command()
@click.pass_obj
@ensure_project
def create_bucket(project):
    """Create S3 buckets on Minio"""
    from derex.runner.docker import run_minio_shell

    click.echo(f"Creating bucket {project.name} with dowload policy on /profile-images")
    command = f"mc mb --ignore-existing local/{project.name}; "
    command += f"mc policy set download local/{project.name}/profile-images"
    run_minio_shell(command)


@derex.command()
@click.pass_obj
@ensure_project
def reset_rabbitmq(project):
    """Create rabbitmq vhost"""
    from derex.runner.compose_utils import run_compose

    vhost = f"{project.name}_edxqueue"
    args = [
        "exec",
        "-T",
        "rabbitmq",
        "sh",
        "-c",
        f"""rabbitmqctl add_vhost {vhost}
        rabbitmqctl set_permissions -p {vhost} guest ".*" ".*" ".*"
        """,
    ]
    run_compose(args, exit_afterwards=True)
    click.echo(f"Rabbitmq vhost {vhost} created")
    return 0


@derex.group()
def build():
    """Commands to build container images"""


@build.command()
@click.pass_obj
@ensure_project
def requirements(project):
    """Build the image that contains python requirements"""
    from derex.runner.build import build_requirements_image

    click.echo(
        f'Building docker image {project.requirements_image_name} ("{project.name}" requirements)'
    )
    build_requirements_image(project)


@build.command()
@click.pass_obj
@click.pass_context
@ensure_project
def themes(ctx, project: Project):
    """Build the image that includes compiled themes"""
    from derex.runner.build import build_themes_image

    ctx.forward(requirements)
    click.echo(
        f'Building docker image {project.themes_image_name} with "{project.name}" themes'
    )
    build_themes_image(project)
    click.echo(f"Built image {project.themes_image_name}")


@build.command()
@click.pass_obj
@click.pass_context
@ensure_project
def final(ctx, project: Project):
    """Build the final image for this project.
    For now this is the same as the final image"""
    ctx.forward(themes)


@build.command()
@click.pass_obj
@click.pass_context
@ensure_project
def final_refresh(ctx, project: Project):
    """Also pull base docker image before starting building"""
    from derex.runner.docker import pull_images

    pull_images([project.base_image, project.final_base_image])
    ctx.forward(final)


@build.command()
@click.argument(
    "version",
    type=click.Choice(OpenEdXVersions.__members__),
    required=True,
    callback=lambda _, __, value: value and OpenEdXVersions[value],
)
@click.option(
    "-t",
    "--target",
    type=click.Choice(
        [
            "dev",
            "nostatic-dev",
            "nostatic",
            "libgeos",
            "base",
            "sourceonly",
            "wheels",
            "translations",
            "nodump",
        ]
    ),
    default="dev",
    help="Target to build (nostatic, dev, translations)",
)
@click.option(
    "--push/--no-push", default=False, help="Also push image to registry after building"
)
@click.option(
    "--only-print-image-name/--do-build",
    default=False,
    help="Only print image name for the given target",
)
@click.option(
    "-d",
    "--docker-opts",
    envvar="DOCKER_OPTS",
    default="--output type=image,name={docker_image_prefix}-{target}{push_arg}",
    help=(
        "Additional options to pass to the docker invocation.\n"
        "By default outputs the image to the local docker daemon."
    ),
)
def openedx(version, target, push, only_print_image_name, docker_opts):
    """Build openedx image using docker. Defaults to dev image target."""
    dockerdir = abspath_from_egg("derex.runner", "docker-definition/Dockerfile").parent
    git_repo = version.value["git_repo"]
    git_branch = version.value["git_branch"]
    python_version = version.value.get("python_version", "3.6")
    docker_image_prefix = version.value["docker_image_prefix"]
    image_name = f"{docker_image_prefix}-{target}:{__version__}"
    if only_print_image_name:
        click.echo(image_name)
        return
    push_arg = ",push=true" if push else ""
    command = [
        "docker",
        "buildx",
        "build",
        str(dockerdir),
        "-t",
        image_name,
        "--build-arg",
        f"PYTHON_VERSION={python_version}",
        "--build-arg",
        f"EDX_PLATFORM_VERSION={git_branch}",
        "--build-arg",
        f"EDX_PLATFORM_REPOSITORY={git_repo}",
        f"--target={target}",
    ]
    transifex_path = os.path.expanduser("~/.transifexrc")
    if os.path.exists(transifex_path):
        command.extend(["--secret", f"id=transifex,src={transifex_path}"])
    if docker_opts:
        command.extend(docker_opts.format(**locals()).split())
    print("Invoking\n" + " ".join(command), file=sys.stderr)
    os.execve(find_executable(command[0]), command, os.environ)


@derex.command()
@click.argument(
    "runmode",
    type=click.Choice(ProjectRunMode.__members__),
    required=False,
    callback=lambda _, __, value: value and ProjectRunMode[value],
)
@click.option(
    "--force/-f",
    required=False,
    default=False,
    help="Allows switching to production mode without a main secret defined",
)
@click.pass_obj
@ensure_project
def runmode(project: Project, runmode: Optional[ProjectRunMode], force):
    """Get/set project runmode (debug/production)"""
    if runmode is None:
        click.echo(project.runmode.name)
    else:
        if project.runmode == runmode:
            click.echo(
                f"The current project runmode is already {runmode.name}", err=True
            )
            return
        if not force:
            if runmode is ProjectRunMode.production:
                if not HAS_MASTER_SECRET:
                    click.echo(
                        red("Set a master secret before switching to production"),
                        err=True,
                    )
                    sys.exit(1)
                    return 1
                    # We need https://github.com/Santandersecurityresearch/DrHeader/pull/102
                    # for the return 1 to work, but it's not released yet
        previous_runmode = project.runmode
        project.runmode = runmode
        click.echo(
            f"Switched runmode: {previous_runmode.name} → {runmode.name}", err=True
        )


def get_available_settings():
    """Return settings available on the current project"""
    try:
        project = Project()
    except ValueError:
        return None
    return project.get_available_settings().__members__


def materialise_settings(ctx, _, value):
    if value:
        return ctx.obj.get_available_settings()[value]
    return None


@derex.command()
@ensure_project
@click.argument(
    "settings",
    type=click.Choice(get_available_settings()),
    required=False,
    callback=materialise_settings,
)
@click.pass_obj
def settings(project: Project, settings: Optional[Any]):
    """Get/set project settings module to use (base.py/production.py)"""
    if settings is None:
        click.echo(project.settings.name)
    else:
        project.settings = settings


@derex.group(invoke_without_command=True)
@click.pass_context
def mongodb(context: click.core.Context):
    """Commands to operate on the mongodb database"""
    if context.invoked_subcommand is None:
        click.echo(mysql.get_help(context))
        if isinstance(context.obj, Project):
            from derex.runner.mongodb import list_databases

            project = context.obj
            database = [
                (database["name"], database["sizeOnDisk"], database["empty"])
                for database in list_databases()
                if database["name"] == project.mongodb_db_name
            ]
            if database:
                table = Table.create(
                    database,
                    ("Name", "Size (bytes)", "Empty"),
                    header_colour=Colour.cyan,
                    column_colours=(Colour.green,),
                )
                click.echo(f'\nCurrent MongoDB database for project "{project.name}"\n')
                click.echo(table)
            else:
                click.echo('No MongoDB database found for project "{project.name}"')


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
    table = Table.create(
        databases,
        ("Name", "Size (bytes)", "Empty"),
        header_colour=Colour.cyan,
        column_colours=(Colour.green,),
    )
    click.echo(f"\n{table}\n")
    return 0


@mongodb.command("copy")
@click.argument("source_db_name", type=str, required=True)
@click.argument("destination_db_name", type=str)
@click.option(
    "--drop", is_flag=True, default=False, help="Drop the source database",
)
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


@debug.command()
def minio_shell():
    from derex.runner.docker import run_minio_shell

    run_minio_shell()


@derex.command()
@click.option(
    "--old-key",
    # This is the key that the current default master secret generates
    default="ICDTE0ZnlbIR7r6/qE81nkF7Kshc2gXYv6fJR4I/HKPeTbxEeB3nxC85Ne6C844hEaaC2+KHBRIOzGou9leulZ7t",
    help="The old key to use for the update",
)
def update_minio(old_key: str):
    """Run minio to re-key data with the new secret. The output is very confusing, but it works.
    If you read a red warning and "Rotation complete" at the end, it means rekeying has worked.
    If your read your current SecretKey, it means the current credentials are correct and you don't need
    to update your keys.
    """
    from derex.runner.compose_utils import run_compose

    # We need to stop minio after it's done re-keying. To this end, we use the expect package
    script = "apk add expect --no-cache "
    # We need to make sure the current credentials are not working...
    script += ' && expect -c "spawn /usr/bin/minio server /data; expect "Endpoint" { close; exit 1 }"'
    # ..but the old ones are
    script += f' && if MINIO_SECRET_KEY="{old_key}" expect -c \'spawn /usr/bin/minio server /data; expect "Endpoint" {{ close; exit 1 }}\'; then exit 1; fi'
    script += f' && export MINIO_ACCESS_KEY_OLD="$MINIO_ACCESS_KEY" MINIO_SECRET_KEY_OLD="{old_key}"'
    expected_string = "Rotation complete, please make sure to unset MINIO_ACCESS_KEY_OLD and MINIO_SECRET_KEY_OLD envs"
    script += f" && expect -c 'spawn /usr/bin/minio server /data; expect \"{expected_string}\" {{ close; exit 0 }}'"
    args = [
        "run",
        "--rm",
        "--entrypoint",
        "/bin/sh",
        "-T",
        "minio",
        "-c",
        script,
    ]
    run_compose(args, exit_afterwards=True)
    click.echo(f"Minio server rekeying finished")


def red(string: str) -> str:
    return click.style(string, fg="red")


@derex.group(invoke_without_command=True)
@click.pass_context
def mysql(context: click.core.Context):
    """Commands to operate on the mysql database"""
    if context.invoked_subcommand is None:
        click.echo(mysql.get_help(context))

        if isinstance(context.obj, Project):
            project = context.obj
            import MySQLdb as mysqlclient
            from derex.runner.mysql import get_mysql_client

            try:
                mysql_client = get_mysql_client(database=project.mysql_db_name)
                n_tables = mysql_client.execute("show tables")
                table = Table.create(
                    [(project.mysql_db_name, n_tables)],
                    ("Name", "Tables"),
                    header_colour=Colour.cyan,
                    column_colours=(Colour.green,),
                )
                click.echo(f'\nCurrent MySQL databases for project "{project.name}"\n')
                click.echo(table)
            except mysqlclient._exceptions.OperationalError:
                click.echo('No MySQL database found for project "{project.name}"')


@mysql.command(name="list")
@click.pass_obj
@click.argument("db_name", type=str, required=False)
def list_mysql(project: Optional[Project], db_name: str):
    """List all mysql databases"""
    from derex.runner.mysql import list_databases

    click.echo("\n".join(list_databases()))
    return 0


@mysql.command(name="create")
@click.pass_obj
@click.argument("db_name", type=str, required=False)
def create_mysql(project: Optional[Project], db_name: str):
    """Create a mysql database"""
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


@mysql.command(name="drop")
@click.pass_obj
@click.argument("db_name", type=str, required=False)
def drop_mysql(project: Optional[Project], db_name: str):
    """Drop a mysql database"""
    if not any([project, db_name]):
        raise click.exceptions.MissingParameter(
            param_hint="db_name",
            param_type="str",
            message="Either specify a database name or run in a derex project.",
        )
    if not db_name and project:
        db_name = project.mysql_db_name

    if click.confirm(
        f'Dropping database "{db_name}". Are you sure you want to continue?'
    ):
        from derex.runner.mysql import drop_database

        drop_database(db_name)
    return 0


@mysql.command("copy")
@click.argument("source_db_name", type=str, required=True)
@click.argument("destination_db_name", type=str)
@click.option(
    "--drop", is_flag=True, default=False, help="Drop the source database",
)
@click.pass_obj
def copy_mysql(
    project: Optional[Project],
    source_db_name: str,
    destination_db_name: Optional[str],
    drop: bool = False,
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
        from derex.runner.mysql import copy_database, drop_database

        copy_database(source_db_name, destination_db_name)
        if drop and click.confirm(
            f'Are you sure you want to drop database "{source_db_name}" ?'
        ):
            drop_database(source_db_name)
    return 0


@mysql.command(name="reset")
@click.pass_obj
@ensure_project
@click.option(
    "--force",
    is_flag=True,
    default=False,
    help="Allow resetting mysql database if runmode is production",
)
def reset_mysql(project, force):
    """Reset mysql database for the project"""
    from derex.runner.mysql import reset_mysql_openedx

    if project.runmode is not ProjectRunMode.debug and not force:
        # Safety belt: we don't want people to run this in production
        click.get_current_context().fail(
            "The command reset-mysql can only be run in `debug` runmode.\n"
            "Use --force to override"
        )

    reset_mysql_openedx(DebugBaseImageProject())
    return 0
