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
from rich.emoji import Emoji
from rich.markup import escape
from rich.rule import Rule
from rich.table import Table

##############################################################################
# Textual imports.
from textual.binding import Binding
from textual.reactive import var
from textual.widgets.option_list import Option, OptionDoesNotExist

##############################################################################
# Local imports.
from ...raindrop import Raindrop
from ..data import Raindrops
from .extended_option_list import OptionListEx


##############################################################################
class RaindropView(Option):
    """An individual raindrop."""

    BROKEN_ICON: Final[str] = Emoji.replace(":skull:")
    """The icon for broken links."""

    UNSORTED_ICON: Final[str] = Emoji.replace(":thinking_face:")
    """The icon for unsorted raindrops."""

    RULE: Final[Rule] = Rule(style="dim")
    """The rule to place at the end of each view."""

    def __init__(self, raindrop: Raindrop, compact: bool = False) -> None:
        """Initialise the object.

        Args:
            raindrop: The raindrop to view.
        """
        self._raindrop = raindrop
        """The raindrop to view."""
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
            f"{self.BROKEN_ICON if self._raindrop.broken else ''}"
            f"{self.UNSORTED_ICON if self._raindrop.is_unsorted else ''}",
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
class RaindropsView(OptionListEx):
    """A widget for viewing a collection of Raindrops."""

    BINDINGS = [
        Binding(
            "enter",
            "visit",
            description="Visit",
            tooltip="Visit the currently-highlighted Raindrop",
        ),
    ]

    HELP = f"""
    ## The Raindrop collection view

    This panel shows the currently-selected collection of Raindrops,
    filtered by any tag ans search text you may have applied.

    Each Raindrop may have one or more icons showing to the right, these
    include:

    ## {RaindropView.BROKEN_ICON}
    The Raindrop has a broken link (*Raindrop Pro only*)
    ## {RaindropView.UNSORTED_ICON}
    The Raindrop hasn't been sorted into a collection yet
    """

    raindrops: var[Raindrops] = var(Raindrops)
    """The list of raindrops being shown."""

    compact: var[bool] = var(False)
    """Toggle to say if we should use a compact view or not."""

    def _add_raindrops(self) -> None:
        """Add the current raindrops to the display."""
        with self.preserved_highlight:
            self.clear_options().add_options(
                [RaindropView(raindrop, self.compact) for raindrop in self.raindrops]
            )

    def watch_raindrops(self) -> None:
        """React to the raindrops being changed."""
        self._add_raindrops()

    def watch_compact(self) -> None:
        """React to the compact setting being toggled."""
        self._add_raindrops()

    @property
    def highlighted_raindrop(self) -> Raindrop | None:
        """The currently-highlighted Raindrop, if there is one, or `None`."""
        if self.highlighted is not None:
            return cast(
                RaindropView, self.get_option_at_index(self.highlighted)
            ).raindrop
        return None

    @highlighted_raindrop.setter
    def highlighted_raindrop(self, raindrop: Raindrop | None) -> None:
        if raindrop is None:
            self.highlighted = None
        else:
            try:
                self.highlighted = self.get_option_index(RaindropView.id_of(raindrop))
            except OptionDoesNotExist:
                pass

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
