# -*- coding: utf-8 -*-
from types import SimpleNamespace
import docker


def test_ensure_network_present(mocker):
    from derex.runner.docker import ensure_network_present

    client = mocker.patch("derex.runner.docker.client")
    ensure_network_present()
    client.networks.get.assert_called_once()

    client.networks.get.side_effect = docker.errors.NotFound("derex network not found")
    ensure_network_present()
    client.networks.create.assert_called_once_with("derex")


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
