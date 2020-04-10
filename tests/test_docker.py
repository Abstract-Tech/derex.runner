# -*- coding: utf-8 -*-
from types import SimpleNamespace

import docker


def test_ensure_volumes_present(mocker):
    from derex.runner.docker import ensure_volumes_present
    from derex.runner.docker import VOLUMES

    client = mocker.patch("derex.runner.docker.client")

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
    from derex.runner.docker import check_services

    client = mocker.patch("derex.runner.docker.client")

    client.containers.get.return_value.status = "running"
    assert check_services(["mysql"])

    client.containers.get.side_effect = docker.errors.NotFound(
        "Mysql container not found"
    )
    assert not check_services(["mysql"])


def test_wait_for_service(mocker):
    from derex.runner.docker import wait_for_service

    wait_for_service("mysql", 'mysql -psecret -e "SHOW DATABASES"', 1)
