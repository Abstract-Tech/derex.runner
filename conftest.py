import logging


def pytest_configure(config):
    # Reduce flake8 verbosity as advised in
    # https://github.com/tholo/pytest-flake8/issues/42#issuecomment-504990956
    logging.getLogger("flake8").setLevel(logging.WARN)
