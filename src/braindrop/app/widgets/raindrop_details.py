"""Provides a widget that shows the detail of a raindrop."""

##############################################################################
# Python imports.
from webbrowser import open as open_url

##############################################################################
# Humanize imports.
from humanize import naturaltime

##############################################################################
# Textual imports.
from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.message import Message
from textual.reactive import var
from textual.widgets import Label

##############################################################################
# Local imports.
from ...raindrop import Raindrop


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
        scrollbar-gutter: stable;

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
            background: $panel;
        }

        #title {
            background: $primary;
            text-align: center;
        }

        #excerpt {
            background: $primary;
            color: $text-muted;
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

    }
    """

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
        yield Label(id="excerpt")
        yield Label(id="note", classes="detail")
        yield Label(id="created-ish", classes="detail ish")
        yield Label(id="created", classes="detail exact")
        yield Label(id="updated-ish", classes="detail ish")
        yield Label(id="updated", classes="detail exact")
        yield Link(id="link", classes="detail")

    def _set(self, widget: str, value: str) -> None:
        """Set the value of a detail widget.

        Args:
            widget: The ID of the widget to set.
            value: The value to set.
        """
        self.query_one(f"#{widget}", Label).update(value)
        self.query_one(f"#{widget}").set_class(not bool(value), "empty")

    def _watch_raindrop(self) -> None:
        """React to the raindrop being changed."""
        try:
            if self.raindrop is None:
                return
            self._set("title", self.raindrop.title)
            self._set("excerpt", self.raindrop.excerpt)
            self._set("note", self.raindrop.note)
            self._set(
                "created-ish", f"Created {naturaltime(self.raindrop.created or 0)}"
            )
            self._set("created", str(self.raindrop.created or "Unknown"))
            self._set(
                "updated-ish", f"Updated {naturaltime(self.raindrop.last_update or 0)}"
            )
            self._set("updated", str(self.raindrop.last_update or "Unknown"))
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