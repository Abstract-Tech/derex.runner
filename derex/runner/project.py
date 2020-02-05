from derex.runner.utils import CONF_FILENAME
from derex.runner.utils import get_dir_hash
from enum import Enum
from enum import IntEnum
from logging import getLogger
from pathlib import Path
from typing import Optional
from typing import Union

import hashlib
import os
import yaml


logger = getLogger(__name__)
DEREX_RUNNER_PROJECT_DIR = ".derex"


class ProjectRunMode(Enum):
    debug = "debug"  # The first is the default
    production = "production"


class Project:
    """Represents a derex.runner project, i.e. a directory with a
    `derex.config.yaml` file and optionally a "themes", "settings" and
    "requirements" directory.
    The directory is inspected on object instantiation: changes will not
    be automatically picked up unless a new object is created.
    """

    #: The root path to this project
    root: Path

    #: The tag of the base image with dev goodies and precompiled assets
    base_image: str

    # Tne image tag of the base image for the final production project build
    final_base_image: str

    #: The directory containing requirements, if defined
    requirements_dir: Optional[Path] = None

    #: The directory containing themes, if defined
    themes_dir: Optional[Path] = None

    # The directory containing project settings (that feed django.conf.settings)
    settings_dir: Optional[Path] = None

    # The directory containing project database fixtures (used on --reset-mysql)
    fixtures_dir: Optional[Path] = None

    # The image tag of the image that includes requirements
    requirements_image_tag: str

    # The image tag of the image that includes requirements and themes
    themes_image_tag: str

    # The image tag of the final image containing everything needed for this project
    image_tag: str

    # Name of the database this project uses
    mysql_db_name: str

    # Path to a local docker-compose.yml file, if present
    local_compose: Optional[Path] = None

    # Enum containing possible settings modules
    _available_settings = None

    @property
    def runmode(self) -> ProjectRunMode:
        """The run mode of this project, either debug or production.
        In debug mode django's runserver is used. Templates are reloaded
        on every request and assets do not need to be collected.
        In production mode gunicorn is run, and assets need to be compiled and collected.
        """
        name = "runmode"
        mode_str = self._get_status(name)
        if mode_str is not None:
            if mode_str in ProjectRunMode.__members__:
                return ProjectRunMode[mode_str]
            # We found a string but we don't recognize it: warn the user
            logger.warn(
                f"Value `{mode_str}` found in `{self.private_filepath(name)}` "
                "is not valid for runmode "
                "(valid values are `debug` and `production`)"
            )
        default = self.config.get(f"default_{name}")
        if default:
            if default not in ProjectRunMode.__members__:
                logger.warn(
                    f"Value `{default}` found in config `{self.root / CONF_FILENAME}` "
                    "is not a valid default for runmode "
                    "(valid values are `debug` and `production`)"
                )
            else:
                return ProjectRunMode[default]
        return next(iter(ProjectRunMode))  # Return the first by default

    @runmode.setter
    def runmode(self, value: ProjectRunMode):
        self._set_status("runmode", value.name)

    @property
    def settings(self):
        """Name of the module to use as DJANGO_SETTINGS_MODULE
        """
        return self.get_available_settings()["base"]

    @settings.setter
    def settings(self, value: IntEnum):
        self._set_status("settings", value.name)

    def _get_status(self, name: str) -> Optional[str]:
        """Read value for the desired status from the project directory.
        """
        filepath = self.private_filepath(name)
        if filepath.exists():
            return filepath.read_text()
        return None

    def _set_status(self, name: str, value: str):
        """Persist a status in the project directory.
        Each status will be written to a different file.
        """
        if not self.private_filepath(name).parent.exists():
            self.private_filepath(name).parent.mkdir()
        self.private_filepath(name).write_text(value)

    def private_filepath(self, name: str) -> Path:
        """Return the full file path to `name` rooted from the
        project private dir ".derex".

            >>> Project().private_filepath("filename.txt")
            "/path/to/project/.derex/filename.txt"
        """
        return self.root / DEREX_RUNNER_PROJECT_DIR / name

    def __init__(self, path: Union[Path, str] = None):
        # Load first, and only afterwards manipulate the folder
        # so that if an error occurs during loading we bail wout
        # before making any change
        self._load(path)
        self._prepare_dir()

    def _load(self, path: Union[Path, str] = None):
        """Load project configuraton from the given directory.
        """
        if not path:
            path = os.getcwd()
        self.root = find_project_root(Path(path))
        config_path = self.root / CONF_FILENAME
        self.config = yaml.load(config_path.open())
        self.base_image = self.config.get("base_image", "derex/openedx-ironwood:latest")
        self.final_base_image = self.config.get(
            "final_base_image", "derex/openedx-nostatic:latest"
        )
        if "project_name" not in self.config:
            raise ValueError(f"A project_name was not specified in {config_path}")
        self.name = self.config["project_name"]
        local_compose = self.root / "docker-compose.yml"
        if local_compose.is_file():
            self.local_compose = local_compose

        requirements_dir = self.root / "requirements"
        if requirements_dir.is_dir():
            self.requirements_dir = requirements_dir
            # We only hash text files inside the requirements image:
            # this way changes to code can be made effective by
            # mounting the requirements directory
            img_hash = get_requirements_hash(self.requirements_dir)
            self.requirements_image_tag = (
                f"{self.name}/openedx-requirements:{img_hash[:6]}"
            )
        else:
            self.requirements_image_tag = self.base_image

        themes_dir = self.root / "themes"
        if themes_dir.is_dir():
            self.themes_dir = themes_dir
            img_hash = get_dir_hash(
                self.themes_dir
            )  # XXX some files are generated. We should ignore them when we hash the directory
            self.themes_image_tag = f"{self.name}/openedx-themes:{img_hash[:6]}"
        else:
            self.themes_image_tag = self.requirements_image_tag

        settings_dir = self.root / "settings"
        if settings_dir.is_dir():
            self.settings_dir = settings_dir
            # TODO: run some sanity checks on the settings dir and raise an
            # exception if they fail

        fixtures_dir = self.root / "fixtures"
        if fixtures_dir.is_dir():
            self.fixtures_dir = fixtures_dir

        self.image_tag = self.themes_image_tag
        self.mysql_db_name = self.config.get("mysql_db_name", f"{self.name}_edxapp")

    def _prepare_dir(self):
        """Make sure the project directory is in the desired state.
        Create a settings directory and populate it if it does not exist.
        Replace files that need to be updated with the newer version.
        """
        if self.settings_dir is not None:
            self._populate_settings()

        if not (self.root / DEREX_RUNNER_PROJECT_DIR).exists():
            (self.root / DEREX_RUNNER_PROJECT_DIR).mkdir()

    def _populate_settings(self):
        """If the project includes user defined settings, add ours to that directory
        to let the project's settings use the line

            from .derex import *
        """
        # TODO

    def get_available_settings(self):
        """Return an Enum object that includes possible settings for this project.
        This enum must be dynamic, since it depends on the contents of the project
        settings directory.
        For this reason we use the functional API for python Enum, which means we're
        limited to IntEnums. For this reason we'll be using `settings.name` instead
        of `settings.value` throughout the code.
        """
        if self._available_settings is not None:
            return self._available_settings
        if self.settings_dir is None:
            available_settings = IntEnum("settings", "base")
        else:
            settings_names = []
            for file in self.settings_dir.iterdir():
                if file.suffix == ".py" and file.stem != "__init__":
                    settings_names.append(file.stem)

            available_settings = IntEnum("settings", " ".join(settings_names))
        self._available_settings = available_settings
        return available_settings


def get_requirements_hash(path: Path) -> str:
    """Given a directory, return a hash of the contents of the text files it contains.
    """
    hasher = hashlib.sha256()
    for file in path.iterdir():
        if file.is_file():
            hasher.update(file.read_bytes())
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
    raise ValueError(
        f"No directory found with a {CONF_FILENAME} file in it, starting from {path}"
    )
