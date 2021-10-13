from derex.runner.constants import CONF_FILENAME
from derex.runner.constants import ProjectBuildTargets
from derex.runner.constants import SECRETS_CONF_FILENAME
from derex.runner.ddc import run_ddc_project
from derex.runner.project import Project
from derex.runner.project import ProjectRunMode
from pathlib import Path
from typing import Dict
from typing import List
from typing import Union

import json
import os
import pytest
import yaml


def test_complete_project(workdir, complete_project):
    with complete_project:
        project_path = Project().root
        project_loaded_with_path = Project(project_path)
        with workdir(project_path / "themes"):
            project = Project()

            assert project.root == project_loaded_with_path.root
            assert type(project.config) == dict
            assert project.requirements_dir == project_path / "requirements"
            assert project.themes_dir == project_path / "themes"
            assert project.e2e_dir == project_path / "e2e"
            assert project.name == f"{project.openedx_version.name}-complete"

            if project.openedx_version.name == "ironwood":
                assert (
                    project.get_build_target_image_name(
                        ProjectBuildTargets.requirements
                    )
                    == f"{project.name}/openedx-requirements:859e8a"
                )
            if project.openedx_version.name == "juniper":
                assert (
                    project.get_build_target_image_name(
                        ProjectBuildTargets.requirements
                    )
                    == f"{project.name}/openedx-requirements:d3922b"
                )
            if project.openedx_version.name == "koa":
                assert (
                    project.get_build_target_image_name(
                        ProjectBuildTargets.requirements
                    )
                    == f"{project.name}/openedx-requirements:fb1c1f"
                )


def test_minimal_project(minimal_project):
    with minimal_project:
        project = Project()

    assert type(project.config) == dict
    assert project.requirements_dir is None
    assert project.themes_dir is None
    assert project.e2e_dir is None
    assert project.name == f"{project.openedx_version.name}-minimal"
    assert project.get_build_target_image_name(ProjectBuildTargets.requirements) is None
    assert project.get_build_target_image_name(ProjectBuildTargets.themes) is None
    assert project.docker_image_name == project.base_image


def test_runmode(minimal_project):
    with minimal_project:
        project = Project()
        # If no default is specified, the value should be debug
        assert project.runmode == ProjectRunMode.debug

        # If a default value is specified, it should be picked up
        with (project.root / CONF_FILENAME).open("a") as fh:
            fh.write("default_runmode: production\n")
        assert Project().runmode == ProjectRunMode.production

        Project().runmode = ProjectRunMode.debug
        # Runmode changes should be persisted in the project directory
        # and picked up by a second Project instance
        assert Project().runmode == ProjectRunMode.debug


def test_ddc_project_addition(minimal_project, mocker, capsys):
    from derex.runner import hookimpl

    class CustomAdditional:
        @staticmethod
        @hookimpl
        def ddc_project_options(
            project: Project,
        ) -> Dict[str, Union[str, List[str]]]:
            """See derex.runner.plugin_spec.ddc_project_options docstring"""
            return {
                "options": ["custom-additional"],
                "name": "custom",
                "priority": ">local-derex",
            }

    with minimal_project:
        docker_compose_path = Project().root / "docker-compose.yml"
        with docker_compose_path.open("w") as fh:
            fh.write("lms:\n  image: foobar\n")
        project = Project()
        run_ddc_project([], project, dry_run=True)
        output = capsys.readouterr().out
        # The last option should be the path of the user docker compose file for this project
        assert output.endswith(f"-f {docker_compose_path}\n")


def test_docker_compose_addition_per_runmode(minimal_project, mocker, capsys):
    with minimal_project:
        docker_compose_debug_path = Project().root / "docker-compose-debug.yml"
        with docker_compose_debug_path.open("w") as fh:
            fh.write("lms:\n  image: foobar\n")
        project = Project()
        run_ddc_project([], project, dry_run=True)
        output = capsys.readouterr().out
        # The last option should be the path of the debug docker compose
        assert output.endswith(f"-f {docker_compose_debug_path}\n")

        project.runmode = ProjectRunMode.production
        default_project_docker_compose_file = project.private_filepath(
            "docker-compose.yml"
        )
        run_ddc_project([], project, dry_run=True)
        output = capsys.readouterr().out
        # The last option should be the path of the project default docker compose file
        assert output.endswith(f"-f {default_project_docker_compose_file}\n")


def test_settings_enum(minimal_project):
    with minimal_project:
        assert (
            Project().settings.value == Project().get_available_settings().default.value
        )

        create_settings_file(Project().root, "production")
        Project().settings = Project().get_available_settings().production
        assert (
            Project().settings.value
            == Project().get_available_settings().production.value
        )


def test_image_prefix(minimal_project):
    with minimal_project:
        conf_file = Project().root / CONF_FILENAME
        config = {
            "project_name": "minimal",
            "image_prefix": "registry.example.com/onlinecourses/edx-ironwood",
        }
        conf_file.write_text(yaml.dump(config))
        # Create a requirements directory to signal derex
        # that we're going to build images for this project
        (Project().root / "requirements").mkdir()
        project = Project()
        assert project.image_prefix == config["image_prefix"]
        assert project.get_build_target_image_name(
            ProjectBuildTargets.requirements
        ).startswith(project.image_prefix)


def test_materialize_settings(minimal_project):
    with minimal_project:
        default_settings_dir = Project().settings_directory_path()
        assert default_settings_dir.is_dir()

        create_settings_file(Project().root, "production")
        project = Project(read_only=True)

        assert default_settings_dir != project.settings_directory_path()

        project._materialize_settings()
        assert (project.settings_dir / "__init__.py").is_file(), str(
            sorted((project.settings_dir).iterdir())
        )
        assert (project.settings_dir / "derex").is_dir(), str(
            sorted((project.settings_dir).iterdir())
        )
        assets_py = project.settings_dir / "derex" / "build" / "assets.py"
        assert assets_py.is_file()

        base_py = project.settings_dir / "derex" / "default" / "__init__.py"
        assert base_py.is_file()
        assert os.access(str(base_py), os.W_OK)

        # In case a settings file was already present, it should be overwritten,
        # even if it lacks owner write permission.
        base_py.write_text("# Changed")
        base_py.chmod(0o444)
        assert not os.access(str(base_py), os.W_OK)
        project._materialize_settings()
        assert os.access(str(base_py), os.W_OK)


def test_container_variables(minimal_project):
    with minimal_project:
        conf_file = Project().root / CONF_FILENAME
        config = {
            "project_name": "minimal",
            "variables": {
                "lms_site_name": {
                    "default": "dev.onlinecourses.example",
                    "production": "onlinecourses.example",
                }
            },
        }
        conf_file.write_text(yaml.dump(config))
        create_settings_file(Project().root, "production")
        project = Project()
        env = project.get_container_env()
        assert "DEREX_LMS_SITE_NAME" in env
        assert env["DEREX_LMS_SITE_NAME"] == "dev.onlinecourses.example"

        project.settings = project.get_available_settings().production
        env = project.get_container_env()
        assert env["DEREX_LMS_SITE_NAME"] == "onlinecourses.example"


def test_project_name_constraints(minimal_project):
    with minimal_project:
        project_root = Project().root
        conf_file = project_root / CONF_FILENAME
        config = {"project_name": ";invalid;"}
        conf_file.write_text(yaml.dump(config))
        create_settings_file(project_root, "production")
        with pytest.raises(ValueError):
            Project()


def test_container_variables_json_serialized(minimal_project):
    with minimal_project:
        conf_file = Project().root / CONF_FILENAME
        config = {
            "project_name": "minimal",
            "variables": {
                "ALL_JWT_AUTH": {
                    "default": {
                        "JWT_AUDIENCE": "jwt-audience",
                        "JWT_SECRET_KEY": "jwt-secret",
                    },
                    "production": {
                        "JWT_AUDIENCE": "prod-audience",
                        "JWT_SECRET_KEY": "prod-secret",
                    },
                },
            },
        }
        conf_file.write_text(yaml.dump(config))
        create_settings_file(Project().root, "production")
        project = Project()
        env = project.get_container_env()
        assert "DEREX_JSON_ALL_JWT_AUTH" in env
        expected = config["variables"]["ALL_JWT_AUTH"]["default"]
        assert expected == json.loads(env["DEREX_JSON_ALL_JWT_AUTH"])

        project.settings = project._available_settings.production
        env = project.get_container_env()
        assert "DEREX_JSON_ALL_JWT_AUTH" in env
        expected = config["variables"]["ALL_JWT_AUTH"]["production"]
        assert expected == json.loads(env["DEREX_JSON_ALL_JWT_AUTH"])


def test_secret_variables(complete_project):
    with complete_project:
        conf_file = Project().root / SECRETS_CONF_FILENAME
        config = {
            "variables": {
                "ALL_MYSQL_ROOT_PASSWORD": {
                    "default": "base-secret-password",
                    "production": "production-secret-password",
                },
            },
        }
        conf_file.write_text(yaml.dump(config))
        create_settings_file(Project().root, "production")
        project = Project()
        env = project.get_container_env()
        assert "DEREX_ALL_MYSQL_ROOT_PASSWORD" in env
        expected = config["variables"]["ALL_MYSQL_ROOT_PASSWORD"]["default"]
        assert expected == env["DEREX_ALL_MYSQL_ROOT_PASSWORD"]

        project.settings = project._available_settings.production
        env = project.get_container_env()
        assert "DEREX_ALL_MYSQL_ROOT_PASSWORD" in env
        expected = config["variables"]["ALL_MYSQL_ROOT_PASSWORD"]["production"]
        assert expected == env["DEREX_ALL_MYSQL_ROOT_PASSWORD"]


def create_settings_file(project_root: Path, filename: str):
    """Create an empty settings file inside the given project"""
    settings_dir = project_root / "settings"
    if not settings_dir.is_dir():
        settings_dir.mkdir()
        (settings_dir / "__init__.py").write_text("")
    (settings_dir / f"{filename}.py").write_text("# Empty file")


def test_get_openedx_requirements_paths(complete_project):
    with complete_project:
        project = Project()
        requirements_paths = project.get_openedx_requirements_files()
        assert len(requirements_paths) == 2
        assert "testplugin.txt" in requirements_paths
        assert "xblocks.txt" in requirements_paths
