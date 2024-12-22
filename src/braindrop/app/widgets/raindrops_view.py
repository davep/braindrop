"""Provides a widget for viewing a collection of Raindrops."""

##############################################################################
# Python imports.
from typing import Final, cast
from webbrowser import open as open_url

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
from textual.binding import Binding
from textual.reactive import var
from textual.widgets import OptionList
from textual.widgets.option_list import Option

##############################################################################
# Local imports.
from ...raindrop import Raindrop
from ..data import Raindrops
from .preserved_highlight import PreservedHighlight


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
        super().__init__(self.prompt, id=f"raindrop-{raindrop.identity}")

    @property
    def raindrop(self) -> Raindrop:
        """The Raindrop being displayed."""
        return self._raindrop

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

    BINDINGS = [
        Binding(
            "enter",
            "visit",
            description="Visit",
            tooltip="Visit the currently-highlighted bookmark",
        )
    ]

    raindrops: var[Raindrops] = var(Raindrops)
    """The list of raindrops being shown."""

    def watch_raindrops(self) -> None:
        """React to the raindrops being changed."""
        with PreservedHighlight(self):
            self.clear_options().add_options(
                [RaindropView(raindrop) for raindrop in self.raindrops]
            )

    @property
    def highlighted_raindrop(self) -> Raindrop | None:
        """The currently-highlighted Raindrop, if there is one, or `None`."""
        if self.highlighted is not None:
            return cast(
                RaindropView, self.get_option_at_index(self.highlighted)
            ).raindrop
        return None

    def action_visit(self) -> None:
        """Action that visits the currently-selected raindrop link, if there is one."""
        if (raindrop := self.highlighted_raindrop) is not None:
            if raindrop.link:
                open_url(raindrop.link)
            else:
                self.notify(
                    "There is no link associated with that Raindrop",
                    title="No link",
                    severity="error",
                )


### raindrops_view.py ends here
