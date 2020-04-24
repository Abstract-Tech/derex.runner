from pathlib import Path

import appdirs


DEREX_DIR = Path(appdirs.user_data_dir(appname="derex"))


def ensure_dir(directory: Path):
    if not directory.exists():
        directory.mkdir(parents=True)
