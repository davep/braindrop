"""The main screen for the application."""

##############################################################################
# Python imports.
from typing import Callable
from webbrowser import open as open_url

##############################################################################
# Pyperclip imports.
from pyperclip import PyperclipException
from pyperclip import copy as to_clipboard

##############################################################################
# Textual imports.
from textual import on, work
from textual.app import ComposeResult
from textual.reactive import var
from textual.widgets import Footer, Header
from textual_enhanced.commands import ChangeTheme, Command, Help, Quit

##############################################################################
# Textual enhanced imports.
from textual_enhanced.dialogs import Confirm, ModalInput
from textual_enhanced.screen import EnhancedScreen

##############################################################################
# Typing extension imports.
from typing_extensions import TypeIs

##############################################################################
# Local imports.
from ... import __version__
from ...raindrop import API, Raindrop, SpecialCollection, User
from ..commands import (
    AddRaindrop,
    CheckTheWaybackMachine,
    ClearFilters,
    CompactMode,
    CopyLinkToClipboard,
    DeleteRaindrop,
    Details,
    EditRaindrop,
    Escape,
    Logout,
    Redownload,
    Search,
    SearchCollections,
    SearchTags,
    ShowAll,
    ShowUnsorted,
    ShowUntagged,
    TagOrder,
    VisitLink,
    VisitRaindrop,
)
from ..data import (
    ExitState,
    LocalData,
    Raindrops,
    load_configuration,
    local_data_file,
    token_file,
    update_configuration,
)
from ..messages import ShowCollection, ShowOfType, ShowTagged
from ..providers import CollectionCommands, MainCommands, TagCommands
from ..widgets import Navigation, RaindropDetails, RaindropsView
from .downloading import Downloading
from .raindrop_input import RaindropInput
from .wayback_checker import WaybackChecker


##############################################################################
class Main(EnhancedScreen[None]):
    """The main screen of the application."""

    TITLE = f"Braindrop v{__version__}"

    HELP = """
    ## Main application keys and commands

    The following keys and commands can be used anywhere here on the main screen.
    """

    DEFAULT_CSS = """
    Main {
        layout: horizontal;

        .panel {
            height: 1fr;
            padding-right: 0;
            border: none;
            border-left: round $border 50%;
            background: $surface;
            scrollbar-gutter: stable;
            scrollbar-background: $surface;
            scrollbar-background-hover: $surface;
            scrollbar-background-active: $surface;
            &:focus, &:focus-within {
                border: none;
                border-left: round $border;
                background: $panel 80%;
                scrollbar-background: $panel;
                scrollbar-background-hover: $panel;
                scrollbar-background-active: $panel;
            }
            &> .option-list--option {
                padding: 0 1;
            }
        }

        Navigation {
            width: 2fr;
        }

        RaindropsView {
            width: 5fr;
            scrollbar-gutter: stable;
        }

        RaindropDetails {
            width: 3fr;
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

    COMMAND_MESSAGES = (
        # Keep these together as they're bound to function keys and destined
        # for the footer.
        Help,
        VisitRaindrop,
        Details,
        TagOrder,
        CompactMode,
        # Everything else.
        AddRaindrop,
        ChangeTheme,
        CheckTheWaybackMachine,
        ClearFilters,
        CopyLinkToClipboard,
        DeleteRaindrop,
        EditRaindrop,
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
        VisitLink,
    )

    BINDINGS = Command.bindings(*COMMAND_MESSAGES)

    COMMANDS = {MainCommands}

    active_collection: var[Raindrops] = var(Raindrops, always_update=True)
    """The currently-active collection."""

    highlighted_raindrop: var[Raindrop | None] = var(None)
    """The currently-highlighted raindrop."""

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
        self._draft_raindrop: Raindrop | None = None
        """Used to hold on to Raindrop data until we know it's been added or edited."""
        self._redownload_wiggle_room = 2
        """The number of seconds difference needs to exist to consider a full redownload."""
        CollectionCommands.data = self._data

    def compose(self) -> ComposeResult:
        """Compose the content of the screen."""
        yield Header()
        yield Navigation(self._api, classes="panel").data_bind(Main.active_collection)
        yield RaindropsView(classes="panel").data_bind(raindrops=Main.active_collection)
        yield RaindropDetails(classes="panel").data_bind(
            raindrop=Main.highlighted_raindrop
        )
        yield Footer()

    @work
    async def maybe_redownload(self) -> None:
        """Redownload the Raindrop data if it looks like server data is newer."""

        # Ensure that whatever we have at the moment is visible.
        self.populate_display()

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

        if self._data.outdated_format:
            self.notify("Local file format has changed; rebuilding from the server.")
        elif self._data.last_downloaded is None:
            self.notify("No local data found; checking in with the server.")
        elif (
            self._user.last_update is not None
            and (self._user.last_update - self._data.last_downloaded).total_seconds()
            > self._redownload_wiggle_room
        ):
            # NOTE: for this check, I'm still undecided if I should be using
            # last_update or last_action. The latter seems more sensible,
            # but I think it can record the last action that *didn't* result
            # in an update (eg: for Pro users it may look if a new link is
            # broken, and so record an action, and then not update because
            # it isn't broken); as such I'm going with last update for now.
            #
            # This may change.
            self.notify(
                "Data on the server appears to be newer; downloading a fresh copy."
            )
        else:
            # It doesn't look like we're in a situation where we need to
            # download data from the server.
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
        self.query_one(RaindropsView).compact = config.compact_mode
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
        self.query_one(RaindropsView).data = self._data
        self.query_one(RaindropDetails).data = self._data
        self.active_collection = self._data.all
        self.query_one(Navigation).highlight_collection(SpecialCollection.ALL())

    @on(ShowCollection)
    def command_show_collection(self, command: ShowCollection) -> None:
        """Handle the command that requests we show a collection.

        Args:
            command: The command.
        """
        self.active_collection = self._data.in_collection(command.collection)
        self.query_one(Navigation).highlight_collection(command.collection)

    def action_search_collections_command(self) -> None:
        """Show the collection-based command palette."""
        self.show_palette(CollectionCommands)

    def action_search_tags_command(self) -> None:
        """Show the tags-based command palette."""
        if self.active_collection.tags:
            self.show_palette(TagCommands)
        else:
            self.notify(
                f"The '{self.active_collection.title}' collection has no tags",
                severity="information",
            )

    @on(ShowOfType)
    def command_show_of_type(self, command: ShowOfType) -> None:
        """handle the command that requests we show Raindrops of a given type.

        Args:
            command: The command.
        """
        self.active_collection = self.active_collection.of_type(command.raindrop_type)

    @on(ShowTagged)
    def command_show_tagged(self, command: ShowTagged) -> None:
        """Handle the command that requests we show Raindrops with a given tag.

        Args:
            command: The command.
        """
        self.active_collection = self.active_collection.tagged(command.tag)

    @on(RaindropsView.Empty)
    def deselect_raindrop(self) -> None:
        """Handle that there is no selected Raindrop."""
        self.highlighted_raindrop = None

    @on(RaindropsView.Highlighted)
    def highlight_raindrop(self, message: RaindropsView.Highlighted) -> None:
        """Handle the highlighted raindrop changing."""
        self.highlighted_raindrop = message.raindrop

    @on(Redownload)
    def action_redownload_command(self) -> None:
        """Redownload data from the server."""
        self.download_data()

    def action_visit_raindrop_command(self) -> None:
        """Open the Raindrop application in the browser."""
        open_url("https://app.raindrop.io/")

    def action_tag_order_command(self) -> None:
        """Toggle the ordering of tags."""
        self.query_one(Navigation).tags_by_count = (
            by_count := not self.query_one(Navigation).tags_by_count
        )
        with update_configuration() as config:
            config.show_tags_by_count = by_count

    def action_show_all_command(self) -> None:
        """Select the collection that shows all Raindrops."""
        self.query_one(Navigation).show_all()

    def action_show_unsorted_command(self) -> None:
        """Select the collection that shows all unsorted Raindrops."""
        self.query_one(Navigation).show_unsorted()

    def action_show_untagged_command(self) -> None:
        """Select the collection that shows all untagged Raindrops."""
        self.query_one(Navigation).show_untagged()

    def action_clear_filters_command(self) -> None:
        """Remove any filtering from the active collection."""
        self.active_collection = self.active_collection.unfiltered

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

    def action_details_command(self) -> None:
        """Toggle the details of the raindrop details view."""
        self.toggle_class("details-hidden")
        if (
            hidden := self.has_class("details-hidden")
            and self.focused is not None
            and self.query_one(RaindropDetails) in (self.focused, self.focused.parent)
        ):
            # Focus was on the details, or within, so let's ensure it heads
            # back to the list of raindrops as that feels like the most
            # logical landing point.
            self.set_focus(self.query_one(RaindropsView))
        with update_configuration() as config:
            config.details_visible = not hidden

    def action_compact_mode_command(self) -> None:
        """Toggle the compact mode for the list of raindrops."""
        self.query_one(RaindropsView).compact = not self.query_one(
            RaindropsView
        ).compact
        with update_configuration() as config:
            config.compact_mode = self.query_one(RaindropsView).compact

    @work
    async def action_search_command(self) -> None:
        """Free-text search within the Raindrops."""
        if search_text := await self.app.push_screen_wait(
            ModalInput("Case-insensitive text to look for in the Raindrops")
        ):
            self.active_collection = self.active_collection.containing(search_text)

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

    def action_quit_command(self) -> None:
        """Quit the application."""
        self.app.exit(ExitState.OKAY)

    def _current_raindrop(self, action: str) -> Raindrop | None:
        """Get the current raindrop.

        Args:
            action: The action that we're getting the raindrop for.

        Returns:
            The highlighted raindrop, or `None`.
        """
        if (raindrop := self.highlighted_raindrop) is None:
            self.notify(
                f"No Raindrop is highlighted, there is nothing to {action}!",
                title="No Raindrop",
                severity="warning",
            )
            return None
        return raindrop

    def _current_link(self, action: str) -> str | None:
        """Get the current link.

        Args:
            action: The action that we're getting the link for.

        Returns:
            The link if there is one, or `None`.
        """
        if (raindrop := self._current_raindrop(action)) is None:
            return None
        if not raindrop.link:
            self.notify(
                f"The highlighted Raindrop doesn't have an associated link to {action}.",
                title="No link",
                severity="warning",
            )
            return None
        return raindrop.link

    def action_visit_link_command(self) -> None:
        """Visit the currently-highlighted link."""
        if (link := self._current_link("visit")) is None:
            return
        open_url(link)

    def action_copy_link_to_clipboard_command(self) -> None:
        """Copy the currently-highlighted link to the clipboard."""

        if (link := self._current_link("copy")) is None:
            return

        # Copy the link to the clipboard using Textual's own facility; this
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

    def action_check_the_wayback_machine_command(self) -> None:
        """Check if the current raindrop is on the Wayback Machine."""
        if (link := self._current_link("check")) is None:
            return
        self.app.push_screen(WaybackChecker(link))

    def _was_not_saved(self, raindrop: Raindrop | None) -> TypeIs[None]:
        """Check if the raindrop data wasn't saved.

        Args:
            raindrop: The raindrop data to check.

        Returns:
            `True` if the data looks saved, `False` if not.

        Notes:
            As a side-effect of calling this method, if the save appears to
            have failed the user will be notified of this.
        """
        if raindrop is None:
            self.notify(
                "Raindrop.io did not confirm the save of the data, try again...",
                title="Save not confirmed",
                severity="warning",
            )
            return True
        return False

    def _locally_refresh(
        self,
        local_save: Callable[[Raindrop], LocalData],
        raindrop: Raindrop,
        confirmation: str,
    ) -> None:
        """Refresh the local state.

        Args:
            local_save: The callable that locally saves the change.
            raindrop: The raindrop causing the refresh.
            confirmation: The message to show the user.
        """
        with self.query_one(Navigation).preserved_highlight:
            # Ensure local storage is updated.
            local_save(raindrop)
            # Get the navigation bar to refresh its content.
            self.query_one(Navigation).data = self._data
            # Remake the active collection from the new data, keeping all
            # filtering intact.
            self.active_collection = self._data.rebuild(self.active_collection)
            # Let the user know what happened.
            self.notify(confirmation)

    @work
    async def action_add_raindrop_command(self) -> None:
        """Add a new Raindrop."""

        # Get the details of the new Raindrop from the user.
        self._draft_raindrop = await self.app.push_screen_wait(
            RaindropInput(self._api, self._data, self._draft_raindrop)
        )
        if self._draft_raindrop is None:
            return

        # They've provided the new details, so now push them to the server.
        # In doing so get the full version of the data back from the server;
        # it's this that we'll actually add locally.
        try:
            added_raindrop = await self._api.add_raindrop(self._draft_raindrop)
        except API.Error as error:
            self.notify(
                str(error),
                title="Error adding new Raindrop",
                severity="error",
                timeout=8,
            )
            return

        # GTFO if it looks like it didn't save.
        if self._was_not_saved(added_raindrop):
            return

        # Reflect the change locally.
        self._locally_refresh(self._data.add, added_raindrop, "Saved")

        # We're safe to drop the draft now.
        self._draft_raindrop = None

    @work
    async def action_edit_raindrop_command(self) -> None:
        """Edit the currently-highlighted raindrop."""

        # Get the highlighted raindrop, or GTFO if we're somehow in here
        # when nothing is highlighted.
        if (raindrop := self._current_raindrop("edit")) is None:
            return

        # For the moment, don't allow editing of uploaded images.
        # https://github.com/davep/braindrop/issues/123
        if raindrop.domain == "up.raindrop.io":
            self.notify(
                "There seems to be a problem with the Raindrop API where, "
                "if you modify a Raindrop associated with an uploaded file, "
                "the uploaded file is lost.\n\n"
                "To ensure your file isn't lost this edit is not permitted.",
                title="Editing of uploads disabled",
                severity="warning",
                timeout=8,
            )
            return

        # If we've got a draft, and it's for the current raindrop...
        if (
            self._draft_raindrop is not None
            and self._draft_raindrop.identity == raindrop.identity
        ):
            # ...let's roll with the draft.
            raindrop = self._draft_raindrop

        # We now have the data we want to edit, throw up the edit dialog.
        self._draft_raindrop = await self.app.push_screen_wait(
            RaindropInput(self._api, self._data, raindrop)
        )
        if self._draft_raindrop is None:
            return

        # The user has confirmed their save, update to the server.
        try:
            updated_raindrop = await self._api.update_raindrop(self._draft_raindrop)
        except API.Error as error:
            self.notify(
                str(error),
                title="Error updating the Raindrop",
                severity="error",
                timeout=8,
            )
            return

        # GTFO if it looks like it didn't save.
        if self._was_not_saved(updated_raindrop):
            return

        # Reflect the change locally.
        self._locally_refresh(self._data.update, updated_raindrop, "Saved")

        # We're safe to drop the draft now.
        self._draft_raindrop = None

    @work
    async def action_delete_raindrop_command(self) -> None:
        """Delete the currently-highlighted raindrop."""

        # Get the highlighted raindrop, or GTFO if we're somehow in here
        # when nothing is highlighted.
        if (raindrop := self._current_raindrop("delete")) is None:
            return

        # Check the user actually wants to do this.
        if not await self.app.push_screen_wait(
            Confirm(
                "Delete Raindrop",
                "Are you sure you want to delete the currently-highlighted Raindrop?",
            )
        ):
            return

        # We know the raindrop, we know the user wants to nuke it. So be
        # it...
        try:
            deleted = await self._api.remove_raindrop(raindrop)
        except API.Error as error:
            self.notify(
                str(error),
                title="Error deleting the Raindrop",
                severity="error",
                timeout=8,
            )
            return

        # Act on how that went down.
        if deleted:
            self._locally_refresh(self._data.delete, raindrop, "Deleted")
        else:
            self.notify(
                "Raindrop.io reported that the delete operation failed.",
                title="Failed to delete",
                severity="error",
                timeout=8,
            )


### main.py ends here
