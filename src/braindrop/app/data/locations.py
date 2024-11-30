"""Functions for getting the locations of data."""

##############################################################################
# Python imports.
from pathlib import Path

##############################################################################
# XDG imports.
from xdg_base_dirs import xdg_config_home, xdg_data_home


##############################################################################
def _app_dir(root: Path) -> Path:
    """Given a root, ensure and return the app directory within it.

    Args:
        root: The root directory within which to make/get the directory.

    Returns:
        The full path to the directory.

    Note:
        If the directory doesn't exist, it will be created as a side-effect
        of calling this function.
    """
    (save_to := root / "braindrop").mkdir(parents=True, exist_ok=True)
    return save_to


##############################################################################
def data_dir() -> Path:
    """The path to the data directory for the application.

    Returns:
        The path to the data directory for the application.

    Note:
        If the directory doesn't exist, it will be created as a side-effect
        of calling this function.
    """
    return _app_dir(xdg_data_home())


##############################################################################
def config_dir() -> Path:
    """The path to the configuration directory for the application.

    Returns:
        The path to the configuration directory for the application.

    Note:
        If the directory doesn't exist, it will be created as a side-effect
        of calling this function.
    """
    return _app_dir(xdg_config_home())


### locations.py ends here
