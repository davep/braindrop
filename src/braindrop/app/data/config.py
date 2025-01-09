"""Code relating to the application's configuration file."""

##############################################################################
# Python imports.
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from functools import lru_cache
from json import dumps, loads
from pathlib import Path
from typing import Iterator

##############################################################################
# Local imports.
from .locations import config_dir


##############################################################################
@dataclass
class Configuration:
    """The configuration data for the application."""

    theme: str | None = None
    """The theme for the application."""

    details_visible: bool = True
    """Show the details pane be visible?"""

    show_tags_by_count: bool = False
    """Show the tags ordered by their count?"""

    compact_mode: bool = False
    """Use compact mode?"""


##############################################################################
def configuration_file() -> Path:
    """The path to the file that holds the application configuration.

    Returns:
        The path to the configuration file.
    """
    return config_dir() / "configuration.json"


##############################################################################
def save_configuration(configuration: Configuration) -> Configuration:
    """Save the given configuration.

    Args:
        The configuration to store.

    Returns:
        The configuration.
    """
    load_configuration.cache_clear()
    configuration_file().write_text(
        dumps(asdict(configuration), indent=4), encoding="utf-8"
    )
    return load_configuration()


##############################################################################
@lru_cache(maxsize=None)
def load_configuration() -> Configuration:
    """Load the configuration.

    Returns:
        The configuration.

    Note:
        As a side-effect, if the configuration doesn't exist a default one
        will be saved to storage.

        This function is designed so that it's safe and low-cost to
        repeatedly call it. The configuration is cached and will only be
        loaded from storage when necessary.
    """
    source = configuration_file()
    return (
        Configuration(**loads(source.read_text(encoding="utf-8")))
        if source.exists()
        else save_configuration(Configuration())
    )


##############################################################################
@contextmanager
def update_configuration() -> Iterator[Configuration]:
    """Context manager for updating the configuration.

    Loads the configuration and makes it available, then ensures it is
    saved.

    Example:
        ```python
        with update_configuration() as config:
            config.meaning = 42
        ```
    """
    configuration = load_configuration()
    try:
        yield configuration
    finally:
        save_configuration(configuration)


### config.py ends here
