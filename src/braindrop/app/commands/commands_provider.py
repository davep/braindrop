"""Provides a base command-oriented command palette provider class."""

##############################################################################
# Python imports.
from abc import abstractmethod
from functools import partial
from typing import Iterator, NamedTuple, TypeAlias

##############################################################################
# Textual imports.
from textual.command import DiscoveryHit, Hit, Hits, Provider

##############################################################################
# Local imports.
from ..messages import Command


##############################################################################
class CommandHit(NamedTuple):
    """A command hit for use in building a command palette hit."""

    command: str
    """The command."""
    description: str
    """The description of the command."""
    message: Command
    """The message to emit when the command is chosen."""


##############################################################################
CommandHits: TypeAlias = Iterator[CommandHit | Command]
"""The result of looking for commands to make into hits."""


##############################################################################
class CommandsProvider(Provider):
    """A base class for command-message-oriented command palette commands."""

    @classmethod
    def prompt(cls) -> str:
        """The prompt for the command provider."""
        return ""

    @abstractmethod
    def commands(self) -> CommandHits:
        """Provide the command data for the command palette.

        Yields:
            A tuple of the command, the command description and a command message.
        """
        raise NotImplemented

    @property
    def _commands(self) -> Iterator[CommandHit]:
        """The commands available for the palette."""
        return (
            CommandHit(command.command(), command.tooltip(), command)
            if isinstance(command, Command)
            else command
            for command in self.commands()
        )

    async def discover(self) -> Hits:
        """Handle a request to discover commands.

        Yields:
            Command discovery hits for the command palette.
        """
        for command, description, message in self._commands:
            yield DiscoveryHit(
                message.maybe_add_binding(command),
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
        for command, description, message in self._commands:
            if match := matcher.match(command):
                yield Hit(
                    match,
                    message.maybe_add_binding(matcher.highlight(command)),
                    partial(self.screen._post_message, message),
                    help=description,
                )


### commands_provider.py ends here
