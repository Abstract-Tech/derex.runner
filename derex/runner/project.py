from derex.runner.utils import get_dir_hash
from pathlib import Path
from typing import Union

import hashlib
import os
import yaml


CONF_FILENAME = ".derex.config.yaml"


class Project:
    def __init__(self, path: Union[Path, str] = None):
        if not path:
            path = os.getcwd()

        self.path = Path(path)
        self.themes_dir = self.path / "themes"
        self.requirements_dir = self.path / "requirements"
        self.name = self.config["project_name"]
        self.base_image = self.config.get("base_image", "derex/openedx-ironwood:latest")

    def __eq__(self, other):
        return self.root == other.root

    @property
    def requirements_image_tag(self):
        """Returns a string suitabile to be used as tag for a docker image
        """
        hasher = hashlib.sha256()
        hasher.update(get_dir_hash(self.requirements_dir).encode("utf-8"))
        version = hasher.hexdigest()[:6]
        return f"{self.name}/openedx-requirements:{version}"

    @property
    def themes_image_tag(self):
        """Returns a string suitabile to be used as tag for a docker image
        """
        hasher = hashlib.sha256()
        hasher.update(get_dir_hash(self.themes_dir).encode("utf-8"))
        version = hasher.hexdigest()[:6]
        return f"{self.name}/openedx-themes:{version}"

    @property
    def config(self):
        """Return the parsed configuration of this project.
        """
        filepath = self.root / CONF_FILENAME
        return yaml.load(filepath.open())

    @property
    def root(self):
        """Find the project directory walking up the filesystem starting on the
        given path until a configuration file is found.
        """
        current = self.path
        while current != current.parent:
            if (current / CONF_FILENAME).is_file():
                return current
            current = current.parent
        raise ValueError(
            f"No directory found with a {CONF_FILENAME} file in it, starting from {self.path}"
        )
