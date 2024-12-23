"""Collection-oriented commands for the command palette."""

##############################################################################
# Local imports.
from ...raindrop import API, Collection
from ..data import LocalData
from ..messages import ShowCollection
from .commands_provider import CommandHit, CommandHits, CommandsProvider


##############################################################################
class CollectionCommands(CommandsProvider):
    """A command palette provider related to collections."""

    data: LocalData | None = None
    """The local copy of the Raindrop data."""

    def commands(self) -> CommandHits:
        """Provide collection-based command data for the command palette.

        Yields:
            A tuple of the command, the command description and a command
                message to jump to that collection.
        """
        if self.data is None or self.data.user is None:
            return
        pro_features: tuple[Collection, ...] = (
            (API.SpecialCollection.BROKEN(),) if self.data.user.pro else ()
        )
        collections = (
            API.SpecialCollection.ALL(),
            API.SpecialCollection.UNSORTED(),
            API.SpecialCollection.TRASH(),
            *pro_features,
            *self.data.collections,
        )
        for collection in collections:
            yield CommandHit(
                f"Open the '{collection.title}' collection",
                f"Jump to the '{collection.title}' collection and show all related Raindrops",
                ShowCollection(collection),
            )


### collections.py ends here
