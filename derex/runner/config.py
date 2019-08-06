import os
from typing import List, Dict, Callable
import pluggy
from derex import runner
from derex.runner import hookimpl
from derex.runner.utils import asbool, compose_path


class BaseConfig:
    def yaml_opts_services(self) -> List[str]:
        """Return a list of strings pointing to docker-compose yml files suitable
        to be passed as options to docker-compose.
        The compose file includes services needed to run Open edX (mysql. mongodb etc)
        and (if not disabled) administrative tools.
        The list looks like:
        ['-f', '/path/to/docker-compose.yml', '-f', '/path/to/another-docker-compose.yml']
        """
        result = ["-f", compose_path("services.yml")]
        if asbool(os.environ.get("DEREX_ADMIN_SERVICES", True)):
            result += ["-f", compose_path("admin.yml")]
        return result

    def yaml_opts_openedx(self) -> List[str]:
        """Return a list of strings pointing to docker-compose yml files suitable
        to be passed as options to docker-compose.
        The compose file includes Open edX services (lms, cms, workers)
        The list looks like:
        ['-f', '/path/to/docker-compose.yml', '-f', '/path/to/another-docker-compose.yml']
        """
        return ["-f", compose_path("ironwood.yml")]

    @runner.hookimpl
    def settings(self) -> Dict[str, Callable]:
        """Return a dict mapping service variants to callables.
        Callables should return a list of strings pointing to docker-compose yml files
        suitable to be passed as options to docker-compose.
        """
        return {"services": self.yaml_opts_services, "openedx": self.yaml_opts_openedx}
