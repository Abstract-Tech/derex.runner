class ProjectNotFound(ValueError):
    """No derex project could be found."""


class DerexSecretError(ValueError):
    """The main secret provided to derex is not valid or could not be found."""


class BuildError(RuntimeError):
    """An error occurred while building a docker image"""
