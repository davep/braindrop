"""The main application class."""

##############################################################################
# Python imports.
from pathlib import Path

##############################################################################
# Textual imports.
from textual.app import App
from textual.screen import Screen

##############################################################################
# Local imports.
from ..raindrop import Raindrop
from .screens import Main

##############################################################################
class Braindrop(App[None]):
    """The Braindrop application class."""

    def __init__(self):
        """Initialise the application."""
        super().__init__()
        self._api = Raindrop(Path(".test_token").read_text().strip())
        """The API client for Raindrop."""

    def get_default_screen(self) -> Screen:
        """Returns the `Main` screen."""
        return Main(self._api)

### app.py ends here
