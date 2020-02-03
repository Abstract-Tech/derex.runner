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
    assert project.requirements_image_tag == "complete/openedx-requirements:a2e46f"
    # assert project.themes_image_tag == "complete/openedx-themes:1f732a"


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
    assert project.themes_image_tag == project.base_image


def test_runmode(testproj):
    from derex.runner.project import Project
    from derex.runner.project import ProjectRunMode
    from derex.runner.utils import CONF_FILENAME

    with testproj:
        # If no default is specified, the value should be debug
        assert Project().runmode == ProjectRunMode.debug

        # If a default value is specified, it should be picked up
        with (Path(testproj._tmpdir.name) / CONF_FILENAME).open("a") as fh:
            fh.write("default_runmode: production\n")
        assert Project().runmode == ProjectRunMode.production

        Project().runmode = ProjectRunMode.production
        # Runmode changes should be persisted in the project directory
        # and picked up by a second Project instance
        assert Project().runmode == ProjectRunMode.production
