"""A dialog for getting text to search for."""

##############################################################################
# Textual imports.
from textual import on
from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Input


##############################################################################
class SearchInput(ModalScreen[str]):
    """A modal screen to get search text from the user."""

    CSS = """
    SearchInput {
        align: center middle;

        Input, Input:focus {
            border: round $border;
            width: 60%;
            padding: 1;
            height: auto;
        }
    }
    """

    BINDINGS = [("escape", "escape")]

    def compose(self) -> ComposeResult:
        """Compose the input dialog."""
        yield Input(placeholder="Case-insensitive text to look for in the Raindrops")

    @on(Input.Submitted)
    def search(self) -> None:
        """Perform the search."""
        self.dismiss(self.query_one(Input).value.strip())

    def action_escape(self) -> None:
        """Escape out without searching."""
        self.app.pop_screen()


### search_input.py ends here
