"""Provides command-oriented messages that affect the raindrops."""

##############################################################################
# Local imports.
from .base import Command


##############################################################################
class AddRaindrop(Command):
    """Add a new raindrop"""

    BINDING_KEY = "n"
    SHOW_IN_FOOTER = False


##############################################################################
class CheckTheWaybackMachine(Command):
    """Check if the currently-highlighted raindrop is archived in the Wayback Machine"""

    BINDING_KEY = "w"
    SHOW_IN_FOOTER = False


##############################################################################
class CopyLinkToClipboard(Command):
    """Copy the currently-highlighted link to the clipboard"""

    BINDING_KEY = "c"
    SHOW_IN_FOOTER = False


##############################################################################
class DeleteRaindrop(Command):
    """Delete the currently-highlighted raindrop"""

    BINDING_KEY = "d, delete"
    SHOW_IN_FOOTER = False


##############################################################################
class EditRaindrop(Command):
    """Edit the currently-highlighted raindrop"""

    BINDING_KEY = "e"
    SHOW_IN_FOOTER = False


##############################################################################
class VisitLink(Command):
    """Visit currently-highlighted link"""

    BINDING_KEY = "v"
    SHOW_IN_FOOTER = False


### raindrop.py ends here
