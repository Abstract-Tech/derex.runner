from pathlib import Path


MINIMAL_PROJ = Path(__file__).with_name("fixtures") / "minimal"
COMPLETE_PROJ = Path(__file__).with_name("fixtures") / "complete"


def test_complete_project(workdir):
    from derex.runner.project import Project

    with workdir(COMPLETE_PROJ / "themes"):
        project = Project()

    project_loaded_with_path = Project(COMPLETE_PROJ)

    assert project.root == project_loaded_with_path.root

    assert type(project.config) == dict
    assert project.requirements_dir == COMPLETE_PROJ / "requirements"
    assert project.themes_dir == COMPLETE_PROJ / "themes"
    assert project.name == "complete"
    assert project.requirements_image_tag == "complete/openedx-requirements:a3d523"
    assert project.themes_image_tag == "complete/openedx-themes:1f732a"


def test_minimal_project(workdir):
    from derex.runner.project import Project

    with workdir(MINIMAL_PROJ):
        project = Project()

    assert type(project.config) == dict
    assert project.requirements_dir is None
    assert project.themes_dir is None
    assert project.name == "minimal"
    assert project.requirements_image_tag == project.image_tag
    assert project.themes_image_tag == project.image_tag
