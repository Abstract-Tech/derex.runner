from derex.runner.project import Project
from derex.runner.project import ProjectRunMode
from pathlib import Path

import os


MINIMAL_PROJ = Path(__file__).with_name("fixtures") / "minimal"
COMPLETE_PROJ = Path(__file__).with_name("fixtures") / "complete"


def test_complete_project(workdir):
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


def test_settings_enum(testproj):
    with testproj:
        assert Project().settings == Project().get_available_settings().base

        create_settings_file(Project().root, "production")
        Project().settings = Project().get_available_settings().production
        assert Project().settings == Project().get_available_settings().production


def test_populate_settings(testproj):
    with testproj as projdir:

        default_settings_dir = Project().settings_directory_path()
        assert default_settings_dir.is_dir()

        create_settings_file(Path(projdir), "production")
        project = Project(read_only=True)

        assert default_settings_dir != project.settings_directory_path()

        project._populate_settings()
        assert (project.settings_dir / "base.py").is_file(), str(
            sorted((project.settings_dir).iterdir())
        )
        assert (project.settings_dir / "derex").is_dir(), str(
            sorted((project.settings_dir).iterdir())
        )
        assert (project.settings_dir / "derex" / "base.py").is_file()
        assert (project.settings_dir / "derex" / "__init__.py").is_file()

        assert not os.access(str(project.settings_dir / "derex" / "base.py"), os.W_OK)


def create_settings_file(project_root: Path, filename: str):
    """Create a settings file inside the given project
    Does not take into account
    """
    settings_dir = project_root / "settings"
    if not settings_dir.is_dir():
        settings_dir.mkdir()
        (settings_dir / "__init__.py").write_text("")
        project = Project(read_only=True)
    (project.settings_dir / f"{filename}.py").write_text("# Empty file")
