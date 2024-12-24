"""The main screen for the application."""

##############################################################################
# Python imports.
from webbrowser import open as open_url

##############################################################################
# Textual imports.
from textual import on, work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal
from textual.reactive import var
from textual.screen import Screen
from textual.widgets import Footer, Header

##############################################################################
# Local imports.
from ... import __version__
from ...raindrop import API, User
from ..commands import CollectionCommands, TagCommands
from ..data import LocalData, Raindrops
from ..messages import ShowCollection, ShowTagged
from ..widgets import Navigation, RaindropDetails, RaindropsView
from .downloading import Downloading
from .search_input import SearchInput


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
        width: 2fr;
        height: 1fr;
        &> .option-list--option {
            padding: 0 1;
        }
    }

    RaindropsView {
        width: 5fr;
        height: 1fr;
        &> .option-list--option {
            padding: 0 1;
        }
    }

    RaindropDetails {
        width: 3fr;
        height: 1fr;
    }

    .focus {
        border: none;
        border-left: tall $border-blurred;
        &:focus {
            border: none;
            border-left: tall $border;
        }
    }
    """

    BINDINGS = [
        Binding(
            Navigation.SHORTCUT_ALL,
            "show_all",
            tooltip="Show all Raindrops",
        ),
        Binding(
            Navigation.SHORTCUT_UNSORTED,
            "show_unsorted",
            tooltip="Show all unsorted Raindrops",
        ),
        Binding(
            "c",
            "clear_filters",
            tooltip="Clear tags and other filters",
        ),
        Binding(
            "/",
            "search",
            "Search",
            tooltip="Search for text anywhere in the raindrops",
        ),
        Binding(
            "f2",
            "goto_raindrop",
            "raindrop.io",
            tooltip="Open the web-based raindrop.io application",
        ),
        Binding(
            "f4",
            "toggle_tag_order",
            "Tag Order",
            tooltip="Toggle the tags sort order between by-name and by-count",
        ),
        Binding(
            "ctrl+r",
            "redownload",
            "Redownload",
            tooltip="Download a fresh copy of all data from raindrop.io",
        ),
        Binding("escape", "escape"),
    ]

    TITLE = f"Braindrop v{__version__}"

    COMMANDS = {CollectionCommands, TagCommands}

    active_collection: var[Raindrops] = var(Raindrops, always_update=True)
    """The currently-active collection."""

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
        self._data = LocalData(api)
        """The local copy of the Raindrop data."""
        CollectionCommands.data = self._data

    def compose(self) -> ComposeResult:
        """Compose the content of the screen."""
        yield Header()
        with Horizontal():
            yield Navigation(self._api, classes="focus").data_bind(
                Main.active_collection
            )
            yield RaindropsView(classes="focus").data_bind(
                raindrops=Main.active_collection
            )
            yield RaindropDetails(classes="focus")
        yield Footer()

    @work
    async def maybe_redownload(self) -> None:
        """Redownload the Raindrop data if it looks like server data is newer."""

        # First off, get the user information. It's via this where we'll
        # figure out the last server activity and will then be able to
        # figure out if we're out of date down here.
        try:
            self._user = await self._api.user()
        except API.Error as error:
            self.app.bell()
            self.notify(
                f"Unable to get the last updated time from the Raindrop server.\n\n{error}",
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
            self.populate_display()
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
        await self.app.push_screen_wait(Downloading(self._user, self._data))
        self.populate_display()

    def on_mount(self) -> None:
        """Start the process of loading up the Raindrop data."""
        self.load_data()

    def watch_active_collection(self) -> None:
        """Handle the active collection being changed."""
        if self.active_collection.title:
            self.sub_title = self.active_collection.description
            TagCommands.active_collection = self.active_collection
        else:
            self.sub_title = "Loading..."

    def populate_display(self) -> None:
        """Populate the display."""
        self.query_one(Navigation).data = self._data
        self.active_collection = self._data.all
        self.query_one(Navigation).highlight_collection(API.SpecialCollection.ALL())

    @on(ShowCollection)
    def command_show_collection(self, command: ShowCollection) -> None:
        """Handle the command that requests we show a collection.

        Args:
            command: The command.
        """
        self.active_collection = self._data.in_collection(command.collection)
        self.query_one(Navigation).highlight_collection(command.collection)

    @on(ShowTagged)
    def command_show_tagged(self, command: ShowTagged) -> None:
        """Handle the command that requests we show Raindrops with a given tag.

        Args:
            command: The command.
        """
        self.active_collection = self.active_collection.tagged(command.tag)

    @on(RaindropsView.OptionHighlighted)
    def update_details(self) -> None:
        """Update the details panel to show the current raindrop."""
        self.query_one(RaindropDetails).raindrop = self.query_one(
            RaindropsView
        ).highlighted_raindrop

    def action_redownload(self) -> None:
        """Redownload data from the server."""
        self.download_data()

    def action_goto_raindrop(self) -> None:
        """Open the Raindrop application in the browser."""
        open_url("https://app.raindrop.io/")

    def action_toggle_tag_order(self) -> None:
        """Toggle the ordering of tags."""
        self.query_one(Navigation).tags_by_count = not self.query_one(
            Navigation
        ).tags_by_count

    def action_show_all(self) -> None:
        """Select the collection that shows all Raindrops."""
        self.query_one(Navigation).show_all()

    def action_show_unsorted(self) -> None:
        """Select the collection that shows all unsorted Raindrops."""
        self.query_one(Navigation).show_unsorted()

    def action_clear_filters(self) -> None:
        """Remove any filtering from the active collection."""
        self.active_collection = self.active_collection.unfiltered

    def action_escape(self) -> None:
        """Handle escaping.

        The action's approach is to step-by-step back out from the 'deepest'
        level to the topmost, and if we're at the topmost then exit the
        application.
        """
        if self.focused is self.query_one(RaindropsView):
            self.set_focus(self.query_one(Navigation))
        else:
            self.app.exit()

    @work
    async def action_search(self) -> None:
        """Free-text search within the Raindrops."""
        if search_text := await self.app.push_screen_wait(SearchInput()):
            self.active_collection = self.active_collection.containing(search_text)


### main.py ends here
