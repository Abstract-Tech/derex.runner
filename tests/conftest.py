from pathlib import Path
from shutil import copytree
from tempfile import TemporaryDirectory

import contextlib
import logging
import os
import pytest
import sys
import traceback


DEREX_TEST_USER = "derex_test_user"


# Do not trust the value of __file__ in this module: on Azure it's wrong


@pytest.fixture
def workdir():
    @contextlib.contextmanager
    def workdir_decorator(path: Path):
        """Changes working directory to the given one.
        Returns to the previous working directory on exit."""
        prev_cwd = Path.cwd()
        os.chdir(path)
        try:
            yield path
        finally:
            os.chdir(prev_cwd)

    return workdir_decorator


@pytest.fixture
def workdir_copy():
    @contextlib.contextmanager
    def workdir_decorator(path: Path):
        """Creates a copy of the given directory's parent, changes working directory
        to be the copy of the given one and returns to the previous working
        directory on exit."""
        prev_cwd = Path.cwd()
        tmpdir = TemporaryDirectory("", "derex-test-")
        copy_dest = Path(tmpdir.name) / path.parent.name
        new_path = copy_dest / path.name

        copytree(path.parent, str(copy_dest), symlinks=True)
        os.chdir(new_path)
        try:
            yield new_path
        finally:
            os.chdir(prev_cwd)
            tmpdir.cleanup()

    return workdir_decorator


@pytest.fixture(params=["ironwood", "juniper"])
def minimal_project(request, workdir_copy):
    """Return a context manager that can be used to work inside
    a minimal project.
    """
    return workdir_copy(
        Path(__file__).parent.with_name("examples") / request.param / "minimal"
    )


@pytest.fixture(params=["ironwood", "juniper"])
def complete_project(request, workdir_copy):
    """Return a context manager that can be used to work inside
    a complete project.
    """
    return workdir_copy(
        Path(__file__).parent.with_name("examples") / request.param / "complete"
    )


@pytest.fixture(scope=("session"))
def sys_argv(session_mocker):
    @contextlib.contextmanager
    def my_cm(eargs):
        with session_mocker.mock_module.patch.object(sys, "argv", eargs):
            try:
                yield
            except SystemExit as exc:
                if exc.code != 0:
                    raise

    return my_cm


def pytest_configure(config):
    # Reduce flake8 verbosity as advised in
    # https://github.com/tholo/pytest-flake8/issues/42#issuecomment-504990956
    logging.getLogger("flake8").setLevel(logging.WARN)


def assert_result_ok(result):
    """Makes sure the click script exited on purpose, and not by accident
    because of an exception.
    """
    if not isinstance(result.exc_info[1], SystemExit):
        tb_info = "\n".join(traceback.format_tb(result.exc_info[2]))
        assert result.exit_code == 0, tb_info
