from derex.runner.constants import CONF_FILENAME
from derex.runner.exceptions import ProjectNotFound
from jinja2 import Environment
from jinja2 import FileSystemLoader
from logging import getLogger
from pathlib import Path
from rich.console import Console
from rich.table import Table
from typing import Any
from typing import List
from typing import Union

import hashlib
import os
import re


logger = getLogger(__name__)
truthy = frozenset(("t", "true", "y", "yes", "on", "1"))


def get_dir_hash(
    dirname: Union[Path, str],
    excluded_files: List = [],
    ignore_hidden: bool = False,
    followlinks: bool = False,
    excluded_extensions: List = [],
) -> str:
    """Given a directory return an hash based on its contents"""
    if not os.path.isdir(dirname):
        raise TypeError(f"{dirname} is not a directory.")

    hashvalues = []
    for root, dirs, files in sorted(
        os.walk(dirname, topdown=True, followlinks=followlinks)
    ):
        if ignore_hidden and re.search(r"/\.", root):
            continue

        for filename in sorted(files):
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

    hasher = hashlib.sha256()
    for hashvalue in sorted(hashvalues):
        hasher.update(hashvalue.encode("utf-8"))
    return hasher.hexdigest()


def asbool(s: Any) -> bool:
    """Return the boolean value ``True`` if the case-lowered value of string
    input ``s`` is a `truthy string`. If ``s`` is already one of the
    boolean values ``True`` or ``False``, return it.
    Lifted from pyramid.settings.
    """
    if s is None:
        return False
    if isinstance(s, bool):
        return s
    s = str(s).strip()
    return s.lower() in truthy


def get_rich_console(*args, **kwargs):
    return Console(*args, **kwargs)


def get_rich_table(*args, **kwargs):
    return Table(*args, show_header=True, **kwargs)


def get_requirements_hash(path: Path) -> str:
    """Given a directory, return a hash of the contents of the text files it contains."""
    hasher = hashlib.sha256()
    logger.debug(
        f"Calculating hash for requirements dir {path}; initial (empty) hash is {hasher.hexdigest()}"
    )
    for file in sorted(path.iterdir()):
        if file.is_file():
            hasher.update(file.read_bytes())
        logger.debug(f"Examined contents of {file}; hash so far: {hasher.hexdigest()}")
    return hasher.hexdigest()


def find_project_root(path: Path) -> Path:
    """Find the project directory walking up the filesystem starting on the
    given path until a configuration file is found.
    """
    current = path
    while current != current.parent:
        if (current / CONF_FILENAME).is_file():
            return current
        current = current.parent
    raise ProjectNotFound(
        f"No directory found with a {CONF_FILENAME} file in it, starting from {path}"
    )


def compile_jinja_template(
    template_path: Path, destination: Path, context: dict = {}
) -> Path:
    """Write a compiled jinja2 template using the given context variables"""
    template = Environment(loader=FileSystemLoader(template_path.parent)).from_string(
        template_path.read_text()
    )
    rendered_template = template.render(**context)
    destination.write_text(rendered_template)
    return destination
