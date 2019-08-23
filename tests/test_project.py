from derex.runner.project import Project

from .fixtures import MINIMAL_PROJ, working_directory


def test_project():
    with working_directory(MINIMAL_PROJ):
        project = Project()

    project_loaded_with_path = Project(MINIMAL_PROJ)

    assert project == project_loaded_with_path

    assert type(project.config) == dict
    assert project.requirements_dir == MINIMAL_PROJ / "requirements"
    assert project.themes_dir == MINIMAL_PROJ / "themes"
    assert project.project_name == "minimal"
    assert project.requirements_image_tag == "minimal/openedx-requirements:b964b4"
    assert project.themes_image_tag == "minimal/openedx-themes:0c4b97"
