from pathlib import Path

import contextlib
import os


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
