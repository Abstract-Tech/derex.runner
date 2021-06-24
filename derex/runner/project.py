from derex.runner import __version__
from derex.runner.constants import CONF_FILENAME
from derex.runner.constants import DEREX_DJANGO_SETTINGS_PATH
from derex.runner.constants import DEREX_OPENEDX_CUSTOMIZATIONS_PATH
from derex.runner.constants import MONGODB_ROOT_USER
from derex.runner.constants import MYSQL_ROOT_USER
from derex.runner.constants import SECRETS_CONF_FILENAME
from derex.runner.secrets import DerexSecrets
from derex.runner.secrets import get_secret
from derex.runner.utils import get_dir_hash
from enum import Enum
from logging import getLogger
from pathlib import Path
from typing import Dict
from typing import Optional
from typing import Union

import difflib
import hashlib
import json
import os
import re
import stat
import yaml


logger = getLogger(__name__)
DEREX_RUNNER_PROJECT_DIR = ".derex"


class OpenEdXVersions(Enum):
    # Values will be passed as uppercased named arguments to the docker build
    # e.g. --build-arg EDX_PLATFORM_RELEASE=koa
    ironwood = {
        "edx_platform_repository": "https://github.com/edx/edx-platform.git",
        "edx_platform_version": "open-release/ironwood.master",
        "edx_platform_release": "ironwood",
        "docker_image_prefix": "derex/openedx-ironwood",
        "alpine_version": "alpine3.11",
        "python_version": "2.7",
        "pip_version": "20.3.4",
        # The latest node release does not work on ironwood
        # (node-sass version fails to compile)
        "node_version": "v10.22.1",
        "mysql_image": "mysql:5.6.36",
        "mongodb_image": "mongo:3.2.21",
    }
    juniper = {
        "edx_platform_repository": "https://github.com/edx/edx-platform.git",
        "edx_platform_version": "open-release/juniper.master",
        "edx_platform_release": "juniper",
        "docker_image_prefix": "derex/openedx-juniper",
        "alpine_version": "alpine3.11",
        "python_version": "3.6",
        "pip_version": "21.0.1",
        "node_version": "v12.19.0",
        "mysql_image": "mysql:5.6.36",
        "mongodb_image": "mongo:3.6.23",
    }
    koa = {
        "edx_platform_repository": "https://github.com/edx/edx-platform.git",
        # We set koa.3 since as today (20 may 2021) koa.master codebase is broken
        "edx_platform_version": "open-release/koa.3",
        "edx_platform_release": "koa",
        "docker_image_prefix": "derex/openedx-koa",
        # We are stuck on alpine3.12 since SciPy won't build
        # on gcc>=10 due to fortran incompatibility issues.
        # See more at https://gcc.gnu.org/gcc-10/porting_to.html
        "alpine_version": "alpine3.12",
        "python_version": "3.8",
        "pip_version": "21.0.1",
        "node_version": "v12.19.0",
        "mysql_image": "mysql:5.7.34",
        "mongodb_image": "mongo:3.6.23",
    }


class ProjectRunMode(Enum):
    debug = "debug"  # The first is the default
    production = "production"


class Project:
    """Represents a derex.runner project, i.e. a directory with a
    `derex.config.yaml` file and optionally a "themes", "settings" and
    "requirements" directory.
    The directory is inspected on object instantiation: changes will not
    be automatically picked up unless a new object is created.

    The project root directory can be passed in the `path` parameter, and
    defaults to the current directory.
    If files needed by derex outside of its private `.derex.` dir are missing
    they will be created, unless the `read_only` parameter is set to True.
    """

    #: The root path to this project
    root: Path

    #: The name of the base image with dev goodies and precompiled assets
    base_image: str

    # Tne image name of the base image for the final production project build
    final_base_image: str

    # The named version of Open edX to use
    openedx_version: OpenEdXVersions

    #: The directory containing requirements, if defined
    requirements_dir: Optional[Path] = None

    #: The directory containing themes, if defined
    themes_dir: Optional[Path] = None

    # The directory containing project settings (that feed django.conf.settings)
    settings_dir: Optional[Path] = None

    # The directory containing project database fixtures (used on --reset-mysql)
    fixtures_dir: Optional[Path] = None

    # The directory where plugins can store their custom requirements, settings,
    # fixtures and themes.
    plugins_dir: Optional[Path] = None

    # The directory containing openedx python modules to be replaced
    openedx_customizations_dir: Optional[Path] = None

    # The directory containing cypress tests
    e2e_dir: Optional[Path] = None

    # The image name of the image that includes requirements
    requirements_image_name: str

    # The image name of the image that includes requirements and themes
    themes_image_name: str

    # The image name of the final image containing everything needed for this project
    image_name: str

    # Image prefix to construct the above image names if they're not specified.
    # Can include a private docker name, like registry.example.com/onlinecourses/edx-ironwood
    image_prefix: str

    # Path to a local docker-compose.yml file, if present
    local_compose: Optional[Path] = None

    # Volumes to mount the requirements. In case this is not None the requirements
    # directory will not be mounted directly, but this dictionary will be used.
    # Keys are paths on the host system and values are path inside the container
    requirements_volumes: Optional[Dict[str, str]] = None

    # Wheter derex default settings should be materialized in the project
    # settings directory
    materialize_derex_settings = bool

    # Enum containing possible settings modules
    _available_settings = None

    @property
    def mysql_db_name(self) -> str:
        return self.config.get("mysql_db_name", f"{self.name}_openedx")

    @property
    def mysql_user(self) -> str:
        return self.config.get("mysql_user", MYSQL_ROOT_USER)

    @property
    def mongodb_db_name(self) -> str:
        return self.config.get("mongodb_db_name", f"{self.name}_openedx")

    @property
    def mongodb_user(self) -> str:
        return self.config.get("mongodb_user", MONGODB_ROOT_USER)

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
            logger.warning(
                f"Value `{mode_str}` found in `{self.private_filepath(name)}` "
                "is not valid as runmode "
                "(valid values are `debug` and `production`)"
            )
        default = self.config.get(f"default_{name}")
        if default:
            if default not in ProjectRunMode.__members__:
                logger.warning(
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
        """Name of the module to use as DJANGO_SETTINGS_MODULE"""
        current_status = self._get_status("settings", "default")
        return self.get_available_settings()[current_status]

    @settings.setter
    def settings(self, value: Enum):
        self._set_status("settings", value.name)

    def settings_directory_path(self) -> Path:
        """Return an absolute path that will be mounted under
        /openedx/edx-platform/derex_settings inside the
        container.
        If the project has local settings, we use that directory.
        Otherwise we use the derex_django settings directory bundled
        with `derex.runner`
        """
        if self.settings_dir is not None:
            return self.settings_dir
        return DEREX_DJANGO_SETTINGS_PATH

    def _get_status(self, name: str, default: Optional[str] = None) -> Optional[str]:
        """Read value for the desired status from the project directory."""
        filepath = self.private_filepath(name)
        if filepath.exists():
            return filepath.read_text()
        return default

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

    def __init__(self, path: Union[Path, str] = None, read_only: bool = False):
        logger.debug("Creating project object")
        # Load first, and only afterwards manipulate the folder
        # so that if an error occurs during loading we bail wout
        # before making any change
        self._load(path)
        if not read_only:
            self._materialize_settings()
        if not (self.root / DEREX_RUNNER_PROJECT_DIR).exists():
            (self.root / DEREX_RUNNER_PROJECT_DIR).mkdir()

    def _load(self, path: Union[Path, str] = None):
        """Load project configuraton from the given directory."""
        if not path:
            path = os.getcwd()
        self.root = find_project_root(Path(path))
        config_path = self.root / CONF_FILENAME
        secrets_config_path = self.root / SECRETS_CONF_FILENAME
        self.config = yaml.load(config_path.open(), Loader=yaml.FullLoader)
        try:
            self.secrets_config = yaml.load(
                secrets_config_path.open(), Loader=yaml.FullLoader
            )
        except FileNotFoundError:
            self.secrets_config = {}
        self.openedx_version = OpenEdXVersions[
            self.config.get("openedx_version", "koa")
        ]
        source_image_prefix = self.openedx_version.value["docker_image_prefix"]
        self.base_image = self.config.get(
            "base_image", f"{source_image_prefix}-dev:{__version__}"
        )
        self.final_base_image = self.config.get(
            "final_base_image", f"{source_image_prefix}-nostatic:{__version__}"
        )
        if "project_name" not in self.config:
            raise ValueError(f"A project_name was not specified in {config_path}")
        self.name = self.config["project_name"]
        if not re.search("^[0-9a-zA-Z-]+$", self.name):
            raise ValueError(
                f"`{self.name}` is not a valid name: A project_name can only contain letters, numbers and dashes"
            )
        self.image_prefix = self.config.get("image_prefix", f"{self.name}/openedx")
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
            self.requirements_image_name = (
                f"{self.image_prefix}-requirements:{img_hash[:6]}"
            )
            requirements_volumes: Dict[str, str] = {}
            # If the requirements directory contains any symlink we mount
            # their targets individually instead of the whole requirements directory
            for el in self.requirements_dir.iterdir():
                if el.is_symlink():
                    self.requirements_volumes = requirements_volumes
                requirements_volumes[str(el.resolve())] = (
                    "/openedx/derex.requirements/" + el.name
                )
        else:
            self.requirements_image_name = self.base_image

        themes_dir = self.root / "themes"
        if themes_dir.is_dir():
            self.themes_dir = themes_dir
            img_hash = get_dir_hash(
                self.themes_dir
            )  # XXX some files are generated. We should ignore them when we hash the directory
            self.themes_image_name = f"{self.image_prefix}-themes:{img_hash[:6]}"
        else:
            self.themes_image_name = self.requirements_image_name

        settings_dir = self.root / "settings"
        if settings_dir.is_dir():
            self.settings_dir = settings_dir
            # TODO: run some sanity checks on the settings dir and raise an
            # exception if they fail

        fixtures_dir = self.root / "fixtures"
        if fixtures_dir.is_dir():
            self.fixtures_dir = fixtures_dir

        plugins_dir = self.root / "plugins"
        if plugins_dir.is_dir():
            self.plugins_dir = plugins_dir

        openedx_customizations_dir = self.root / "openedx_customizations"
        if openedx_customizations_dir.is_dir():
            self.openedx_customizations_dir = openedx_customizations_dir

        e2e_dir = self.root / "e2e"
        if e2e_dir.is_dir():
            self.e2e_dir = e2e_dir

        self.image_name = self.themes_image_name
        self.materialize_derex_settings = self.config.get(
            "materialize_derex_settings", True
        )

    def update_default_settings(self, default_settings_dir, destination_settings_dir):
        """Update default settings in a specified directory.
        Given a directory where to look for default settings modules, recursively
        copy or update them into the destination directory.
        Additionally add a warning asking not to manually edit files.
        If files needs to be overwritten, print a diff.
        """
        for source in default_settings_dir.glob("**/*.py"):
            destination = destination_settings_dir / source.relative_to(
                default_settings_dir
            )
            new_text = (
                "# DO NOT EDIT THIS FILE!\n"
                "# IT CAN BE OVERWRITTEN ON UPGRADE.\n"
                f"# Generated by derex.runner {__version__}\n\n"
                f"{source.read_text()}"
            )
            if destination.is_file():
                old_text = destination.read_text()
                if old_text != new_text:
                    logger.warning(f"Replacing file {destination} with newer version")
                    diff = tuple(
                        difflib.unified_diff(
                            old_text.splitlines(keepends=True),
                            new_text.splitlines(keepends=True),
                        )
                    )
                    logger.warning("".join(diff))
            else:
                if not destination.parent.is_dir():
                    destination.parent.mkdir(parents=True)
            try:
                destination.write_text(new_text)
            except PermissionError:
                current_mode = stat.S_IMODE(os.lstat(destination).st_mode)
                # XXX Remove me: older versions of derex set a non-writable permission
                # for their files. This except branch is needed now (Easter 2020), but
                # when the pandemic is over we can probably remove it
                destination.chmod(current_mode | 0o700)
                destination.write_text(new_text)

    def _materialize_settings(self):
        """If the project includes user defined settings and
        `materialize_derex_settings` is True for the project then
        copy current derex default settings to the project settings
        directory.
        This is useful to keep track of settings changes between
        version upgrades.
        """
        if self.settings_dir is None or not self.materialize_derex_settings:
            return

        base_settings = self.settings_dir / "base.py"
        if not base_settings.is_file():
            base_settings.write_text("from derex_django.settings.default import *\n")

        self.update_default_settings(
            DEREX_DJANGO_SETTINGS_PATH, self.settings_dir / "derex"
        )

    def get_plugin_directories(self, plugin: str) -> Dict[str, Path]:
        """
        Return a dictionary filled with paths to existing directories
        for custom requirements, settings, fixtures and themes for
        a plugin.
        """
        plugin_directories = {}
        if self.plugins_dir:
            plugin_dir = self.plugins_dir / plugin
            if plugin_dir.exists():
                for directory in ["settings", "requirements", "fixtures", "themes"]:
                    if (plugin_dir / directory).exists():
                        plugin_directories[directory] = plugin_dir / directory
        return plugin_directories

    def get_available_settings(self):
        """Return an Enum object that includes possible settings for this project.
        This enum must be dynamic, since it depends on the contents of the project
        settings directory.
        """
        if self._available_settings is not None:
            return self._available_settings
        available_settings = {"default": "derex_django.settings.default"}
        if self.settings_dir is not None:
            for file in self.settings_dir.iterdir():
                if file.suffix == ".py" and file.stem != "__init__":
                    available_settings[file.stem] = f"derex_settings.{file.stem}"
        available_settings_enum = Enum("ProjectSettings", available_settings)
        self._available_settings = available_settings_enum
        return available_settings_enum

    def get_container_env(self):
        """Return a dictionary to be used as environment variables for all containers
        in this project. Variables are looked up inside the config according to
        the current settings for the project.
        """
        settings = self.settings.name
        result = {}

        for config in [self.config, self.secrets_config]:
            variables = config.get("variables", {})
            for variable in variables:
                value = variables[variable][settings]
                if not isinstance(value, str):
                    result[f"DEREX_JSON_{variable.upper()}"] = json.dumps(value)
                else:
                    result[f"DEREX_{variable.upper()}"] = value
        return result

    def secret(self, name: str) -> str:
        return get_secret(DerexSecrets[name])

    def get_openedx_customizations(self) -> dict:
        """Return a mapping of customized files to be mounted in
        the container in order to replace default edx-platform modules.
        """
        openedx_customizations = {}
        for openedx_customizations_dir in [
            DEREX_OPENEDX_CUSTOMIZATIONS_PATH / self.openedx_version.name,
            self.openedx_customizations_dir,
        ]:
            if openedx_customizations_dir and openedx_customizations_dir.exists():
                for file_path in openedx_customizations_dir.rglob("*"):
                    if file_path.is_file():
                        source = str(file_path)
                        destination = str(file_path).replace(
                            str(openedx_customizations_dir), "/openedx/edx-platform"
                        )
                        openedx_customizations[destination] = source
        return openedx_customizations


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


class DebugBaseImageProject(Project):
    """A project that is always in debug mode and always uses the base image,
    irregardless of the presence of requirements.
    """

    runmode = ProjectRunMode.debug

    @property  # type: ignore
    def requirements_image_name(self):
        return self.base_image

    @requirements_image_name.setter
    def requirements_image_name(self, value):
        pass


class ProjectNotFound(ValueError):
    """No derex project could be found."""
