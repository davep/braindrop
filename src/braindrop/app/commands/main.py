"""The main commands used within the application."""

##############################################################################
# Local imports.
from .base import Command


##############################################################################
class ChangeTheme(Command):
    """Change the application's theme"""

    BINDING_KEY = "f9"
    SHOW_IN_FOOTER = False


##############################################################################
class CompactMode(Command):
    "Toggle the compact mode for the Raindrop list"

    BINDING_KEY = "f5"


##############################################################################
class Details(Command):
    """Toggle the view of the current Raindrop's details"""

    BINDING_KEY = "f3"


##############################################################################
class Escape(Command):
    "Back up through the panes, right to left, or exit the app if the navigation pane has focus"

    BINDING_KEY = "escape"
    SHOW_IN_FOOTER = False


##############################################################################
class Help(Command):
    """Show help for and information about the application"""

    BINDING_KEY = "f1, ?"


##############################################################################
class Logout(Command):
    """Forget your API token and remove the local raindrop cache"""

    BINDING_KEY = "f12"
    SHOW_IN_FOOTER = False


##############################################################################
class Quit(Command):
    """Quit the application"""

    BINDING_KEY = "f10, ctrl+q"


##############################################################################
class Redownload(Command):
    "Download a fresh copy of all data from raindrop.io"

    BINDING_KEY = "ctrl+r"
    SHOW_IN_FOOTER = False


##############################################################################
class TagOrder(Command):
    "Toggle the tags sort order between by-name and by-count"

    BINDING_KEY = "f4"


##############################################################################
class VisitRaindrop(Command):
    """Open the web-based raindrop.io application in your default web browser"""

    COMMAND = "Visit raindrop.io"
    BINDING_KEY = "f2"
    FOOTER_TEXT = "raindrop.io"


### main.py ends here
