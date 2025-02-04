"""Provides command-oriented messages that relate to the collections."""

##############################################################################
# Textual enhanced imports.
from textual_enhanced.commands import Command


##############################################################################
class SearchCollections(Command):
    """Search for a collection by name and show its contents"""

    BINDING_KEY = "C"


##############################################################################
class ShowAll(Command):
    """Show all Raindrops"""

    BINDING_KEY = "a"


##############################################################################
class ShowUnsorted(Command):
    "Show all unsorted Raindrops"

    BINDING_KEY = "u"


##############################################################################
class ShowUntagged(Command):
    """Show all Raindrops that are lacking tags"""

    BINDING_KEY = "U"


### collection.py ends here
