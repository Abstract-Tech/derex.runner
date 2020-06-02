"""
Custom pyinstaller hooks for derex.runner
"""

from PyInstaller.utils.hooks import collect_data_files
from PyInstaller.utils.hooks import copy_metadata


datas = copy_metadata("derex.runner")
datas += collect_data_files("derex.runner")
datas += collect_data_files("compose", include_py_files=True)
