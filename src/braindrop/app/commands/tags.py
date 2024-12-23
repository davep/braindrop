"""Tag filtering commands for the command palette."""

##############################################################################
# Local imports.
from ..data import Raindrops
from ..messages import ShowTagged
from .commands_provider import CommandHit, CommandHits, CommandsProvider


##############################################################################
class TagCommands(CommandsProvider):
    """A command palette provider related to tags."""

    active_collection: Raindrops = Raindrops()
    """The currently-active collection to get the tags from."""

    def commands(self) -> CommandHits:
        """Provide the tag-based command data for the command palette.

        Yields:
            A tuple of the command, the command description and a command
                message to filter to the tag.
        """
        help_prefix = "Also filter" if self.active_collection.is_filtered else "Filter"
        command_prefix = (
            "Also tagged" if self.active_collection.is_filtered else "Tagged"
        )
        for tag in self.active_collection.tags:
            yield CommandHit(
                f"{command_prefix} {tag.tag}",
                f"{help_prefix} to Raindrops tagged with {tag.tag} (narrows down to {tag.count})",
                ShowTagged(tag.tag),
            )


### tags.py ends here
