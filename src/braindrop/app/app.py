"""The main application class."""

##############################################################################
# Python imports.
from pathlib import Path

##############################################################################
# Textual imports.
from textual.app import App

##############################################################################
# Local imports.
from ..raindrop import Raindrop

##############################################################################
class Braindrop(App[None]):
    """The Braindrop application class."""

    def __init__(self):
        """Initialise the application."""
        super().__init__()
        self._api = Raindrop(Path(".test_token").read_text().strip())
        """The API client for Raindrop."""


### app.py ends here
