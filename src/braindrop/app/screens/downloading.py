"""Screen shown when downloading data from the server."""

##############################################################################
# Textual imports.
from textual import work
from textual.app import ComposeResult
from textual.containers import Center, Vertical
from textual.screen import ModalScreen
from textual.widgets import Label

##############################################################################
# Local imports.
from ...raindrop import API, User
from ..data import LocalData


##############################################################################
class Downloading(ModalScreen[None]):
    """Modal screen that shows we're downloading data."""

    CSS = """
    Downloading {
        align: center middle;

        &> Center {
            padding: 1 2;
            border: round $border;
            width: auto;
            height: auto;
            background: $panel;
            Vertical {
                margin-top: 1;
                margin-bottom: 1;
                height: 1;
                width: 100%;
            }
            #status {
                width: 100%;
                text-align: center;
                color: $text-success;
            }
        }
    }
    """

    def __init__(self, user: User | None, data: LocalData) -> None:
        """Initialise the downloading screen.

        Args:
            user: The user to get the data for.
            data: The local data object that will be doing the loading.
        """
        super().__init__()
        self._user = user
        """The user to download the data for."""
        self._data = data
        """The local data object that will do the downloading."""

    def compose(self) -> ComposeResult:
        """Compose the loading screen."""
        with Center():
            yield Label("Downloading all your Raindrop data from raindrop.io")
            yield Vertical()
            yield Label(id="status")

    def on_mount(self) -> None:
        """Configure the screen when the DOM is mounted."""
        self.query_one("Vertical").loading = True
        self.download_data()

    @work
    async def download_data(self) -> None:
        """Download the data from the serer.

        Note:
            As a side-effect the data is saved locally.
        """
        try:
            if self._user is None:
                self.app.bell()
                self.notify(
                    "Request made to download Raindrop data when the user is unknown.",
                    title="Application Error",
                    severity="error",
                    timeout=8,
                )
                return

            try:
                await self._data.download(
                    self._user, self.query_one("#status", Label).update
                )
            except API.Error as error:
                self.app.bell()
                self.notify(
                    str(error),
                    title="Error downloading data from the server.",
                    severity="error",
                    timeout=80,
                )
                return

            try:
                self._data.save()
            except OSError as error:
                self.app.bell()
                self.notify(
                    f"Error saving the data.\n\n{error}",
                    title="Save Error",
                    severity="error",
                    timeout=8,
                )
                return

        finally:
            self.dismiss()


### downloading.py ends here
