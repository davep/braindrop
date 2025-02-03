"""Provides the command palette command provides for the application."""

##############################################################################
# Local imports.
from .collections import CollectionCommands
from .main import MainCommands
from .tags import TagCommands

##############################################################################
# Exports.
__all__ = ["CollectionCommands", "MainCommands", "TagCommands"]

### __init__.py ends here
