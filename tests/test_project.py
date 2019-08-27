from .fixtures import COMPLETE_PROJ
from .fixtures import working_directory


def test_project():
    from derex.runner.project import Project

    with working_directory(COMPLETE_PROJ):
        project = Project()

    project_loaded_with_path = Project(COMPLETE_PROJ)

    assert project == project_loaded_with_path

    assert type(project.config) == dict
    assert project.requirements_dir == COMPLETE_PROJ / "requirements"
    assert project.themes_dir == COMPLETE_PROJ / "themes"
    assert project.name == "minimal"
    assert project.requirements_image_tag == "minimal/openedx-requirements:b964b4"
    assert project.themes_image_tag == "minimal/openedx-themes:0c4b97"


def test_default_project():
    from derex.runner.project import DefaultProject

    project = DefaultProject()
    assert project.name
