"""Provides command-oriented messages that affect the raindrops."""

##############################################################################
# Textual enhanced imports.
from textual_enhanced.commands import Command


##############################################################################
class AddRaindrop(Command):
    """Add a new raindrop"""

    BINDING_KEY = "n"


##############################################################################
class CheckTheWaybackMachine(Command):
    """Check if the currently-highlighted raindrop is archived in the Wayback Machine"""

    BINDING_KEY = "w"


##############################################################################
class CopyLinkToClipboard(Command):
    """Copy the currently-highlighted link to the clipboard"""

    BINDING_KEY = "c"


##############################################################################
class DeleteRaindrop(Command):
    """Delete the currently-highlighted raindrop"""

    BINDING_KEY = "d, delete"


##############################################################################
class EditRaindrop(Command):
    """Edit the currently-highlighted raindrop"""

    BINDING_KEY = "e"


##############################################################################
class VisitLink(Command):
    """Visit currently-highlighted link"""

    BINDING_KEY = "v"


### raindrop.py ends here
