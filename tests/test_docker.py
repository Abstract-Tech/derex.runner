# -*- coding: utf-8 -*-
from derex.runner.project import Project
from types import SimpleNamespace

import docker


def test_ensure_volumes_present(mocker):
    from derex.runner.docker_utils import ensure_volumes_present
    from derex.runner.docker_utils import VOLUMES

    client = mocker.patch("derex.runner.docker_utils.client")

    client.volumes.list.return_value = []
    ensure_volumes_present()
    assert client.volumes.create.call_count > 3
    client.volumes.create.assert_any_call("derex_mysql")
    client.volumes.create.assert_any_call("derex_mongodb")

    client.volumes.create.reset_mock()
    client.volumes.list.return_value = [SimpleNamespace(name=name) for name in VOLUMES]
    ensure_volumes_present()
    client.volumes.create.assert_not_called()


def test_check_services(mocker):
    from derex.runner.docker_utils import check_services

    client = mocker.patch("derex.runner.docker_utils.client")

    client.containers.get.return_value.status = "running"
    assert check_services(["mysql"])

    client.containers.get.side_effect = docker.errors.NotFound(
        "Mysql container not found"
    )
    assert not check_services(["mysql"])


def test_wait_for_service(mocker):
    from derex.runner.docker_utils import wait_for_service

    container = mocker.MagicMock()
    container.exec_run.return_value = mocker.MagicMock(exit_code=0)

    client = mocker.patch("derex.runner.docker_utils.client")
    client.containers.get.return_value = container

    wait_for_service("mysql", 'mysql -psecret -e "SHOW DATABASES"', 1)
    client.containers.get.assert_called_with("mysql")
    container.exec_run.assert_called_with('mysql -psecret -e "SHOW DATABASES"')


def test_get_final_image(mocker, minimal_project):
    from derex.runner.docker_utils import image_exists

    mocker.patch(
        "derex.runner.docker_utils.docker.APIClient",
        return_value=mocker.Mock(
            images=mocker.Mock(return_value=DOCKER_DAEMON_IMAGES_RESPONSE)
        ),
    )
    with minimal_project:
        project = Project()
        image_exists(project)


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
