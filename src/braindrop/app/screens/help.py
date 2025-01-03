"""The help screen for the application."""

##############################################################################
# Python imports.
from inspect import cleandoc
from typing import Any
from webbrowser import open as open_url

##############################################################################
# Textual imports.
from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Center, Vertical, VerticalScroll
from textual.dom import DOMNode
from textual.screen import ModalScreen, Screen
from textual.widgets import Button, Markdown

##############################################################################
# Local imports.
from ... import __version__
from ..messages import Command

##############################################################################
# The help text.
HELP = f"""\
# Braindrop v{__version__}

{{context_help}}

## About

`Braindrop` is a terminal-based client for
[raindrop.io](https://raindrop.io/); it was created by and is maintained by
[Dave Pearson](https://www.davep.org/); it is Free Software and can be
[found on GitHub](https://github.com/davep/braindrop).


## Licence

Braindrop - A client for the Raindrop bookmarking service.[EOL]
Copyright (C) 2024-2025 Dave Pearson

This program is free software: you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the Free
Software Foundation, either version 3 of the License, or (at your option)
any later version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
more details.

You should have received a copy of the GNU General Public License along with
this program. If not, see <https://www.gnu.org/licenses/>.
"""


##############################################################################
class HelpScreen(ModalScreen[None]):
    """The help screen."""

    CSS = """
    HelpScreen {
        align: center middle;

        Vertical {
            width: 75%;
            height: 90%;
            background: $panel;
            border: solid $border;
        }

        Markdown {
            background: $panel;
        }

        VerticalScroll {
            scrollbar-gutter: stable;
        }

        Center {
            height: auto;
            width: 100%;
            border-top: solid $border;
        }
    }
    """

    BINDINGS = [("escape", "close")]

    def __init__(self, help_for: Screen[Any]) -> None:
        """Initialise the help screen.

        Args:
            help_for: The screen to show the help for.
        """
        super().__init__()
        self._context_help = ""
        for node in (
            help_for.focused if help_for.focused is not None else help_for
        ).ancestors_with_self:
            if node.HELP is not None:
                self._context_help += f"\n\n{cleandoc(node.HELP)}"
            self._context_help += self.command_help(node)

    def _all_keys(self, command: Command) -> str:
        """Render all the keys for the given command.

        Args:
            command: The command to get all the keys for.

        Returns:
            A string listing all the keys for the command.
        """
        return ", ".join(
            self.app.get_key_display(Binding(key.strip(), ""))
            for key in command.binding().key.split(",")
        )

    def command_help(self, node: DOMNode) -> str:
        """Build help from the commands provided by a DOM node.

        Args:
            node: The node that might provide commands

        Returns:
            The help text.
        """
        if (commands := getattr(node, "COMMAND_MESSAGES", None)) is None:
            return ""
        keys = "| Key | Command | Description |\n| - | - | - |\n"
        for command in commands:
            keys += f"| {self._all_keys(command)} | {command.command()} | {command.tooltip()} |\n"
        return f"\n\n{keys}"

    def compose(self) -> ComposeResult:
        """Compose the layout of the help screen."""
        with Vertical() as help_screen:
            help_screen.border_title = "Help"
            with VerticalScroll():
                yield Markdown(
                    HELP.replace("[EOL]", "  ").format(context_help=self._context_help)
                )
            with Center():
                yield Button("Okay [dim]\\[Esc]")

    @on(Button.Pressed)
    def action_close(self) -> None:
        """Close the help screen."""
        self.dismiss(None)

    @on(Markdown.LinkClicked)
    def visit(self, event: Markdown.LinkClicked) -> None:
        """Visit any link clicked in the help."""
        open_url(event.href)


### help.py ends here
