import os
from typing import List, Dict, Callable, Union
import pluggy
from derex.runner.utils import asbool
from derex.runner import hookimpl
from derex.runner.utils import compose_path


class BaseServices:
    @staticmethod
    @hookimpl
    def compose_options() -> Dict[str, Union[str, List[str]]]:
        """See derex.runner.plugin_spec.compose_options docstring
        """
        options = [
            "--project-name",
            "derex_services",
            "-f",
            compose_path("services.yml"),
        ]
        if asbool(os.environ.get("DEREX_ADMIN_SERVICES", True)):
            options += ["-f", compose_path("admin.yml")]
        return {
            "options": options,
            "name": "base",
            "priority": "_begin",
            "variant": "services",
        }


class BaseOpenEdX:
    @staticmethod
    @hookimpl
    def compose_options() -> Dict[str, Union[str, List[str]]]:
        """See derex.runner.plugin_spec.compose_options docstring
        """
        return {
            "options": [
                "--project-name",
                "derex_ironwood",
                "-f",
                compose_path("ironwood.yml"),
            ],
            "name": "base",
            "priority": "_begin",
            "variant": "openedx",
        }


class LocalOpenEdX:
    @staticmethod
    @hookimpl
    def compose_options() -> Dict[str, Union[str, List[str]]]:
        """See derex.runner.plugin_spec.compose_options docstring
        """
        return {
            "options": ["-f", compose_path("ironwood.yml")],
            "name": "base",
            "priority": "_begin",
            "variant": "local",
        }
