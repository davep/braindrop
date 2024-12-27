"""Provides a confirmation dialog."""

##############################################################################
# Textual imports.
from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Label


##############################################################################
class Confirm(ModalScreen[bool]):
    """A modal dialog for confirming things."""

    CSS = """
    Confirm {
        align: center middle;

        &> Vertical {
            padding: 1 2;
            height: auto;
            width: auto;
            max-width: 80vw;
            background: $surface;
            border: panel $error;
            border-title-color: $text;

            &> Horizontal {
                height: auto;
                width: 100%;
                align-horizontal: center;
            }
        }

        Label {
            width: auto;
            max-width: 70vw;
            padding-left: 1;
            padding-right: 1;
            margin-bottom: 1;
        }

        Button {
            margin-right: 1;
        }
    }
    """

    BINDINGS = [
        ("escape", "no"),
        ("f2", "yes"),
        ("left", "focus_previous"),
        ("right", "focus_next"),
    ]

    def __init__(
        self, title: str, question: str, yes_text: str = "Yes", no_text: str = "No"
    ) -> None:
        """Initialise the dialog.

        Args:
            title: The title for the dialog.
            question: The question to ask the user.
            yes_text: The text for the yes button.
            no_text: The text for the no button.
        """
        super().__init__()
        self._title = title
        """The title for the dialog."""
        self._question = question
        """The question to ask the user."""
        self._yes = yes_text
        """The text of the yes button."""
        self._no = no_text
        """The text of the no button."""

    def compose(self) -> ComposeResult:
        """Compose the layout of the dialog."""
        with Vertical() as dialog:
            dialog.border_title = self._title
            yield Label(self._question)
            with Horizontal():
                yield Button(f"{self._no} [dim]\\[Esc][/]", id="no")
                yield Button(f"{self._yes} [dim]\\[F2][/]", id="yes")

    @on(Button.Pressed, "#yes")
    def action_yes(self) -> None:
        """Send back the positive response."""
        self.dismiss(True)

    @on(Button.Pressed, "#no")
    def action_no(self) -> None:
        """Send back the negative response."""
        self.dismiss(False)


### confirm.py ends here
