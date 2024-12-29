"""Provides the main application commands for the command palette."""

##############################################################################
# Local imports.
from ..data import Raindrops
from ..messages import (
    ClearFilters,
    CompactMode,
    Details,
    Escape,
    Logout,
    Redownload,
    Search,
    SearchCollections,
    SearchTags,
    ShowAll,
    ShowUnsorted,
    TagOrder,
    VisitRaindrop,
)
from .commands_provider import CommandHits, CommandsProvider


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
        yield ClearFilters()
        yield CompactMode()
        yield Details()
        yield Escape()
        yield Logout()
        yield Redownload()
        yield Search()
        yield SearchCollections()
        if self.active_collection.tags:
            yield SearchTags(self.active_collection)
        yield ShowAll()
        yield ShowUnsorted()
        yield TagOrder()
        yield VisitRaindrop()


### main.py ends here
