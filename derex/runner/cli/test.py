from derex.runner.cli.utils import ensure_project
from derex.runner.cli.utils import red
from derex.runner.compose_generation import generate_ddc_test_compose
from derex.runner.ddc import run_docker_compose

import click


@click.group()
def test():
    """Commands to run project tests"""


@test.command()
@click.pass_obj
@ensure_project
def e2e(project):
    """Run project e2e tests"""
    if not project.e2e_dir:
        click.echo(red(f"No e2e tests directory found in {project.root}"), err=True)
        return 1

    click.echo(f"Running e2e Cypress tests from {project.e2e_dir}")
    test_compose_path = generate_ddc_test_compose(project)
    run_docker_compose(
        ["-f", str(test_compose_path), "run", "--rm", "cypress"],
        dry_run=False,
        exit_afterwards=True,
    )
