from typing import Dict, List, Union
import pluggy


hookspec = pluggy.HookspecMarker("derex.runner")


@hookspec
def compose_options() -> Dict[str, Union[str, float, int, List[str]]]:
    """Return a dict describing how to add this plugin.
    The dict `name` and `priority` keys will be used to determine ordering.
    The `variant` key can have values `services` or `openedx`.
    The `options` key contains a list of strings pointing to docker-compose yml files
    suitable to be passed as options to docker-compose.
    Example:

    {
        "name": "addon",
        "priority": ">base",
        "variant": "ironwood",
        "options": ["-f", "/path/to/docker-compose.yml"],
    }
    """


@hookspec
def local_compose_options(
    project_root: str
) -> Dict[str, Union[str, float, int, List[str]]]:
    """Return a dict describing how to add this plugin to a local project.
    The dict `name` and `priority` keys will be used to determine ordering.
    The `options` key contains a list of strings pointing to docker-compose yml files
    suitable to be passed as options to docker-compose.
    Example:

    {
        "name": "addon",
        "priority": ">base",
        "options": ["-f", "/path/to/docker-compose.yml"],
    }
    """
