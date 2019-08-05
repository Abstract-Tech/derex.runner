import os
import pkg_resources
from typing import List, Dict, Callable
import pluggy
from derex import runner
from derex.runner import hookimpl
from derex.runner.utils import asbool


class BaseConfig:
    def __compose_path(self, name: str) -> str:
        """Given a docker compose file name return its path
        inside this package.
        """
        return pkg_resources.resource_filename(__name__, f"compose_files/{name}")

    def yaml_opts_services(self) -> List[str]:
        """Return a list of strings pointing to docker-compose yml files suitable
        to be passed as options to docker-compose.
        The compose file includes services needed to run Open edX (mysql. mongodb etc)
        and (if not disabled) administrative tools.
        The list looks like:
        ['-f', '/path/to/docker-compose.yml', '-f', '/path/to/another-docker-compose.yml']
        """
        result = ["-f", self.__compose_path("services.yml")]
        if asbool(os.environ.get("DEREX_ADMIN_SERVICES", True)):
            result += ["-f", self.__compose_path("admin.yml")]
        return result

    def yaml_opts_openedx(self) -> List[str]:
        """Return a list of strings pointing to docker-compose yml files suitable
        to be passed as options to docker-compose.
        The compose file includes Open edX services (lms, cms, workers)
        The list looks like:
        ['-f', '/path/to/docker-compose.yml', '-f', '/path/to/another-docker-compose.yml']
        """
        return ["-f", self.__compose_path("ironwood.yml")]

    @runner.hookimpl
    def settings(self) -> Dict[str, Callable]:
        """Return a dict mapping service variants to callables.
        Callables should return a list of strings pointing to docker-compose yml files
        suitable to be passed as options to docker-compose.
        """
        return {"services": self.yaml_opts_services, "openedx": self.yaml_opts_openedx}
