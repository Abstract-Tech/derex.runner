import os
import pkg_resources
from typing import List, Dict, Callable
import pluggy
from derex.runner import hookimpl
from derex.runner.utils import asbool

hookspec = pluggy.HookspecMarker("derex.runner")


class ConfigSpec:
    @hookspec
    def settings(self) -> Dict[str, Callable]:
        """Return a dict mapping service variants to callables.
        Callables should return a list of strings pointing to docker-compose yml files
        suitable to be passed as options to docker-compose.
        """
