"""
Custom pyinstaller hooks for derex.runner
"""

from PyInstaller.utils.hooks import collect_data_files
from PyInstaller.utils.hooks import copy_metadata


datas = copy_metadata("derex.runner")
datas += collect_data_files("derex.runner")
datas += collect_data_files("compose", include_py_files=True)

try:
    import _scrypt  # type: ignore # noqa: F403,F401

    binaries = [(_scrypt.__file__, ".")]
except ImportError:
    pass
