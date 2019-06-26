# -*- coding: utf-8 -*-
import docker


def test_ensure_network_present(mocker):
    from derex.runner.docker import ensure_network_present

    client = mocker.patch("derex.runner.docker.client")
    ensure_network_present()
    client.networks.get.assert_called_once()

    client.networks.get.side_effect = docker.errors.NotFound("derex network not found")
    ensure_network_present()
    client.networks.create.assert_called_once_with("derex")
