"""The main screen for the application."""

##############################################################################
# Python imports.
from webbrowser import open as open_url

##############################################################################
# Textual imports.
from textual import on, work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.command import CommandPalette
from textual.containers import Horizontal
from textual.reactive import var
from textual.screen import Screen
from textual.widgets import Footer, Header

##############################################################################
# Local imports.
from ... import __version__
from ...raindrop import API, SpecialCollection, User
from ..commands import CollectionCommands, CommandsProvider, MainCommands, TagCommands
from ..data import (
    ExitState,
    LocalData,
    Raindrops,
    load_configuration,
    local_data_file,
    save_configuration,
    token_file,
)
from ..messages import Logout, SearchCollections, SearchTags, ShowCollection, ShowTagged
from ..widgets import Navigation, RaindropDetails, RaindropsView
from .confirm import Confirm
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

    Main {
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
            border-left: double $border 50%;
            scrollbar-gutter: stable;
            &:focus, &:focus-within {
                border: none;
                border-left: double $border;
            }
        }

        /* For when the details are hidden. */
        &.details-hidden {
            RaindropsView {
                width: 8fr;
            }
            RaindropDetails {
                display: none;
            }
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
            "f3",
            "toggle_details_view",
            "Details",
            tooltip="Toggle the display of the Raindrop details panel",
        ),
        Binding(
            "f4",
            "toggle_tag_order",
            "Tag Order",
            tooltip="Toggle the tags sort order between by-name and by-count",
        ),
        Binding(
            "f5",
            "toggle_compact_mode",
            "Compact",
            tooltip="Toggle the compact mode for the Raindrop list",
        ),
        Logout.binding(),
        Binding(
            "ctrl+r",
            "redownload",
            "Redownload",
            tooltip="Download a fresh copy of all data from raindrop.io",
        ),
        Binding(
            "escape",
            "escape",
            tooltip="Back up through the panes, right to left, or exit the app if the navigation pane has focus",
        ),
    ]

    TITLE = f"Braindrop v{__version__}"

    COMMANDS = {MainCommands}

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
        config = load_configuration()
        self.set_class(not config.details_visible, "details-hidden")
        self.query_one(Navigation).tags_by_count = config.show_tags_by_count
        self.load_data()

    def watch_active_collection(self) -> None:
        """Handle the active collection being changed."""
        if self.active_collection.title:
            self.sub_title = self.active_collection.description
            MainCommands.active_collection = self.active_collection
            TagCommands.active_collection = self.active_collection
        else:
            self.sub_title = "Loading..."

    def populate_display(self) -> None:
        """Populate the display."""
        self.query_one(Navigation).data = self._data
        self.active_collection = self._data.all
        self.query_one(Navigation).highlight_collection(SpecialCollection.ALL())

    def _show_palette(self, provider: type[CommandsProvider]) -> None:
        """Show a particular command palette.

        Args:
            provider: The commands provider for the palette.
        """
        self.app.push_screen(
            CommandPalette(
                providers=(provider,),
                placeholder=provider.prompt(),
            )
        )

    @on(ShowCollection)
    def command_show_collection(self, command: ShowCollection) -> None:
        """Handle the command that requests we show a collection.

        Args:
            command: The command.
        """
        self.active_collection = self._data.in_collection(command.collection)
        self.query_one(Navigation).highlight_collection(command.collection)

    @on(SearchCollections)
    def command_search_collections(self) -> None:
        """Show the collection-based command palette."""
        self._show_palette(CollectionCommands)

    @on(SearchTags)
    def command_search_tags(self) -> None:
        """Show the tags-based command palette."""
        self._show_palette(TagCommands)

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
        self.query_one(Navigation).tags_by_count = (
            by_count := not self.query_one(Navigation).tags_by_count
        )
        config = load_configuration()
        config.show_tags_by_count = by_count
        save_configuration(config)

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
        if self.focused is not None and self.focused.parent is self.query_one(
            RaindropDetails
        ):
            self.set_focus(self.query_one(RaindropDetails))
        elif self.focused is self.query_one(RaindropDetails):
            self.set_focus(self.query_one(RaindropsView))
        elif self.focused is self.query_one(RaindropsView):
            self.set_focus(self.query_one(Navigation))
        else:
            self.app.exit()

    def action_toggle_details_view(self) -> None:
        """Toggle the details of the raindrop details view."""
        self.toggle_class("details-hidden")
        config = load_configuration()
        config.details_visible = not self.has_class("details-hidden")
        save_configuration(config)

    def action_toggle_compact_mode(self) -> None:
        """Toggle the compact mode for the list of raindrops."""
        self.query_one(RaindropsView).compact = not self.query_one(
            RaindropsView
        ).compact

    @work
    async def action_search(self) -> None:
        """Free-text search within the Raindrops."""
        if search_text := await self.app.push_screen_wait(SearchInput()):
            self.active_collection = self.active_collection.containing(search_text)

    @on(Logout)
    @work
    async def action_logout_command(self) -> None:
        """Perform the logout action."""
        if await self.app.push_screen_wait(
            Confirm(
                "Logout",
                "Remove the local copy of your API token and delete the local copy of all your data?",
            )
        ):
            token_file().unlink(True)
            local_data_file().unlink(True)
            self.app.exit(ExitState.TOKEN_FORGOTTEN)


### main.py ends here
