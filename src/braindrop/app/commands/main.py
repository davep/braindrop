"""The main commands used within the application."""

##############################################################################
# Textual enhanced imports.
from textual_enhanced.commands import Command


##############################################################################
class ChangeTheme(Command):
    """Change the application's theme"""

    BINDING_KEY = "f9"


##############################################################################
class CompactMode(Command):
    "Toggle the compact mode for the Raindrop list"

    BINDING_KEY = "f5"
    SHOW_IN_FOOTER = True


##############################################################################
class Details(Command):
    """Toggle the view of the current Raindrop's details"""

    BINDING_KEY = "f3"
    SHOW_IN_FOOTER = True


##############################################################################
class Escape(Command):
    "Back up through the panes, right to left, or exit the app if the navigation pane has focus"

    BINDING_KEY = "escape"


##############################################################################
class Logout(Command):
    """Forget your API token and remove the local raindrop cache"""

    BINDING_KEY = "f12"


##############################################################################
class Redownload(Command):
    "Download a fresh copy of all data from raindrop.io"

    BINDING_KEY = "ctrl+r"


##############################################################################
class TagOrder(Command):
    "Toggle the tags sort order between by-name and by-count"

    BINDING_KEY = "f4"
    SHOW_IN_FOOTER = True


##############################################################################
class VisitRaindrop(Command):
    """Open the web-based raindrop.io application in your default web browser"""

    COMMAND = "Visit raindrop.io"
    BINDING_KEY = "f2"
    FOOTER_TEXT = "raindrop.io"
    SHOW_IN_FOOTER = True


### main.py ends here
