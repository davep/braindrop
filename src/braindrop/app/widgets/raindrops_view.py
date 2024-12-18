"""Provides a widget for viewing a collection of Raindrops."""

##############################################################################
# Python imports.
from typing import Final

##############################################################################
# Humanize imports.
from humanize import naturaltime

##############################################################################
# Rich imports.
from rich.console import Group
from rich.markup import escape
from rich.rule import Rule
from rich.table import Table

##############################################################################
# Textual imports.
from textual.widgets import OptionList
from textual.widgets.option_list import Option

##############################################################################
# Local imports.
from ...raindrop import Raindrop


##############################################################################
class RaindropView(Option):
    """An individual raindrop."""

    RULE: Final[Rule] = Rule(style="dim")
    """The rule to place at the end of each view."""

    def __init__(self, raindrop: Raindrop) -> None:
        """Initialise the object.

        Args:
            raindrop: The raindrop to view.
        """
        self._raindrop = raindrop
        """The raindrop to view."""
        super().__init__(self.prompt, id=str(raindrop.identity))

    @property
    def prompt(self) -> Group:
        """The prompt for the Raindrop."""

        title = Table.grid(expand=True)
        title.add_column(ratio=1)
        title.add_row(escape(self._raindrop.title))

        body: list[str] = []
        if self._raindrop.excerpt:
            body.append(f"[dim]{escape(self._raindrop.excerpt)}[/dim]")

        details = Table.grid(expand=True)
        details.add_column(ratio=1)
        details.add_column()
        details.add_row(
            f"[dim][i]{naturaltime(self._raindrop.created) if self._raindrop.created else 'Unknown'}[/][/]",
            f"[dim]{', '.join(str(tag) for tag in sorted(self._raindrop.tags))}[/]",
        )

        return Group(title, *body, details, self.RULE)


##############################################################################
class RaindropsView(OptionList):
    """A widget for viewing a collection of Raindrops."""

    def show(self, raindrops: list[Raindrop]) -> None:
        """Show the given raindrops.

        Args:
            raindrops: The raindrops to show.
        """
        self.clear_options().add_options(
            [RaindropView(raindrop) for raindrop in raindrops]
        )


### raindrops_view.py ends here
