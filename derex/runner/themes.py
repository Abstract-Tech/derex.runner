from pathlib import Path


class Theme:
    """
    Simple class to collect info about an OpenedX theme
    """

    name: str
    root: Path

    def __init__(self, root):
        self.root = Path(root)
        if not self.root.is_dir():
            raise RuntimeError("A theme root must be a directory")
        self.name = self.root.name

    def is_lms_theme(self):
        return (self.root / "lms").is_dir()

    def has_lms_static(self):
        return (self.root / "lms" / "static").is_dir()

    def is_cms_theme(self):
        return (self.root / "cms").is_dir()

    def has_cms_static(self):
        return (self.root / "cms" / "static").is_dir()
