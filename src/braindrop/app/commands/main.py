"""Provides the main application commands for the command palette."""

##############################################################################
# Local imports.
from ..data import Raindrops
from ..messages import ClearFilters, Logout, SearchCollections, SearchTags
from .commands_provider import CommandHit, CommandHits, CommandsProvider


##############################################################################
class MainCommands(CommandsProvider):
    """Provides some top-level commands for the application."""

    active_collection: Raindrops = Raindrops()
    """The currently-active collection."""

    def commands(self) -> CommandHits:
        """Provide the main command data for the command palette.

        Yields:
            A tuple of the command, the command description and a command
                message to run the command.
        """
        yield ClearFilters()
        yield CommandHit(
            "Open Raindrop collection...",
            "View all the raindrops in a given collection",
            SearchCollections(),
        )
        if self.active_collection.tags:
            yield CommandHit(
                "Also tagged..." if self.active_collection.is_filtered else "Tagged...",
                "Add another tag to the current filter"
                if self.active_collection.is_filtered
                else "Filter the current collection with a tag",
                SearchTags(),
            )
        yield Logout()


### main.py ends here
