from derex.runner.project import Project

from .fixtures import MINIMAL_PROJ, working_directory


def test_project():
    with working_directory(MINIMAL_PROJ):
        project = Project()

    assert type(project.config) == dict
    assert project.requirements_dir == MINIMAL_PROJ / "requirements"
    assert project.themes_dir == MINIMAL_PROJ / "themes"
    assert project.project_name == "minimal"

    project = Project(MINIMAL_PROJ)

    assert type(project.config) == dict
    assert project.requirements_dir == MINIMAL_PROJ / "requirements"
    assert project.themes_dir == MINIMAL_PROJ / "themes"
    assert project.project_name == "minimal"
