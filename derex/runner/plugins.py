import os
import pkg_resources
from typing import List, Dict, Callable
import pluggy
from derex.runner import hookimpl
from derex.runner.config import BaseConfig
from derex.runner.utils import asbool

hookspec = pluggy.HookspecMarker("derex.runner")


class ConfigSpec:
    @hookspec
    def settings(self) -> Dict[str, Callable]:
        """Return a dict mapping service variants to callables.
        Callables should return a list of strings pointing to docker-compose yml files
        suitable to be passed as options to docker-compose.
        """


def setup_plugin_manager():
    plugin_manager = pluggy.PluginManager("derex.runner")
    plugin_manager.add_hookspecs(ConfigSpec)
    plugin_manager.load_setuptools_entrypoints("derex.runner")
    plugin_manager.register(BaseConfig())
    return plugin_manager
