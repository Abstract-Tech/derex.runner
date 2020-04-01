from derex.runner.project import Project
from derex.runner.project import ProjectRunMode
from pathlib import Path
from typing import Dict
from typing import List
from typing import Union

import json
import os
import yaml


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
    assert project.requirements_image_name == "complete/openedx-requirements:a2e46f"
    # assert project.themes_image_name == "complete/openedx-themes:1f732a"


def test_minimal_project(workdir_copy):
    with workdir_copy(MINIMAL_PROJ):
        project = Project()

    assert type(project.config) == dict
    assert project.requirements_dir is None
    assert project.themes_dir is None
    assert project.name == "minimal"
    assert project.requirements_image_name == project.image_name
    assert project.themes_image_name == project.image_name
    assert project.themes_image_name == project.base_image


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


def test_docker_compose_addition(testproj, mocker):
    from derex.runner import hookimpl
    from derex.runner.compose_utils import get_compose_options
    from derex.runner.plugins import setup_plugin_manager

    class CustomAdditional:
        @staticmethod
        @hookimpl
        def local_compose_options(project: Project) -> Dict[str, Union[str, List[str]]]:
            """See derex.runner.plugin_spec.compose_options docstring
            """
            return {
                "options": ["custom-additional"],
                "name": "custom",
                "priority": ">local-derex",
            }

    with testproj:
        docker_compose_path = Path(testproj._tmpdir.name) / "docker-compose.yml"
        with docker_compose_path.open("w") as fh:
            fh.write("lms:\n  image: foobar\n")
        project = Project()
        mgr = setup_plugin_manager()
        mgr.register(CustomAdditional)
        mocker.patch(
            "derex.runner.compose_utils.setup_plugin_manager", return_value=mgr
        )
        opts = get_compose_options(args=[], variant="", project=project)
        # The last option should be the path of the user docker compose file for this project
        assert opts[-1] == str(docker_compose_path)


def test_docker_compose_addition_per_runmode(testproj, mocker):
    from derex.runner.compose_utils import get_compose_options

    with testproj:
        docker_compose_path = Path(testproj._tmpdir.name) / "docker-compose-debug.yml"
        with docker_compose_path.open("w") as fh:
            fh.write("lms:\n  image: foobar\n")
        project = Project()
        opts = get_compose_options(args=[], variant="", project=project)
        # The last option should be the path of the debug docker compose
        assert opts[-1] == str(docker_compose_path)

        project.runmode = ProjectRunMode.production
        opts = get_compose_options(args=[], variant="", project=project)
        # The last option should be the path of the production docker compose file
        assert opts[-1] != str(docker_compose_path)


def test_settings_enum(testproj):
    with testproj:
        assert Project().settings == Project().get_available_settings().base

        create_settings_file(Project().root, "production")
        Project().settings = Project().get_available_settings().production
        assert Project().settings == Project().get_available_settings().production


def test_image_prefix(testproj):
    with testproj as projdir:
        conf_file = Path(projdir) / "derex.config.yaml"
        config = {
            "project_name": "minimal",
            "image_prefix": "registry.example.com/onlinecourses/edx-ironwood",
        }
        conf_file.write_text(yaml.dump(config))
        # Create a requirements directory to signal derex
        # that we're going to build images for this project
        (Path(projdir) / "requirements").mkdir()
        project = Project()
        assert project.image_prefix == config["image_prefix"]
        assert project.themes_image_name.startswith(project.image_prefix)


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


def test_container_variables(testproj):
    with testproj as projdir:
        conf_file = Path(projdir) / "derex.config.yaml"
        config = {
            "project_name": "minimal",
            "variables": {
                "lms_site_name": {
                    "base": "dev.onlinecourses.example",
                    "production": "onlinecourses.example",
                }
            },
        }
        conf_file.write_text(yaml.dump(config))
        create_settings_file(Path(projdir), "production")
        project = Project()
        env = project.get_container_env()
        assert "DEREX_LMS_SITE_NAME" in env
        assert env["DEREX_LMS_SITE_NAME"] == "dev.onlinecourses.example"

        project.settings = project.get_available_settings().production
        env = project.get_container_env()
        assert env["DEREX_LMS_SITE_NAME"] == "onlinecourses.example"


def test_container_variables_json_serialized(testproj):
    with testproj as projdir:
        conf_file = Path(projdir) / "derex.config.yaml"
        config = {
            "project_name": "minimal",
            "variables": {
                "lms_ALL_JWT_AUTH": {
                    "base": {
                        "JWT_AUDIENCE": "jwt-audience",
                        "JWT_SECRET_KEY": "jwt-secret",
                    },
                    "production": {
                        "JWT_AUDIENCE": "prod-audience",
                        "JWT_SECRET_KEY": "prod-secret",
                    },
                }
            },
        }
        conf_file.write_text(yaml.dump(config))
        create_settings_file(Path(projdir), "production")
        project = Project()
        env = project.get_container_env()
        assert "DEREX_JSON_LMS_ALL_JWT_AUTH" in env
        expected = json.loads(env["DEREX_JSON_LMS_ALL_JWT_AUTH"])
        assert expected == config["variables"]["lms_ALL_JWT_AUTH"]["base"]


def create_settings_file(project_root: Path, filename: str):
    """Create an empty settings file inside the given project"""
    settings_dir = project_root / "settings"
    if not settings_dir.is_dir():
        settings_dir.mkdir()
        (settings_dir / "__init__.py").write_text("")
        project = Project(read_only=True)
    (project.settings_dir / f"{filename}.py").write_text("# Empty file")
