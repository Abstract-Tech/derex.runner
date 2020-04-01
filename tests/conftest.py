from pathlib import Path
from shutil import copytree
from tempfile import TemporaryDirectory

import contextlib
import os
import pytest
import sys


# Do not trust the value of __file__ in this module: on Azure it's wrong


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


@pytest.fixture
def workdir():
    @contextlib.contextmanager
    def workdir_decorator(path: Path):
        """Creates a copy of the given directory's parent, changes working directory
        to be the copy of the given one and returns to the previous working
        directory on exit."""
        prev_cwd = Path.cwd()
        os.chdir(path)
        try:
            yield path
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
    """Return a context manager that can be used to work inside
    a test project.
    """
    from derex.runner.utils import CONF_FILENAME

    directory = TemporaryDirectory("-derex-project")
    with open(f"{directory.name}/{CONF_FILENAME}", "w") as fh:
        fh.write(f"project_name: testminimal\n")
    result = workdir(Path(directory.name))
    # TemporaryDirectory will do its cleanup when it's garbage collected.
    # We attach it to the workdir context manager so that it will be garbage collected
    # together with it.
    result._tmpdir = directory
    return result
