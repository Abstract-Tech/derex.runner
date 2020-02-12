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
    from derex.runner.utils import CONF_FILENAME

    directory = TemporaryDirectory("-derex-project")
    with open(f"{directory.name}/{CONF_FILENAME}", "w") as fh:
        fh.write(f"project_name: testminimal\n")
    result = workdir(directory.name)
    # TemporaryDirectory will do its cleanup when it's garbage collected.
    # We attach it to the workdir context manager so that it will be garbage collected
    # together with it.
    result._tmpdir = directory
    return result
