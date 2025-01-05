"""Provides a widget that shows the detail of a raindrop."""

##############################################################################
# Python imports.
from datetime import datetime
from typing import Any, Callable, Final
from webbrowser import open as open_url

##############################################################################
# Humanize imports.
from humanize import naturaltime

##############################################################################
# Rich imports.
from rich.emoji import Emoji

##############################################################################
# Textual imports.
from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.message import Message
from textual.reactive import var
from textual.widgets import Label
from textual.widgets.option_list import Option

##############################################################################
# Local imports.
from ...raindrop import Raindrop, Tag
from ..messages import ShowTagged
from .extended_option_list import OptionListEx

##############################################################################
HELP = """
## The highlighted Raindrop's details.

This panel contains the details of the currently-highlighted Raindrop.
"""
"""The help to use in the widgets."""


##############################################################################
class Tags(OptionListEx):
    """Show the tags for a Raindrop."""

    HELP = HELP

    _ICON: Final[str] = Emoji.replace(":bookmark: ")
    """The icon to show before tags."""

    raindrop: var[Raindrop | None] = var(None)
    """The raindrop to show the tags for."""

    def watch_raindrop(self) -> None:
        """Show the tags for the given raindrop.

        Args:
            raindrop: The raindrop to show the tags for.
        """
        self.clear_options().add_options(
            []
            if self.raindrop is None
            else (
                Option(f"{self._ICON} {tag}", id=str(tag))
                for tag in sorted(self.raindrop.tags)
            )
        )
        self.set_class(not bool(self.option_count), "empty")

    @on(OptionListEx.OptionSelected)
    def show_tag(self, message: OptionListEx.OptionSelected) -> None:
        """Filter on a given tag when one is selected."""
        if message.option_id is not None:
            self.post_message(ShowTagged(Tag(message.option_id)))

    def on_focus(self) -> None:
        """Ensure the highlight appears when we get focus."""
        if self.highlighted is None and self.option_count:
            self.highlighted = 0

    def on_blur(self) -> None:
        """Remove the highlight when we no longer have focus."""
        self.highlighted = None


##############################################################################
class Link(Label):
    """Widget for showing the link.

    This is here mostly to work around the fact that a click action doesn't
    propagate in the way you'd expect.

    https://github.com/Textualize/textual/issues/3690
    """

    class Visit(Message):
        """Message to indicate that the link should be visited."""

    def action_visit(self) -> None:
        """Handle a UI request to visit the link."""
        self.post_message(self.Visit())


##############################################################################
class RaindropDetails(VerticalScroll):
    """A widget for viewing the details of a raindrop."""

    DEFAULT_CSS = """
    RaindropDetails {
        background: $surface;

        &:focus, &:focus-within {
            .detail, Tags, Tags:focus{
                background: $boost 200%;
            }
        }

        .hidden {
            visibility: hidden;
        }

        .empty {
            display: none;
        }

        Label {
            margin: 0 2 1 2;
            padding: 1 2 1 2;
            width: 1fr;
            color: $text;
        }

        .detail {
            color: $foreground;
            background: $boost 150%;
        }

        #title {
            background: $primary;
            text-align: center;
        }

        #excerpt {
            background: $primary;
            color: $text-muted;
        }

        #borked {
            background: $error;
            text-align: center;
        }

        .ish {
            margin: 0 2 0 2;
            padding: 1 2 0 2;
        }

        .exact {
            padding: 0 2 1 2;
            text-align: right;
            color: $text-muted;
            text-style: italic;
        }

        Tags, Tags:focus {
            & > .option-list--option {
                color: $foreground;
            }
            border: none;
            background: $boost 150%;
            margin: 1 2 1 2;
            padding: 1 2 1 2;
            height: auto;
            /* Stop a flash of unnecessary scrollbar. */
            scrollbar-size-vertical: 0;
        }
    }
    """

    HELP = HELP

    BINDINGS = [
        Binding(
            "enter",
            "visit_link",
            description="Visit",
            tooltip="Visit the current Raindrop's link",
        )
    ]

    raindrop: var[Raindrop | None] = var(None)
    """The raindrop to view the details of."""

    def compose(self) -> ComposeResult:
        """Compose the content of the widget.

        Returns:
            The content of the widget.
        """
        yield Label(id="title")
        yield Label(id="borked")
        yield Label(id="excerpt")
        yield Label(id="note", classes="detail")
        yield Label(id="created-ish", classes="detail ish")
        yield Label(id="created", classes="detail exact")
        yield Label(id="updated-ish", classes="detail ish")
        yield Label(id="updated", classes="detail exact")
        yield Link(id="link", classes="detail")
        yield Tags().data_bind(RaindropDetails.raindrop)

    def _set(self, widget: str, value: str) -> None:
        """Set the value of a detail widget.

        Args:
            widget: The ID of the widget to set.
            value: The value to set.
        """
        self.query_one(f"#{widget}", Label).update(value)
        self.query_one(f"#{widget}").set_class(not bool(value), "empty")

    @staticmethod
    def _time(
        time: datetime | None,
        prefix: str = "",
        strify: Callable[[Any], str] = str,
        if_different_to: datetime | None = None,
    ) -> str:
        """Format a time.

        Args:
            time: The time to format.
            prefix: The prefix to give the time.
            strify: The function to use to `str` the `time`.
            if_different_to: Only return the time if it's different to this.

        Returns:
            The formatted time.
        """
        if time is not None:
            time = time.replace(microsecond=0)
        if if_different_to is not None:
            if_different_to = if_different_to.replace(microsecond=0)
        return (
            "" if time == if_different_to else f"{prefix} {strify(time or 'Unknown')}"
        )

    def _watch_raindrop(self) -> None:
        """React to the raindrop being changed."""
        try:
            if self.raindrop is None:
                return
            self._set("title", self.raindrop.title)
            self._set("borked", "Broken link!" if self.raindrop.broken else "")
            self._set("excerpt", self.raindrop.excerpt)
            self._set("note", self.raindrop.note)
            self._set(
                "created-ish", self._time(self.raindrop.created, "Created", naturaltime)
            )
            self._set("created", self._time(self.raindrop.created))
            self._set(
                "updated-ish",
                self._time(
                    self.raindrop.last_update,
                    "Updated",
                    naturaltime,
                    self.raindrop.created,
                ),
            )
            self._set(
                "updated",
                self._time(
                    self.raindrop.last_update,
                    if_different_to=self.raindrop.created,
                ),
            )
            self._set(
                "link",
                f"[@click=visit]{self.raindrop.link}[/]" if self.raindrop.link else "",
            )
        finally:
            self.query("*").set_class(not bool(self.raindrop), "hidden")

    @on(Link.Visit)
    def action_visit_link(self) -> None:
        """Visit a link associated with the raindrop."""
        if self.raindrop is not None and self.raindrop.link:
            open_url(self.raindrop.link)


### raindrop_details.py ends here
