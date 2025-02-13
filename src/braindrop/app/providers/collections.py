"""Collection-oriented commands for the command palette."""

##############################################################################
# Textual enhanced imports.
from textual_enhanced.commands import CommandHit, CommandHits, CommandsProvider

##############################################################################
# Local imports.
from ...raindrop import Collection, SpecialCollection
from ..data import LocalData
from ..messages import ShowCollection


##############################################################################
class CollectionCommands(CommandsProvider):
    """A command palette provider related to collections."""

    data: LocalData | None = None
    """The local copy of the Raindrop data."""

    @classmethod
    def prompt(cls) -> str:
        """The prompt for the command provider."""
        return "Open collection..."

    def commands(self) -> CommandHits:
        """Provide collection-based command data for the command palette.

        Yields:
            The commands for the command palette.
        """
        if self.data is None or self.data.user is None:
            return
        pro_features: tuple[Collection, ...] = (
            (SpecialCollection.BROKEN(),) if self.data.user.pro else ()
        )
        collections = (
            SpecialCollection.ALL(),
            SpecialCollection.UNSORTED(),
            SpecialCollection.UNTAGGED(),
            SpecialCollection.TRASH(),
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
