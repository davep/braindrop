"""Tag filtering commands for the command palette."""

##############################################################################
# Python imports.
from functools import partial
from typing import AsyncIterator

##############################################################################
# Textual imports.
from textual.command import DiscoveryHit, Hit, Hits, Provider

##############################################################################
# Local imports.
from ..data import Raindrops
from ..messages import ShowTagged


##############################################################################
class TagCommands(Provider):
    active_collection: Raindrops = Raindrops()
    """The currently-active collection to get the tags from."""

    async def _tag_commands(self) -> AsyncIterator[tuple[str, str, ShowTagged]]:
        """Provide the tag-based command data for the command palette.

        Yields:
            A tuple of the command, the tag and a command message to filter to the tag.
        """
        help_prefix = "Also filter" if self.active_collection.is_filtered else "Filter"
        command_prefix = (
            "Also tagged" if self.active_collection.is_filtered else "Tagged"
        )
        for tag in self.active_collection.tags:
            yield (
                f"{command_prefix} {tag.tag}",
                f"{help_prefix} to Raindrops tagged with {tag.tag} (narrows down to {tag.count})",
                ShowTagged(tag.tag),
            )

    async def discover(self) -> Hits:
        """Handle a request to discover commands.

        Yields:
            Command discovery hits for the command palette.
        """
        async for command, description, message in self._tag_commands():
            yield DiscoveryHit(
                command,
                partial(self.screen._post_message, message),
                help=description,
            )

    async def search(self, query: str) -> Hits:
        """Handle a request to search for commands that match the query.

        Args:
            query: The query from the user.

        Yields:
            Command hits for the command palette.
        """
        matcher = self.matcher(query)
        async for command, description, message in self._tag_commands():
            if match := matcher.match(command):
                yield Hit(
                    match,
                    matcher.highlight(command),
                    partial(self.screen._post_message, message),
                    help=description,
                )


### tags.py ends here
