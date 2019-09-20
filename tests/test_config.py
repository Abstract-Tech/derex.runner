from derex.runner.project import Project
from pathlib import Path


MINIMAL_PROJ = Path(__file__).with_name("fixtures") / "minimal"


def test_get_final_image(mocker):
    from derex.runner.config import get_final_image

    mocker.patch(
        "derex.runner.config.docker.APIClient",
        return_value=mocker.Mock(
            images=mocker.Mock(return_value=DOCKER_DAEMON_IMAGES_RESPONSE)
        ),
    )
    project = Project(MINIMAL_PROJ)
    get_final_image(project)


DOCKER_DAEMON_IMAGES_RESPONSE = [
    {
        "Containers": -1,
        "Created": 1568757938,
        "Id": "sha256:e7d35cfa3056cf59688f75d3d5e3b7ac2c38a00ef64058937cf8bcfa078ff81f",
        "Labels": None,
        "ParentId": "",
        "RepoDigests": [
            "derex/openedx-ironwood@sha256:ced32894ea157b1fad9d894343059666492a928714d769ae3dd4eab09de99e59"
        ],
        "RepoTags": None,
        "SharedSize": -1,
        "Size": 1665836550,
        "VirtualSize": 1665836550,
    }
]
