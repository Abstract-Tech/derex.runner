"""
Custom pyinstaller hooks for derex.runner
"""

from PyInstaller.utils.hooks import collect_data_files
from PyInstaller.utils.hooks import copy_metadata


datas = copy_metadata("derex.runner")
datas += collect_data_files("derex.runner")
datas += collect_data_files("compose", include_py_files=True)

try:
    import scrypt  # type: ignore # noqa: F403,F401

    datas += copy_metadata("scrypt")
    datas += collect_data_files("scrypt", include_py_files=True)
except ImportError:
    pass
