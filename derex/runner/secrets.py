"""Tools to deal with secrets in derex.
"""
from base64 import b64encode
from hashlib import scrypt
from pathlib import Path

import logging
import os


logger = logging.getLogger(__name__)


DEREX_MAIN_SECRET_MAX_SIZE = 1024
DEREX_MAIN_SECRET_PATH = "/etc/derex/main_secret"


def get_master_secret() -> str:
    """Derex uses a master secret to derive all other secrets.
    This functions finds the master secret on the current machine,
    and if it can't find it it will return a default one.

    The default location is `/etc/derex/main_secret`, but can be customized
    via the environment variable DEREX_MAIN_SECRET_PATH.
    """
    filepath = Path(os.environ.get("DEREX_MAIN_SECRET_PATH", DEREX_MAIN_SECRET_PATH))
    max_size = int(
        os.environ.get("DEREX_MAIN_SECRET_MAX_SIZE", DEREX_MAIN_SECRET_MAX_SIZE)
    )

    if os.access(filepath, os.R_OK):
        master_secret = filepath.read_text().strip()
        assert (
            len(master_secret) < max_size
        ), f"Master secret in {filepath} is too large: {len(master_secret)}"
        return master_secret

    if filepath.exists():
        logger.error(f"File filepath is not readable; using default master secret")

    return "Default secret"


def get_secret(name: str) -> str:
    """Derive a secret using the master secret and the provided name.
    """
    master_secret = get_master_secret()
    binary_secret = scrypt(
        master_secret.encode("utf-8"), salt=name.encode("utf-8"), n=2, r=8, p=1
    )
    # Pad the binary string so that its length is a multiple of 3
    # This will make sure its base64 representation is equals-free
    new_length = len(binary_secret) + (3 - len(binary_secret) % 3)
    return b64encode(binary_secret.rjust(new_length, b" ")).decode()
