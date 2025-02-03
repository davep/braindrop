"""Provides the main application commands for the command palette."""

##############################################################################
# Textual enhanced imports.
from textual_enhanced.commands import (
    CommandHits,
    CommandsProvider,
    Help,
    Quit,
)

##############################################################################
# Local imports.
from ..commands import (
    AddRaindrop,
    ChangeTheme,
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
from ..data import Raindrops


##############################################################################
class MainCommands(CommandsProvider):
    """Provides some top-level commands for the application."""

    active_collection: Raindrops = Raindrops()
    """The currently-active collection."""

    def commands(self) -> CommandHits:
        """Provide the main application commands for the command palette.

        Yields:
            The commands for the command palette.
        """
        yield AddRaindrop()
        yield ChangeTheme()
        yield CheckTheWaybackMachine()
        yield ClearFilters()
        yield CompactMode()
        yield CopyLinkToClipboard()
        yield DeleteRaindrop()
        yield Details()
        yield Escape()
        yield EditRaindrop()
        yield Help()
        yield Logout()
        yield Quit()
        yield Redownload()
        yield Search()
        yield SearchCollections()
        if self.active_collection.tags:
            yield SearchTags(self.active_collection)
        yield ShowAll()
        yield ShowUnsorted()
        yield ShowUntagged()
        yield TagOrder()
        yield VisitLink()
        yield VisitRaindrop()


### main.py ends here
