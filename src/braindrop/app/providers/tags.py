"""Tag filtering commands for the command palette."""

##############################################################################
# Textual enhanced imports.
from textual_enhanced.commands import CommandHit, CommandHits, CommandsProvider

##############################################################################
# Local imports.
from ..data import Raindrops, TagCount
from ..messages import ShowTagged


##############################################################################
class TagCommands(CommandsProvider):
    """A command palette provider related to tags."""

    active_collection: Raindrops = Raindrops()
    """The currently-active collection to get the tags from."""

    @classmethod
    def prompt(cls) -> str:
        """The prompt for the command provider."""
        return (
            "Also search for Raindrops tagged with..."
            if cls.active_collection.is_filtered
            else "Search for Raindrops tagged with..."
        )

    def commands(self) -> CommandHits:
        """Provide the tag-based command data for the command palette.

        Yields:
            The commands for the command palette.
        """
        help_prefix = "Also filter" if self.active_collection.is_filtered else "Filter"
        command_prefix = (
            "Also tagged" if self.active_collection.is_filtered else "Tagged"
        )
        for tag in sorted(self.active_collection.tags, key=TagCount.the_tag()):
            yield CommandHit(
                f"{command_prefix} {tag.tag}",
                f"{help_prefix} to Raindrops tagged with {tag.tag} (narrows down to {tag.count})",
                ShowTagged(tag.tag),
            )


### tags.py ends here
