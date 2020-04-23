"""Tools to deal with secrets in derex.
"""
from pathlib import Path

import logging
import os


logger = logging.getLogger(__name__)


def get_master_secret():
    """Derex uses a master secret to derive all other secrets.
    This functions finds the master secret on the current machine,
    and if it can't find it it will return a default one.

    The default location is `/etc/derex/main_secret`, but can be customized
    via the environment variable DEREX_MAIN_SECRET_PATH.
    """
    filepath = Path(os.environ.get("DEREX_MAIN_SECRET_PATH", "/etc/derex/main_secret"))

    if os.access(filepath, os.R_OK):
        return filepath.read_text().strip()

    if filepath.exists():
        logger.error(f"File filepath is not readable; using default master secret")

    return "Default secret"
