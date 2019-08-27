from pathlib import Path

import contextlib
import os
import pytest
import sys


MINIMAL_PROJ = Path(__file__).parent / "fixtures" / "minimal"
COMPLETE_PROJ = Path(__file__).parent / "fixtures" / "complete"


@contextlib.contextmanager
def working_directory(path: Path):
    """Changes working directory and returns to previous on exit."""
    prev_cwd = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(prev_cwd)


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
