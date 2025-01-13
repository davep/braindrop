"""Provides functions and classes for managing the app's data."""

##############################################################################
# Local imports.
from .config import (
    configuration_file,
    load_configuration,
    save_configuration,
    update_configuration,
)
from .exit_state import ExitState
from .local import LocalData, local_data_file
from .raindrops import Raindrops, TagCount, TypeCount
from .token import token_file

##############################################################################
# Exports.
__all__ = [
    "configuration_file",
    "ExitState",
    "load_configuration",
    "local_data_file",
    "LocalData",
    "Raindrops",
    "TagCount",
    "TypeCount",
    "save_configuration",
    "token_file",
    "update_configuration",
]


### __init__.py ends here
