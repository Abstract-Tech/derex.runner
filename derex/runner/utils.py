from pathlib import Path
from typing import Union
import os
import pkg_resources
import yaml


CONF_FILENAME = ".derex.config.yaml"


def compose_path(name):
    return pkg_resources.resource_filename(__name__, f"compose_files/{name}")


def project_config():
    """Return the parsed configuration of this project.
    """
    dir = project_dir(os.getcwd())
    filename = dir / CONF_FILENAME
    return yaml.load(filename.open())


def project_dir(path: Union[Path, str]):
    """Find the project directory walking up the filesystem starting on the
    given path until a configuration file is found.
    """
    current = Path(path)
    while current != current.parent:
        if (current / CONF_FILENAME).is_file():
            return current
        current = current.parent
    raise ValueError(
        f"No directory found with a {CONF_FILENAME} file in it, starting from {path}"
    )


truthy = frozenset(("t", "true", "y", "yes", "on", "1"))


def asbool(s):
    """ Return the boolean value ``True`` if the case-lowered value of string
    input ``s`` is a :term:`truthy string`. If ``s`` is already one of the
    boolean values ``True`` or ``False``, return it.
    Lifted from pyramid.settings.
    """
    if s is None:
        return False
    if isinstance(s, bool):
        return s
    s = str(s).strip()
    return s.lower() in truthy
