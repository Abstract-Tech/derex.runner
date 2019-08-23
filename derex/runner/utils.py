from pathlib import Path
from typing import Union, List
import os
import re
import hashlib
import pkg_resources
import yaml


CONF_FILENAME = ".derex.config.yaml"


def compose_path(name):
    return pkg_resources.resource_filename(__name__, f"compose_files/{name}")


def get_project_config():
    """Return the parsed configuration of this project.
    """
    dir = get_project_dir(os.getcwd())
    filename = dir / CONF_FILENAME
    return yaml.load(filename.open())


def get_project_dir(path: Union[Path, str]):
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


def dirhash(
    dirname: Union[Path, str],
    excluded_files: List = [],
    ignore_hidden: bool = False,
    followlinks: bool = False,
    excluded_extensions: List = [],
):

    if not os.path.isdir(dirname):
        raise TypeError(f"{dirname} is not a directory.")

    hashvalues = []
    for root, dirs, files in os.walk(dirname, topdown=True, followlinks=followlinks):
        if ignore_hidden and re.search(r"/\.", root):
            continue

        dirs.sort()
        files.sort()

        for filename in files:
            if ignore_hidden and filename.startswith("."):
                continue

            if filename.split(".")[-1:][0] in excluded_extensions:
                continue

            if filename in excluded_files:
                continue

            hasher = hashlib.sha256()
            filepath = os.path.join(root, filename)
            if not os.path.exists(filepath):
                hashvalues.append(hasher.hexdigest())
            else:
                with open(filepath, "rb") as fileobj:
                    while True:
                        data = fileobj.read(64 * 1024)
                        if not data:
                            break
                        hasher.update(data)
                hashvalues.append(hasher.hexdigest())

            print(hashvalues)

    hasher = hashlib.sha256()
    for hashvalue in sorted(hashvalues):
        hasher.update(hashvalue.encode("utf-8"))
    return hasher.hexdigest()


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
