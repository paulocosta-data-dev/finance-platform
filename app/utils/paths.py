import sys
from pathlib import Path


def _project_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).parent.parent.parent


def _resource_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)
    return Path(__file__).parent.parent.parent


def data_path(relative: str) -> Path:
    """User data: parquet files, categories, learned rules.
    Lives next to the exe when packaged; at project root in development."""
    return _project_root() / relative


def resource_path(relative: str) -> Path:
    """Bundled app resource: YAML rules and static configs.
    Extracted from bundle when packaged; at project root in development."""
    return _resource_root() / relative
