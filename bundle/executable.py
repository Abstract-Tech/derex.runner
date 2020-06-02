#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Executable bridge to derex and ddc-project/ddc-services.

It can be symlinked and will invoke a different script according
to the symlink name.
"""
from derex.runner import ddc
from derex.runner.cli import derex
from pathlib import Path

import sys


SCRIPTS = {
    "derex": derex,
    "ddc-services": ddc.ddc_services,
    "ddc-project": ddc.ddc_project,
}


if __name__ == "__main__":
    name = Path(sys.argv[0]).name
    if name not in SCRIPTS:
        raise ValueError(
            f"The symlink to this script should have one of these names: {', '.join(SCRIPTS)}"
        )
    SCRIPTS[name]()
