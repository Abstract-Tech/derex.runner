from derex.runner.build import build_project_image
from derex.runner.constants import ProjectBuildTargets
from derex.runner.project import Project


def requirements_dockerfile_tests(project, buildx_mock):
    assert f"FROM {project.final_base_image}" in buildx_mock.call_args.args[0]
    assert "testplugin.txt" in buildx_mock.call_args.args[0]
    assert "xblocks.txt" in buildx_mock.call_args.args[0]


def openedx_customizations_dockerfile_tests(project, buildx_mock):
    assert (
        "FROM requirements as openedx_customizations" in buildx_mock.call_args.args[0]
    )
    assert (
        "/openedx/edx-platform/test_openedx_customization.py"
        in buildx_mock.call_args.args[0]
    )
    assert (
        "/openedx/edx-platform/subfolder/test_openedx_customization.py"
        in buildx_mock.call_args.args[0]
    )


def test_build_project_image_requirements(complete_project, mocker):
    with complete_project:
        project = Project()
        target = ProjectBuildTargets.requirements
        tag = project.requirements_image_name

        buildx_mock = mocker.patch("derex.runner.build.buildx_image")

        build_project_image(
            project,
            target,
            output="docker",
            registry=None,
            tag=tag,
            tag_latest=False,
            pull=False,
            no_cache=False,
            cache_from=False,
            cache_to=False,
        )
        buildx_mock.assert_called_once()

        requirements_dockerfile_tests(project, buildx_mock)

        assert buildx_mock.call_args.args[1] == [project.requirements_dir]
        assert buildx_mock.call_args.args[3] == target.name
        assert buildx_mock.call_args.args[5] == [tag]

        tag = "my-tag"

        build_project_image(
            project,
            target,
            output="docker",
            registry=None,
            tag=tag,
            tag_latest=False,
            pull=False,
            no_cache=False,
            cache_from=False,
            cache_to=False,
        )

        assert buildx_mock.call_count == 2
        assert buildx_mock.call_args.args[5] == [tag]


def test_build_project_image_openedx_customizations(complete_project, mocker):
    with complete_project:
        project = Project()
        target = ProjectBuildTargets.openedx_customizations
        tag = project.openedx_customizations_image_name
        buildx_mock = mocker.patch("derex.runner.build.buildx_image")

        build_project_image(
            project,
            target,
            output="docker",
            registry=None,
            tag=tag,
            tag_latest=False,
            pull=False,
            no_cache=False,
            cache_from=False,
            cache_to=False,
        )

        buildx_mock.assert_called_once()

        requirements_dockerfile_tests(project, buildx_mock)
        openedx_customizations_dockerfile_tests(project, buildx_mock)

        assert project.requirements_dir in buildx_mock.call_args.args[1]
        assert project.openedx_customizations_dir in buildx_mock.call_args.args[1]
        assert buildx_mock.call_args.args[3] == target.name
        assert buildx_mock.call_args.args[5] == [tag]
