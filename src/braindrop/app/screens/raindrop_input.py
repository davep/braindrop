"""Provides the dialog for editing Raindrop details."""

##############################################################################
# Python imports.
from typing import Iterator

##############################################################################
# httpx imports.
from httpx import URL

##############################################################################
# Pyperclip imports.
from pyperclip import PyperclipException
from pyperclip import paste as from_clipboard

##############################################################################
# Textual imports.
from textual import on, work
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.events import DescendantBlur, DescendantFocus
from textual.screen import ModalScreen
from textual.validation import Length, ValidationResult
from textual.widgets import Button, Input, Label, Select, TextArea

##############################################################################
# Local imports.
from ...raindrop import API, Collection, Raindrop, SpecialCollection
from ..data import LocalData
from ..suggestions import SuggestTags


##############################################################################
def looks_urlish(possible_url: str) -> bool:
    """Test if a string looks like a web-oriented URL.

    Args:
        possible_url: The string that might be a URL.

    Returns:
        `True` if the string looks like it might be a URL, `False` if not.
    """
    return (url := URL(possible_url)).is_absolute_url and url.scheme in (
        "http",
        "https",
    )


##############################################################################
class RaindropInput(ModalScreen[Raindrop | None]):
    """The raindrop editing dialog."""

    CSS = """
    RaindropInput {
        align: center middle;

        &> Vertical {
            width: 60%;
            height: auto;
            background: $panel;
            border: panel $border;
        }

        #excerpt {
            height: 5;
        }

        #note {
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

        #tag-suggestions {
            display: none;
            width: 1fr;
            color: $text-muted;
            &.got-suggestions {
                display: block;
            }
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
        self._last_url = self._raindrop.link
        """Keeps track of the last URL entered. Used to decide when to get suggestions."""

    def _selectable_child_collections_of(
        self, parent: Collection, indent: int = 0
    ) -> Iterator[tuple[str, int]]:
        """Get child collections of the given collection for a `Select`.

        Args:
            parent: The parent collection to get the children for.
            indent: The indent level.

        Yields:
            The title of the collection and its identity.
        """
        indent += 1
        for collection in self._data.collections:
            if collection.parent == parent.identity:
                yield f"{'  ' * indent}{collection.title}", collection.identity
                yield from self._selectable_child_collections_of(collection, indent)

    @property
    def _selectable_collections(self) -> Iterator[tuple[str, int]]:
        """An iterator of options for the collections `Select` widget.

        Each item in the iteration is a collection title and its identity.
        """
        yield SpecialCollection.UNSORTED().title, SpecialCollection.UNSORTED().identity
        if self._data.user is not None:
            for group in self._data.user.groups:
                for collection_id in group.collections:
                    collection = self._data.collection(collection_id)
                    yield collection.title, collection.identity
                    yield from self._selectable_child_collections_of(collection)
        yield SpecialCollection.TRASH().title, SpecialCollection.TRASH().identity

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
            yield Label("Collection:")
            yield Select[int](
                self._selectable_collections,
                prompt="The raindrop's collection",
                allow_blank=False,
                id="collection",
            )
            yield Label("Tags:")
            yield Input(
                placeholder=f"Raindrop tags ({Raindrop.TAG_STRING_SEPARATOR_TITLE} separated)",
                suggester=SuggestTags(self._data.all.tags),
                id="tags",
            )
            yield Label(id="tag-suggestions")
            with Horizontal(id="buttons"):
                yield Button("Save [dim]\\[F2][/]", id="save", variant="success")
                yield Button("Cancel [dim]\\[Esc][/]", id="cancel", variant="error")

    @work(exclusive=True)
    async def _get_tag_suggestions(self) -> None:
        """Load up fresh tag suggestions based on the URL."""
        # Don't bother trying to get suggestions if the URL in the URL input
        # doesn't look like an URL.
        if not looks_urlish(url := self.query_one("#url", Input).value):
            return
        # Ask raindrop.io for suggestions.
        try:
            suggestions = await self._api.suggestions_for(url)
        except API.Error as error:
            self.app.bell()
            self.notify(
                str(error),
                title="Error getting suggested tags from raindrop.io",
                severity="error",
                timeout=8,
            )
            return
        # We got suggestions, so show them and set them up for
        # auto-completion too.
        self.query_one("#tag-suggestions", Label).update(
            f"[b]Suggested:[/] {Raindrop.tags_to_string(suggestions.tags)}"
            if suggestions.tags
            else ""
        )
        self.query_one("#tag-suggestions").set_class(
            bool(suggestions.tags), "got-suggestions"
        )
        self.query_one("#tags", Input).suggester = SuggestTags(
            set([*self._data.all.tags, *suggestions.tags])
        )

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
            self._get_tag_suggestions()

    @work(thread=True)
    def _suggest_link(self) -> None:
        """Get a link suggestion by peeking in the user's clipboard."""
        # Look for something in the external clipboard.
        try:
            external = from_clipboard()
        except PyperclipException:
            external = ""
        # Looking at the Textual-internal clipboard, then the external
        # clipboard...
        for candidate in (self.app.clipboard, external):
            # ...only looking at the first line of what we find...
            try:
                candidate = candidate.strip().splitlines()[0]
            except IndexError:
                candidate = ""
            # If it looks like it might be a URL...
            if looks_urlish(candidate):
                # ...paste it into the URL field.
                self.app.call_from_thread(self._paste, candidate)
                break

    def on_mount(self) -> None:
        """Configure the dialog once it's in the DOM."""
        if self._raindrop:
            self.query_one("#title", Input).value = self._raindrop.title
            self.query_one("#excerpt", TextArea).text = self._raindrop.excerpt
            self.query_one("#note", TextArea).text = self._raindrop.note
            self.query_one("#url", Input).value = self._raindrop.link
            self.query_one("#collection", Select).value = self._raindrop.collection
            self.query_one("#tags", Input).value = Raindrop.tags_to_string(
                self._raindrop.tags
            )
        if self._raindrop.link:
            self._get_tag_suggestions()
        else:
            self._suggest_link()

    @on(DescendantFocus, "#url")
    def _remember_url(self, event: DescendantFocus) -> None:
        """Save the URL on entry to the URL field.

        Args:
            event: The event to handle.
        """
        if isinstance(event.widget, Input):  # It should be, but narrow the type.
            self._last_url = event.widget.value.strip()

    @on(DescendantBlur, "#url")
    def _refresh_tag_suggestions(self, event: DescendantBlur) -> None:
        """Refresh the tag suggestions when leaving the URL field, having modified it."""
        if isinstance(event.widget, Input):  # It should be, but narrow the type.
            if (
                event.widget.value.strip()
                and event.widget.value.strip() != self._last_url
            ):
                self.query_one("#tag-suggestions").set_class(False, "got-suggestions")
                self._get_tag_suggestions()

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
                self._raindrop.edit(
                    title=self.query_one("#title", Input).value,
                    excerpt=self.query_one("#excerpt", TextArea).text,
                    note=self.query_one("#note", TextArea).text,
                    link=self.query_one("#url", Input).value,
                    collection=self.query_one("#collection", Select).value,
                    tags=Raindrop.string_to_tags(self.query_one("#tags", Input).value),
                    # TODO: More
                )
            )

    @on(Button.Pressed, "#cancel")
    def action_cancel(self) -> None:
        """Cancel the edit of the raindrop data."""
        self.dismiss(None)


### raindrop_input.py ends here
