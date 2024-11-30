"""The main screen for the application."""

##############################################################################
# Textual imports.
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Footer, Header

##############################################################################
# Local imports.
from ...raindrop import Raindrop
from ..widgets import Groups


##############################################################################
class Main(Screen[None]):
    """The main screen of the application."""

    DEFAULT_CSS = """
    Header {
        /* The header icon is ugly and pointless. Remove it. */
        HeaderIcon {
            visibility: hidden;
        }

        /* The tall version of the header is utterly useless. Nuke that. */
        &.-tall {
            height: 1 !important;
        }
    }
    """

    def __init__(self, api: Raindrop) -> None:
        """Initialise the main screen.

        Args:
            api: The API client object.
        """
        super().__init__()
        self._api = api
        """The API client for Raindrop."""

    def compose(self) -> ComposeResult:
        """Compose the content of the screen."""
        yield Header()
        yield Groups(self._api)
        yield Footer()

    async def on_mount(self) -> None:
        """Populate the screen when it mounts."""
        if user := await self._api.user():
            await self.query_one(Groups).show_for_user(user)


### main.py ends here
