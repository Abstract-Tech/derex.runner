from derex.runner.utils import get_dir_hash
from pathlib import Path
from typing import Optional
from typing import Union

import hashlib
import os
import yaml


CONF_FILENAME = ".derex.config.yaml"


class Project:
    """Represents a derex.runner project, i.e. a directory with a
    `.derex.config.yaml` file and optionally a "themes", "settings" and
    "requirements" directory.
    """

    #: The root path to this project
    root: Path

    #: The directory containing requirements, if defined
    requirements_dir: Optional[Path] = None

    #: The directory containing themes, if defined
    themes_dir: Optional[Path] = None

    # The directory containing project settings (that feed django.conf.settings)
    settings_dir: Optional[Path] = None

    # The image tag of the image that includes requirements
    requirements_image_tag: str

    # The image tag of the image that includes requirements and themes
    themes_image_tag: str

    # The image tag of the final image containing everything needed for this project
    image_tag: str

    # Name of the database this project uses
    mysql_db_name: str

    def __init__(self, path: Union[Path, str] = None):
        if not path:
            path = os.getcwd()
        self.root = find_project_root(Path(path))
        config_path = self.root / CONF_FILENAME
        self.config = yaml.load(config_path.open())
        self.base_image = self.config.get("base_image", "derex/openedx-ironwood:latest")
        if "project_name" not in self.config:
            raise ValueError(f"A project_name was not specified in {config_path}")
        self.name = self.config["project_name"]

        requirements_dir = self.root / "requirements"
        if requirements_dir.is_dir():
            self.requirements_dir = requirements_dir
            img_hash = get_dir_hash(self.requirements_dir)
            self.requirements_image_tag = (
                f"{self.name}/openedx-requirements:{img_hash[:6]}"
            )
        else:
            self.requirements_image_tag = self.base_image

        themes_dir = self.root / "themes"
        if themes_dir.is_dir():
            self.themes_dir = themes_dir
            img_hash = get_dir_hash(self.themes_dir)
            self.themes_image_tag = f"{self.name}/openedx-themes:{img_hash[:6]}"
        else:
            self.themes_image_tag = self.requirements_image_tag

        settings_dir = self.root / "settings"
        if settings_dir.is_dir():
            self.settings_dir = settings_dir
            # TODO: run some sanity checks on the settings dir and raise an
            # exception if they fail

        self.image_tag = self.themes_image_tag
        self.mysql_db_name = self.config.get("mysql_db_name", f"{self.name}_edxapp")


def find_project_root(path: Path) -> Path:
    """Find the project directory walking up the filesystem starting on the
    given path until a configuration file is found.
    """
    current = path
    while current != current.parent:
        if (current / CONF_FILENAME).is_file():
            return current
        current = current.parent
    raise ValueError(
        f"No directory found with a {CONF_FILENAME} file in it, starting from {path}"
    )
