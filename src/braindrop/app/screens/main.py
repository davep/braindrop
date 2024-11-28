"""The main screen for the application."""

##############################################################################
# Textual imports.
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Footer, Header, Tree

##############################################################################
# Local imports.
from ...raindrop import Raindrop, User


##############################################################################
class Main(Screen):
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
        yield Tree("")
        yield Footer()

    async def on_mount(self) -> None:
        """Populate the screen when it mounts."""
        collections = self.query_one(Tree)
        collections.show_root = False
        for collection in await self._api.collections("root"):
            collections.root.add(collection.title, expand=True)
        collections.root.add_leaf("-----")
        if user := await self._api.user():
            for group in user.groups:
                collections.root.add(group.title)


### main.py ends here
