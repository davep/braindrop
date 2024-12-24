"""Provides a widget that shows the detail of a raindrop."""

##############################################################################
# Textual imports.
from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.reactive import var
from textual.widgets import Label

##############################################################################
# Local imports.
from ...raindrop import Raindrop


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
            width: 1fr;
            color: $text;
        }

        #title {
            background: $primary;
            padding: 1 2 1 2;
            text-align: center;
            margin: 0 2 0 2;
        }

        #excerpt {
            background: $primary 50%;
            padding: 1 2 1 2;
            color: $text 50%;
        }
    }
    """

    raindrop: var[Raindrop | None] = var(None)
    """The raindrop to view the details of."""

    def compose(self) -> ComposeResult:
        """Compose the content of the widget.

        Returns:
            The content of the widget.
        """
        yield Label(id="title")
        yield Label(id="excerpt")

    def _watch_raindrop(self) -> None:
        """React to the raindrop being changed."""
        try:
            if self.raindrop is None:
                return
            self.query_one("#title", Label).update(self.raindrop.title)
            self.query_one("#excerpt", Label).update(self.raindrop.excerpt)
            self.query_one("#excerpt").set_class(
                not bool(self.raindrop.excerpt), "empty"
            )
        finally:
            self.query("*").set_class(not bool(self.raindrop), "hidden")


### raindrop_details.py ends here
