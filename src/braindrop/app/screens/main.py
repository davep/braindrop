"""The main screen for the application."""

##############################################################################
# Python imports.
from webbrowser import open as open_url

##############################################################################
# Textual imports.
from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal
from textual.screen import Screen
from textual.widgets import Footer, Header, Placeholder

##############################################################################
# Local imports.
from ...raindrop import API, User
from ..data import Raindrops
from ..widgets import Navigation


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

    Navigation {
        width: 1fr;
    }

    Placeholder {
        width: 4fr;
    }
    """

    BINDINGS = [
        Binding("f2", "goto_raindrop", "raindrop.io"),
    ]

    def __init__(self, api: API) -> None:
        """Initialise the main screen.

        Args:
            api: The API client object.
        """
        super().__init__()
        self._api = api
        """The API client for Raindrop."""
        self._user: User | None = None
        """Details of the Raindrop user."""
        self._data = Raindrops(api)
        """The local copy of the Raindrop data."""

    def compose(self) -> ComposeResult:
        """Compose the content of the screen."""
        yield Header()
        with Horizontal():
            yield Navigation()
            yield Placeholder()
        yield Footer()

    @work
    async def maybe_redownload(self) -> None:
        """Redownload the Raindrop data if it looks like server data is newer."""

        # First off, get the user information. It's via this where we'll
        # figure out the last server activity and will then be able to
        # figure out if we're out of date down here.
        try:
            self._user = await self._api.user()
        except API.Error:
            self.app.bell()
            self.notify(
                "Unable to get the last updated time from the Raindrop server.",
                title="Server Error",
                severity="error",
                timeout=8,
            )
            return

        # Seems we could not get the user data. All bets are off now.
        if self._user is None:
            self.notify(
                "Could not get user data from Raindrop; aborting download check.",
                title="Server Error",
                severity="error",
                timeout=8,
            )
            return

        if self._data.last_downloaded is None:
            self.notify("No local data found; checking in with the server.")
        elif (
            self._user.last_action is None
            or self._user.last_action > self._data.last_downloaded
        ):
            self.notify(
                "Data on the server appears to be newer; downloading a fresh copy."
            )
        else:
            # It doesn't look like we're in a situation where we need to
            # download data from the server. Display the local copy.
            self.query_one(Navigation).data = self._data
            return

        # Having got to this point, it looks like we really do need to pull
        # data down from the server. Go via the action that the user can use
        # to download everything again.
        await self.run_action("redownload")

    @work(thread=True)
    def load_data(self) -> None:
        """Load the Raindrop data, either from local or remote, depending."""
        self._data.load()
        self.app.call_from_thread(self.maybe_redownload)

    @work
    async def download_data(self) -> None:
        """Download the data from the serer.

        Note:
            As a side-effect the data is saved locally.
        """
        if self._user is None:
            self.app.bell()
            self.notify(
                "Request made to download Raindrop data when the user is unknown.",
                title="Application Error",
                severity="error",
                timeout=8,
            )
            return

        try:
            await self._data.download(self._user)
        except API.Error:
            self.app.bell()
            self.notify(
                "Error downloading data from the server.",
                title="Download Error",
                severity="error",
                timeout=8,
            )
            return

        try:
            self._data.save()
        except OSError as error:
            self.app.bell()
            self.notify(
                f"Error saving the data.\n\n{error}",
                title="Save Error",
                severity="error",
                timeout=8,
            )
            return

        self.query_one(Navigation).data = self._data

    def on_mount(self) -> None:
        """Start the process of loading up the Raindrop data."""
        self.load_data()

    def action_redownload(self) -> None:
        self.download_data()

    def action_goto_raindrop(self) -> None:
        """Open the Raindrop application in the browser."""
        open_url("https://app.raindrop.io/")


### main.py ends here
