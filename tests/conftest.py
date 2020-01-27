from pathlib import Path
from tempfile import TemporaryDirectory

import contextlib
import os
import pytest
import sys


# Do not trust the value of __file__ in this module: on Azure it's wrong


@pytest.fixture
def workdir():
    @contextlib.contextmanager
    def workdir_decorator(path: Path):
        """Changes working directory and returns to previous on exit."""
        prev_cwd = Path.cwd()
        os.chdir(path)
        try:
            yield
        finally:
            os.chdir(prev_cwd)

    return workdir_decorator


@pytest.fixture
def sys_argv(mocker):
    @contextlib.contextmanager
    def my_cm(eargs):
        with mocker.mock_module.patch.object(sys, "argv", eargs):
            try:
                yield
            except SystemExit as exc:
                if exc.code != 0:
                    raise

    return my_cm


@pytest.fixture
def testproj(workdir):
    directory = TemporaryDirectory()
    with open("a") as fh:
        fh.write(f"project_name: testminimal")
    return workdir(directory.name)
