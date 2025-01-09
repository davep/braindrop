"""Provides command-oriented messages that relate to the collections."""

##############################################################################
# Local imports.
from .base import Command


##############################################################################
class SearchCollections(Command):
    """Search for a collection by name and show its contents"""

    BINDING_KEY = "C"
    SHOW_IN_FOOTER = False


##############################################################################
class ShowAll(Command):
    """Show all Raindrops"""

    BINDING_KEY = "a"
    SHOW_IN_FOOTER = False


##############################################################################
class ShowUnsorted(Command):
    "Show all unsorted Raindrops"

    BINDING_KEY = "u"
    SHOW_IN_FOOTER = False


##############################################################################
class ShowUntagged(Command):
    """Show all Raindrops that are lacking tags"""

    BINDING_KEY = "U"
    SHOW_IN_FOOTER = False


### collection.py ends here
