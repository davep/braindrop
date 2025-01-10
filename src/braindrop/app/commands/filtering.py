"""Provides command-oriented messages that relate to filtering."""

##############################################################################
# Python imports.
from dataclasses import dataclass

##############################################################################
# Local imports.
from ..data import Raindrops
from .base import Command


##############################################################################
class ClearFilters(Command):
    """Clear all tags and other filters"""

    BINDING_KEY = "f"
    SHOW_IN_FOOTER = False


##############################################################################
class Search(Command):
    """Search for text anywhere in the raindrops"""

    BINDING_KEY = "/"
    SHOW_IN_FOOTER = False


##############################################################################
@dataclass
class SearchTags(Command):
    """Search for a tag and then filter with it"""

    BINDING_KEY = "t, #"
    SHOW_IN_FOOTER = False

    active_collection: Raindrops = Raindrops()
    """The active collection to search within."""

    @property
    def context_command(self) -> str:
        """The command in context."""
        return "Also tagged..." if self.active_collection.is_filtered else "Tagged..."

    @property
    def context_tooltip(self) -> str:
        """The tooltip in context."""
        return (
            "Add another tag to the current filter"
            if self.active_collection.is_filtered
            else "Filter the current collection with a tag"
        )


### filtering.py ends here
