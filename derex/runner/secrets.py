"""Tools to deal with secrets in derex.
"""

from collections import Counter
from derex.runner.constants import DEREX_MAIN_SECRET_DEFAULT_MAX_SIZE  # noqa
from derex.runner.constants import DEREX_MAIN_SECRET_DEFAULT_MIN_ENTROPY  # noqa
from derex.runner.constants import DEREX_MAIN_SECRET_DEFAULT_MIN_SIZE  # noqa
from derex.runner.constants import DEREX_MAIN_SECRET_DEFAULT_PATH  # noqa
from typing import Any

import math
import os


def scrypt_hash_stdlib(main_secret: str, name: str) -> bytes:
    from hashlib import scrypt

    return scrypt(
        main_secret.encode("utf-8"),
        salt=name.encode("utf-8"),
        n=2,
        r=8,
        p=1,  # type: ignore
    )


def scrypt_hash_addon(main_secret: str, name: str) -> bytes:
    """ """
    from scrypt import scrypt

    return scrypt.hash(main_secret.encode("utf-8"), name.encode("utf-8"), N=2, r=8, p=1)


try:
    from hashlib import scrypt as _

    scrypt_hash = scrypt_hash_stdlib
except ImportError:
    from scrypt import scrypt as _  # type:ignore  # noqa

    scrypt_hash = scrypt_hash_addon


def get_derex_secrets_env(name: str, vartype: type) -> Any:
    varname = f"DEREX_MAIN_SECRET_{name.upper()}"
    default_varname = f"DEREX_MAIN_SECRET_DEFAULT_{name.upper()}"
    return vartype(os.environ.get(varname, globals()[default_varname]))


def compute_entropy(s: str) -> float:
    """Get entropy of string s.
    Thanks Rosetta code! https://rosettacode.org/wiki/Entropy#Python:_More_succinct_version
    """
    p, lns = Counter(s), float(len(s))
    per_char_entropy = -sum(
        count / lns * math.log(count / lns, 2) for count in p.values()
    )
    return per_char_entropy * len(s)


__all__ = [
    "compute_entropy",
]
