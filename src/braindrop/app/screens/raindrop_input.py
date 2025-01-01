"""Provides the dialog for editing Raindrop details."""

##############################################################################
# Python imports.
from urllib.parse import urlparse

##############################################################################
# Pyperclip imports.
from pyperclip import PyperclipException
from pyperclip import paste as from_clipboard

##############################################################################
# Textual imports.
from textual import on, work
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.validation import Length, ValidationResult
from textual.widgets import Button, Input, Label, TextArea

##############################################################################
# Local imports.
from ...raindrop import API, Raindrop, Tag
from ..data import LocalData


##############################################################################
class RaindropInput(ModalScreen[Raindrop | None]):
    """The raindrop editing dialog."""

    CSS = """
    RaindropInput {
        align: center middle;

        Vertical {
            width: 60%;
            height: auto;
            background: $panel;
            border: panel $border;
        }

        TextArea {
            height: 10;
        }

        #buttons {
            height: auto;
            margin-top: 1;
            align-horizontal: right;
        }

        Button {
            margin-right: 1;
        }

        Label {
            margin: 1 0 0 1;
        }
    }
    """

    BINDINGS = [("escape", "cancel"), ("f2", "save")]

    def __init__(self, api: API, data: LocalData, raindrop: Raindrop | None = None):
        """Initialise the dialog.

        Args:
            api: The Raindrop API object.
            data: A reference to the local data.
            raindrop: The optional raindrop to edit.
        """
        super().__init__()
        self._api = api
        """The Raindrop API."""
        self._data = data
        """The local raindrop data."""
        self._raindrop = raindrop or Raindrop()
        """The raindrop to edit, or `None` if this is a new raindrop."""

    def compose(self) -> ComposeResult:
        """Compose the dialog.

        Returns:
            The content for the dialog.
        """
        with Vertical() as dialog:
            dialog.border_title = (
                f"{'New' if self._raindrop.is_brand_new else 'Edit'} Raindrop"
            )
            yield Label("Title:")
            yield Input(
                placeholder="Raindrop title",
                id="title",
                validators=[Length(1, failure_description="A title is required")],
            )
            yield Label("Excerpt:")
            yield TextArea(id="excerpt")
            yield Label("Note:")
            yield TextArea(id="note")
            yield Label("URL:")
            yield Input(
                placeholder="The URL of the link for the Raindrop",
                id="url",
                validators=[Length(1, failure_description="A link is required")],
            )
            # TODO Collection
            yield Label("Tags:")
            yield Input(placeholder="Raindrop tags (space separated)", id="tags")
            # TODO: Tag suggestions
            with Horizontal(id="buttons"):
                yield Button("Save [dim]\\[F2][/]", id="save", variant="success")
                yield Button("Cancel [dim]\\[Esc][/]", id="cancel", variant="error")

    def _paste(self, url: str) -> None:
        """Paste the given URL into the link field.

        Args:
            url: The URL to paste.

        Notes:
            The given URL will only be pasted into the link input field if
            that field is empty.
        """
        if not (link := self.query_one("#url", Input)).value:
            link.value = url

    @work(thread=True)
    def _suggest_link(self) -> None:
        """Get a link suggestion by peeking in the user's clipboard."""
        try:
            external = from_clipboard()
        except PyperclipException:
            external = ""
        for candidate in (self.app.clipboard, external):
            if urlparse(candidate).scheme in (  # pylint:disable=no-member
                "http",
                "https",
            ):
                self.app.call_from_thread(self._paste, candidate)
                break

    def on_mount(self) -> None:
        """Configure the dialog once it's in the DOM."""
        if self._raindrop:
            self.query_one("#title", Input).value = self._raindrop.title
            self.query_one("#excerpt", TextArea).text = self._raindrop.excerpt
            self.query_one("#note", TextArea).text = self._raindrop.note
            self.query_one("#url", Input).value = self._raindrop.link
            self.query_one("#tags", Input).value = " ".join(
                str(tag) for tag in self._raindrop.tags
            )
        if not self._raindrop.link:
            self._suggest_link()

    def _all_looks_good(self) -> bool:
        """Does everything on the dialog look okay?

        Returns:
            `True` if it does, `False` if it doesn't.

        Notes:
            As a side effect `Input` validation is run and notifications
            will be shown for problems.
        """
        bad_results: list[ValidationResult] = []
        for check in self.query(Input):
            result = check.validate(check.value)
            if result is not None and not result.is_valid:
                bad_results.append(result)
        if bad_results:
            self.app.bell()
            self.notify(
                "\n- "
                + (
                    "\n- ".join(
                        failure.description or f"{failure.value!r} is not valid"
                        for result in bad_results
                        for failure in result.failures
                    )
                ),
                severity="error",
                title="Missing or incorrect Raindrop data",
            )
        return not bad_results

    @on(Button.Pressed, "#save")
    def action_save(self) -> None:
        """Save the raindrop data."""
        if self._all_looks_good():
            self.dismiss(
                self._raindrop.clone(
                    title=self.query_one("#title", Input).value,
                    excerpt=self.query_one("#excerpt", TextArea).text,
                    note=self.query_one("#note", TextArea).text,
                    link=self.query_one("#url", Input).value,
                    tags=[
                        Tag(tag) for tag in self.query_one("#tags", Input).value.split()
                    ],
                    # TODO: More
                )
            )

    @on(Button.Pressed, "#cancel")
    def action_cancel(self) -> None:
        """Cancel the edit of the raindrop data."""
        self.dismiss(None)


### raindrop_input.py ends here