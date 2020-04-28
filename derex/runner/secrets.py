"""Tools to deal with secrets in derex.
"""
from base64 import b64encode
from collections import Counter
from enum import Enum
from hashlib import scrypt
from pathlib import Path
from typing import Any
from typing import Optional

import logging
import math
import os


logger = logging.getLogger(__name__)


DEREX_MAIN_SECRET_MAX_SIZE = 1024
DEREX_MAIN_SECRET_MIN_SIZE = 8
DEREX_MAIN_SECRET_MIN_ENTROPY = 128
DEREX_MAIN_SECRET_PATH = "/etc/derex/main_secret"


class DerexSecrets(Enum):
    minio = "minio"


def get_var(name: str, vartype: type) -> Any:
    varname = f"DEREX_MAIN_SECRET_{name.upper()}"
    return vartype(os.environ.get(varname, globals()[varname]))


def _get_master_secret() -> Optional[str]:
    """Derex uses a master secret to derive all other secrets.
    This functions finds the master secret on the current machine,
    and if it can't find it it will return a default one.

    The default location is `/etc/derex/main_secret`, but can be customized
    via the environment variable DEREX_MAIN_SECRET_PATH.
    """
    filepath = get_var("path", Path)
    max_size = get_var("max_size", int)
    min_size = get_var("min_size", int)
    min_entropy = get_var("min_entropy", int)

    if os.access(filepath, os.R_OK):
        master_secret = filepath.read_text().strip()
        if len(master_secret) > max_size:
            raise DerexSecretError(
                f"Master secret in {filepath} is too large: {len(master_secret)} (should be {max_size} at most)"
            )
        if len(master_secret) < min_size:
            raise DerexSecretError(
                f"Master secret in {filepath} is too small: {len(master_secret)} (should be {min_size} at least)"
            )
        if compute_entropy(master_secret) < min_entropy:
            raise DerexSecretError(
                f"Master secret in {filepath} has not enough entropy: {compute_entropy(master_secret)} (should be {min_entropy} at least)"
            )
        return master_secret

    if filepath.exists():
        logger.error(f"File filepath is not readable; using default master secret")
    return None


def get_secret(secret: DerexSecrets) -> str:
    """Derive a secret using the master secret and the provided name.
    """
    binary_secret = scrypt(
        MASTER_SECRET.encode("utf-8"), salt=secret.name.encode("utf-8"), n=2, r=8, p=1  # type: ignore
    )
    # Pad the binary string so that its length is a multiple of 3
    # This will make sure its base64 representation is equals-free
    new_length = len(binary_secret) + (3 - len(binary_secret) % 3)
    return b64encode(binary_secret.rjust(new_length, b" ")).decode()


class DerexSecretError(ValueError):
    """The master secret provided to derex is not valid or could not be found.
    """


def compute_entropy(s: str) -> float:
    """Get entropy of string s.
    Thanks Rosetta code! https://rosettacode.org/wiki/Entropy#Python:_More_succinct_version
    """
    p, lns = Counter(s), float(len(s))
    per_char_entropy = -sum(
        count / lns * math.log(count / lns, 2) for count in p.values()
    )
    return per_char_entropy * len(s)


_MASTER_SECRET = _get_master_secret()
if _MASTER_SECRET is None:
    _MASTER_SECRET = "Default secret"
    HAS_MASTER_SECRET = False
else:
    HAS_MASTER_SECRET = True

MASTER_SECRET = _MASTER_SECRET
"The main secret derex uses to derive all other secrets"

__all__ = [
    "MASTER_SECRET",
    "compute_entropy",
    "DerexSecretError",
    "DerexSecrets",
    "get_secret",
]
