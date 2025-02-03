"""Dialog for checking if a bookmark is in the Wayback Machine."""

##############################################################################
# Python imports.
from datetime import datetime
from webbrowser import open as view_url

##############################################################################
# Humanize imports.
from humanize import naturaltime

##############################################################################
# Textual imports.
from textual import on, work
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.reactive import var
from textual.screen import ModalScreen
from textual.widgets import Button, Label

##############################################################################
# Local imports.
from ...wayback import Availability, WaybackError, availability


##############################################################################
class WaybackChecker(ModalScreen[None]):
    """Dialog for checking if a URL is in the Wayback Machine."""

    CSS = """
    WaybackChecker {
        align: center middle;

        &> Vertical {
            height: auto;
            width: auto;
            background: $panel;
            border: hkey $border;

            Label {
                height: auto;
                padding: 1 1 0 1;
                margin-bottom: 1;
            }

            Horizontal {
                width: 100%;
                height: auto;
                align: center middle;
                #view {
                    margin-right: 1;
                }
            }

        }

        #view {
            display: none;
        }

        &.available {
            &> Vertical {
                border: hkey $success;
                background: $success-darken-2;
                border-title-color: $text;
            }
            #view {
                display: block;
            }
        }

        &.not-available > Vertical {
            border: hkey $warning;
            background: $warning-darken-2;
            border-title-color: $text;
        }

        &.error > Vertical {
            border: hkey $error;
            background: $error-darken-2;
            border-title-color: $text;
        }

        &.loading > Vertical {
            min-width: 50vw;
            min-height: 15;
        }
    }
    """

    AUTO_FOCUS = "#close"

    BINDINGS = [("escape", "close")]

    _wayback_data: var[Availability | WaybackError | None] = var(None, init=False)
    """The wayback availability data.

    This can either be `Availability` data, a `WaybackError` if there was a
    problem, or `None`.
    """

    def __init__(self, url: str) -> None:
        """Initialise the dialog.

        Args:
            url: The URL to look up on the Wayback Machine.
        """
        super().__init__(classes="loading")
        self._url = url
        """The URL to check the Wayback Machine status for."""

    def on_mount(self) -> None:
        """Once the DOM is ready, start looking up the URL."""
        self.query_one("#dialog").loading = True
        self.check_availability()

    def compose(self) -> ComposeResult:
        with Vertical(id="dialog") as dialog:
            dialog.border_title = "Wayback Machine"
            yield Label("Loading...")
            with Horizontal():
                yield Button("View archive", id="view")
                yield Button("Close", id="close")

    @work
    async def check_availability(self) -> None:
        """Check if the given URL is available in the Wayback Machine."""
        try:
            self._wayback_data = await availability(self._url)
        except WaybackError as error:
            self._wayback_data = error
        finally:
            self.set_class(False, "loading")
            self.query_one("#dialog").loading = False

    def _watch__wayback_data(self) -> None:
        """React to the data coming back from the Wayback Machine."""
        if self._wayback_data is None:
            return
        if isinstance(self._wayback_data, WaybackError):
            self.query_one(Label).update(
                f"Error talking to the Wayback Machine.\n\n{self._wayback_data}"
            )
            self.set_class(True, "error")
            self.query_one("#dialog", Vertical).set_class(True, "error")
            self.query_one("#close", Button).variant = "error"
            return
        if self._wayback_data.available:
            archived_on = datetime.strptime(
                self._wayback_data.timestamp, "%Y%m%d%H%M%S"
            )
            self.query_one(Label).update(
                "The bookmark is available in the Wayback Machine.\n\n"
                f"It was last archived {archived_on} with status "
                f"{self._wayback_data.status}.\n\n"
                f"That was {naturaltime(archived_on)}."
            )
            self.set_class(True, "available")
            self.query_one("#view", Button).variant = "success"
            self.query_one("#close", Button).variant = "success"
        else:
            self.query_one(Label).update(
                "The bookmark is not available in the Wayback Machine."
            )
            self.query_one("#close", Button).variant = "warning"
            self.set_class(True, "not-available")

    @on(Button.Pressed, "#view")
    def view_wayback_archive(self) -> None:
        """View the archive in the Wayback Machine."""
        if (
            isinstance(self._wayback_data, Availability)
            and self._wayback_data.available
        ):
            view_url(self._wayback_data.archive_url)

    @on(Button.Pressed, "#close")
    def action_close(self) -> None:
        """Close the help screen."""
        self.dismiss(None)


### wayback_checker.py ends here
