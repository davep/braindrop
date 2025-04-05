"""Provides a widget for viewing a collection of Raindrops."""

##############################################################################
# Python imports.
from dataclasses import dataclass
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
from textual import on
from textual.binding import Binding
from textual.message import Message
from textual.reactive import var
from textual.widgets.option_list import Option

##############################################################################
# Textual enhanced imports.
from textual_enhanced.widgets import EnhancedOptionList

##############################################################################
# Local imports.
from ...raindrop import Raindrop
from ..commands import VisitLink
from ..data import LocalData, Raindrops
from .icons import BROKEN_ICON, PRIVATE_ICON, PUBLIC_ICON, UNSORTED_ICON


##############################################################################
class RaindropView(Option):
    """An individual raindrop."""

    RULE: Final[Rule] = Rule(style="dim")
    """The rule to place at the end of each view."""

    def __init__(
        self, raindrop: Raindrop, data: LocalData | None, compact: bool = False
    ) -> None:
        """Initialise the object.

        Args:
            raindrop: The raindrop to view.
        """
        self._raindrop = raindrop
        """The raindrop to view."""
        self._public = (
            False if data is None else data.collection(raindrop.collection).public
        )
        """Is this raindrop visible to the public?"""
        self._compact = compact
        """Use a compact view?"""
        super().__init__(self.prompt, id=self.id_of(raindrop))

    @staticmethod
    def id_of(raindrop: Raindrop) -> str:
        """Create an option ID for the given Raindrop.

        Args:
            raindrop: The raindrop to create the ID for.

        Returns:
            The ID of the raindrop.
        """
        return f"raindrop-{raindrop.identity}"

    @property
    def raindrop(self) -> Raindrop:
        """The Raindrop being displayed."""
        return self._raindrop

    @property
    def prompt(self) -> Group:
        """The prompt for the Raindrop."""

        title = Table.grid(expand=True)
        title.add_column(ratio=1, no_wrap=self._compact)
        title.add_column(justify="right")
        title.add_row(
            escape(self._raindrop.title),
            f"{BROKEN_ICON if self._raindrop.broken else ''}"
            f"{UNSORTED_ICON if self._raindrop.is_unsorted else ''}"
            f"{PUBLIC_ICON if self._public else PRIVATE_ICON}",
        )

        body: list[Table] = []
        if self._raindrop.excerpt:
            excerpt = Table.grid()
            excerpt.add_column(ratio=1, no_wrap=self._compact)
            excerpt.add_row(f"[dim]{escape(self._raindrop.excerpt)}[/dim]")
            body.append(excerpt)

        details = Table.grid(expand=True)
        details.add_column()
        details.add_column(justify="right")
        details.add_row(
            f"[dim][italic]{naturaltime(self._raindrop.created) if self._raindrop.created else 'Unknown'}[/][/] ",
            f"[dim bold italic]{', '.join(str(tag) for tag in sorted(self._raindrop.tags))}[/]",
        )

        return Group(title, *body, details, self.RULE)


##############################################################################
class RaindropsView(EnhancedOptionList):
    """A widget for viewing a collection of Raindrops."""

    BINDINGS = [
        Binding(
            "enter",
            "visit",
            show=False,
        ),
    ]

    HELP = f"""
    ## The Raindrop collection view

    This panel shows the currently-selected collection of Raindrops,
    filtered by any tag and search text you may have applied.

    Each Raindrop may have one or more icons showing to the right, these
    include:

    - {BROKEN_ICON} - The Raindrop has a broken link (*Raindrop Pro only*)
    - {UNSORTED_ICON} - The Raindrop hasn't been sorted into a collection yet
    - {PUBLIC_ICON} - The Raindrop is in a collection that is visible to the public
    - {PRIVATE_ICON} - The Raindrop is in a collection that is private
    """

    data: var[LocalData | None] = var(None, always_update=True)
    """The local data."""

    raindrops: var[Raindrops] = var(Raindrops)
    """The list of raindrops being shown."""

    compact: var[bool] = var(False)
    """Toggle to say if we should use a compact view or not."""

    class Empty(Message):
        """A message sent if the view becomes empty."""

    def _add_raindrops(self) -> None:
        """Add the current raindrops to the display."""
        with self.preserved_highlight:
            self.clear_options().add_options(
                [
                    RaindropView(raindrop, self.data, self.compact)
                    for raindrop in self.raindrops
                ]
            )
        if not self.option_count:
            self.post_message(self.Empty())

    def watch_data(self) -> None:
        """React to the data being changed."""
        self._add_raindrops()

    def watch_raindrops(self) -> None:
        """React to the raindrops being changed."""
        self._add_raindrops()

    def watch_compact(self) -> None:
        """React to the compact setting being toggled."""
        self._add_raindrops()

    @dataclass
    class Highlighted(Message):
        """Message sent when a new Raindrop is highlighted."""

        raindrop: Raindrop
        """The raindrop that was highlighted."""

    @on(EnhancedOptionList.OptionHighlighted)
    def raindrop_highlighted(
        self, message: EnhancedOptionList.OptionHighlighted
    ) -> None:
        """Handle a raindrop being highlighted.

        Args:
            message: The message to handle.
        """
        message.stop()
        assert isinstance(message.option, RaindropView)
        self.post_message(self.Highlighted(message.option.raindrop))

    def action_visit(self) -> None:
        """Action that visits the currently-selected raindrop link, if there is one."""
        self.post_message(VisitLink())


### raindrops_view.py ends here
