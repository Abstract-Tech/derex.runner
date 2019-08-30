from pathlib import Path

import contextlib
import os
import pytest
import sys


MINIMAL_PROJ = Path(__file__).with_name("fixtures") / "minimal"
COMPLETE_PROJ = Path(__file__).with_name("fixtures") / "complete"


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


@pytest.yield_fixture
def minimal_proj():
    prev_cwd = Path.cwd()
    os.chdir(MINIMAL_PROJ)
    try:
        yield
    finally:
        os.chdir(prev_cwd)


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
