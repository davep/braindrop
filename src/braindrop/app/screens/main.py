"""The main screen for the application."""

##############################################################################
# Python imports.
from webbrowser import open as open_url

##############################################################################
# Pyperclip imports.
from pyperclip import PyperclipException
from pyperclip import copy as to_clipboard

##############################################################################
# Textual imports.
from textual import on, work
from textual.app import ComposeResult
from textual.command import CommandPalette
from textual.containers import Horizontal
from textual.reactive import var
from textual.screen import Screen
from textual.widgets import Footer, Header, HelpPanel

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
from ..messages import (
    ChangeTheme,
    CheckTheWaybackMachine,
    ClearFilters,
    Command,
    CompactMode,
    CopyLinkToClipboard,
    Details,
    Escape,
    Help,
    Logout,
    Quit,
    Redownload,
    Search,
    SearchCollections,
    SearchTags,
    ShowAll,
    ShowCollection,
    ShowTagged,
    ShowUnsorted,
    ShowUntagged,
    TagOrder,
    VisitRaindrop,
)
from ..widgets import Navigation, RaindropDetails, RaindropsView
from .confirm import Confirm
from .downloading import Downloading
from .search_input import SearchInput
from .wayback_checker import WaybackChecker


##############################################################################
class Main(Screen[None]):
    """The main screen of the application."""

    TITLE = f"Braindrop v{__version__}"

    DEFAULT_CSS = """
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
            padding-right: 0;
            border: none;
            border-left: round $border 50%;
            scrollbar-gutter: stable;
            scrollbar-background: $surface;
            &:focus, &:focus-within {
                border: none;
                border-left: round $border;
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

    BINDINGS = Command.bindings(
        # Keep these together as they're bound to function keys and destined
        # for the footer.
        Help,
        VisitRaindrop,
        Details,
        TagOrder,
        CompactMode,
        # Everything else.
        ChangeTheme,
        CheckTheWaybackMachine,
        ClearFilters,
        CopyLinkToClipboard,
        Escape,
        Logout,
        Quit,
        Redownload,
        Search,
        SearchCollections,
        SearchTags,
        ShowAll,
        ShowUnsorted,
        ShowUntagged,
    )

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
        # data down from the server. Fire off the redownload command.
        self.post_message(Redownload())

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
    def action_search_collections_command(self) -> None:
        """Show the collection-based command palette."""
        self._show_palette(CollectionCommands)

    @on(SearchTags)
    def action_search_tags_command(self) -> None:
        """Show the tags-based command palette."""
        if self.active_collection.tags:
            self._show_palette(TagCommands)
        else:
            self.notify(
                f"The '{self.active_collection.title}' collection has no tags",
                severity="information",
            )

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

    @on(Redownload)
    def action_redownload_command(self) -> None:
        """Redownload data from the server."""
        self.download_data()

    @on(VisitRaindrop)
    def action_visit_raindrop_command(self) -> None:
        """Open the Raindrop application in the browser."""
        open_url("https://app.raindrop.io/")

    @on(TagOrder)
    def action_tag_order_command(self) -> None:
        """Toggle the ordering of tags."""
        self.query_one(Navigation).tags_by_count = (
            by_count := not self.query_one(Navigation).tags_by_count
        )
        config = load_configuration()
        config.show_tags_by_count = by_count
        save_configuration(config)

    @on(ShowAll)
    def action_show_all_command(self) -> None:
        """Select the collection that shows all Raindrops."""
        self.query_one(Navigation).show_all()

    @on(ShowUnsorted)
    def action_show_unsorted_command(self) -> None:
        """Select the collection that shows all unsorted Raindrops."""
        self.query_one(Navigation).show_unsorted()

    @on(ShowUntagged)
    def action_show_untagged_command(self) -> None:
        """Select the collection that shows all untagged Raindrops."""
        self.query_one(Navigation).show_untagged()

    @on(ClearFilters)
    def action_clear_filters_command(self) -> None:
        """Remove any filtering from the active collection."""
        self.active_collection = self.active_collection.unfiltered

    @on(Escape)
    def action_escape_command(self) -> None:
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

    @on(Details)
    def action_details_command(self) -> None:
        """Toggle the details of the raindrop details view."""
        self.toggle_class("details-hidden")
        config = load_configuration()
        config.details_visible = not self.has_class("details-hidden")
        save_configuration(config)

    @on(CompactMode)
    def action_compact_mode_command(self) -> None:
        """Toggle the compact mode for the list of raindrops."""
        self.query_one(RaindropsView).compact = not self.query_one(
            RaindropsView
        ).compact

    @on(Search)
    @work
    async def action_search_command(self) -> None:
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

    @on(Help)
    def action_help_command(self) -> None:
        """Toggle the display of the help panel."""
        self.call_next(
            self.app.run_action,
            f"{'hide' if self.screen.query(HelpPanel) else 'show'}_help_panel",
        )

    @on(ChangeTheme)
    def action_change_theme_command(self) -> None:
        """Show the theme picker."""
        self.app.search_themes()

    @on(Quit)
    def action_quit_command(self) -> None:
        """Quit the application."""
        self.app.exit(ExitState.OKAY)

    def _current_link(self, action: str) -> str | None:
        """Get the current link.

        Args:
            action: The action that we're getting the link for.

        Returns:
            The link if there is one, or `None`.
        """
        if (raindrop := self.query_one(RaindropsView).highlighted_raindrop) is None:
            self.notify(
                f"No Raindrop is highlighted, there is nothing to {action}!",
                title="No Raindrop",
                severity="warning",
            )
            return None
        if not raindrop.link:
            self.notify(
                f"The highlighted Raindrop doesn't have an associated link to {action}.",
                title="No link",
                severity="warning",
            )
            return None
        return raindrop.link

    @on(CopyLinkToClipboard)
    def action_copy_link_to_clipboard_command(self) -> None:
        """Copy the currently-highlighted link to the clipboard."""

        if (link := self._current_link("copy")) is None:
            return

        # Copy the link tot he clipboard using Textual's own facility; this
        # has the benefit of pushing it through remote connections, where
        # possible.
        self.app.copy_to_clipboard(link)

        # Having done that copy, we'll also try and use pyperclip too. It's
        # possible the user is within a Terminal that doesn't support the
        # Textual approach, so this will belt-and-braces make sure the link
        # gets to some clipboard.
        try:
            to_clipboard(link)
        except PyperclipException:
            self.app.bell()
            self.notify(
                "Clipboard support not available in your environment.",
                severity="error",
            )
        else:
            self.notify("The link has been copied to the clipboard")

    @on(CheckTheWaybackMachine)
    def action_check_the_wayback_machine_command(self) -> None:
        """Check if the current raindrop is on the Wayback Machine."""
        if (link := self._current_link("check")) is None:
            return
        self.app.push_screen(WaybackChecker(link))


### main.py ends here
