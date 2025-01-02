"""Provides the main navigation widget."""

##############################################################################
# Backward compatibility.
from __future__ import annotations

##############################################################################
# Python imports.
from typing import Any

##############################################################################
# Rich imports.
from rich.console import Group, RenderableType
from rich.rule import Rule
from rich.table import Table

##############################################################################
# Textual imports.
from textual import on
from textual.reactive import var
from textual.widgets import OptionList
from textual.widgets.option_list import Option

##############################################################################
# Local imports.
from ...raindrop import API, Collection, SpecialCollection, Tag, TagData
from ..data import LocalData, Raindrops
from ..messages import ShowAll, ShowCollection, ShowTagged, ShowUnsorted, ShowUntagged
from .extended_option_list import OptionListEx


##############################################################################
class CollectionView(Option):
    """Class that holds details of the collection to view."""

    @staticmethod
    def id_of(collection: Collection) -> str:
        """Get the ID of a given collection.

        Args:
            collection: The collection to get an ID for.

        Returns:
            The ID to use for the collection.
        """
        return f"collection-{collection.identity}"

    def __init__(
        self,
        collection: Collection,
        indent: int = 0,
        key: str | None = None,
        key_colour: str | None = None,
        count: int = 0,
    ) -> None:
        """Initialise the object.

        Args:
            collection: The collection to show.
            indent: The indent level for the collection.
            key: The associated with the collection.
            key_colour: The colour to show the key in.
            count: The count of raindrops in the collection.
        """
        self._collection = collection
        """The collection being viewed."""
        self._indent = indent
        """The indent level for the collection."""
        self._key = key
        """The key associated with this collection, if any."""
        self._key_colour = key_colour or "dim"
        """The colour to show the key in."""
        self._count = count or collection.count
        """The count of raindrops in this collection."""
        super().__init__(self.prompt, id=self.id_of(collection))

    @property
    def collection(self) -> Collection:
        """The collection."""
        return self._collection

    @property
    def prompt(self) -> RenderableType:
        """The prompt for the collection.

        Returns:
            A renderable that is the prompt.
        """
        prompt = Table.grid(expand=True)
        prompt.add_column(ratio=1)
        prompt.add_column(justify="right")
        prompt.add_row(
            f"{'[dim]>[/dim] ' * self._indent}{self._collection.title}"
            + (f" [{self._key_colour}]\\[{self._key or ''}][/]" if self._key else ""),
            f"[dim i]{self._count}[/]",
        )
        return prompt


##############################################################################
class TagView(Option):
    """Option for showing a tag."""

    def __init__(self, tag: TagData) -> None:
        """Initialise the object.

        Args:
            tag: The tag to show.
        """
        self._tag = tag
        """The tag being viewed."""
        super().__init__(self.prompt, id=f"_tag_{tag.tag}")

    @property
    def prompt(self) -> RenderableType:
        """The prompt for the tag.

        Returns:
            A renderable that is the prompt.
        """
        prompt = Table.grid(expand=True)
        prompt.add_column(ratio=1)
        prompt.add_column(justify="right")
        prompt.add_row(str(self._tag.tag), f"[dim i]{self._tag.count}[/]")
        return prompt

    @property
    def tag_data(self) -> TagData:
        """The tag data."""
        return self._tag

    @property
    def tag(self) -> Tag:
        """The tag."""
        return self.tag_data.tag


##############################################################################
class Title(Option):
    """Option for showing a title."""

    def __init__(self, title: str) -> None:
        """Initialise the object.

        Args:
            title: The title to show.
        """
        super().__init__(
            Group("", Rule(title, style="bold dim")),
            disabled=True,
            id=f"_title_{title}",
        )


##############################################################################
class Navigation(OptionListEx):
    """The main application navigation widget."""

    HELP = """
    ## The Navigation Panel

    This is the navigation panel. Here you can select a collection to view
    as well as pick tags to filter the view with.
    """

    data: var[LocalData | None] = var(None, always_update=True)
    """Holds a reference to the Raindrop data we're going to handle."""

    active_collection: var[Raindrops] = var(Raindrops(), always_update=True)
    """The currently-active collection being displayed."""

    tags_by_count: var[bool] = var(False)
    """Should the tags be sorted by count?"""

    def __init__(
        self,
        api: API,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        """Initialise the object.

        Args:
            api: The API client object.
            id: The ID of the widget description in the DOM.
            classes: The CSS classes of the widget description.
            disabled: Whether the widget description is disabled or not.
        """
        super().__init__(id=id, classes=classes, disabled=disabled)
        self._api = api
        """The API client object."""

    def on_mount(self) -> None:
        """Configure the widget once the DIM is ready."""

        def redraw(*_: Any) -> None:
            """Force a redraw of the content of the widget."""
            self.active_collection = self.active_collection

        # While the user will almost never notice, if the theme changes the
        # accent colour for the keys will go out of sync, so here we watch
        # for a theme change and then force a redraw of the content so we do
        # keep in sync.
        self.app.theme_changed_signal.subscribe(self, redraw)

    def highlight_collection(self, collection: Collection) -> None:
        """Ensure the given collection is highlighted.

        Args:
            collection: The collection to highlight.
        """
        self.highlighted = self.get_option_index(CollectionView.id_of(collection))

    def select_collection(self, collection: Collection) -> None:
        """Highlight and select a given collection."""
        self.highlight_collection(collection)
        self.call_later(self.run_action, "select")

    def show_all(self) -> None:
        """Show the special collection that is all the Raindrops."""
        self.select_collection(SpecialCollection.ALL())

    def show_untagged(self) -> None:
        """Show the special collection that is all untagged Raindrops."""
        self.select_collection(SpecialCollection.UNTAGGED())

    def show_unsorted(self) -> None:
        """Show the special collection that is the unsorted Raindrops."""
        self.select_collection(SpecialCollection.UNSORTED())

    def _add_collection(
        self, collection: Collection, indent: int = 0, key: str | None = None
    ) -> Collection:
        """Add a collection to the widget.

        Args:
            collection: The collection to add.
            indent: The indent level to add it at.
            key: The shortcut key to use, if any.

        Returns:
            The collection.
        """
        self.add_option(
            CollectionView(
                collection,
                indent,
                key,
                None
                if self.app.current_theme is None
                else self.app.current_theme.accent,
                0 if self.data is None else self.data.collection_size(collection),
            )
        )
        return collection

    def _add_specials(self) -> None:
        """Add the special collections."""
        self._add_collection(SpecialCollection.ALL(), key=ShowAll.key_binding())
        self._add_collection(
            SpecialCollection.UNSORTED(), key=ShowUnsorted.key_binding()
        )
        self._add_collection(
            SpecialCollection.UNTAGGED(), key=ShowUntagged.key_binding()
        )
        if self.data is not None and self.data.user is not None and self.data.user.pro:
            self._add_collection(SpecialCollection.BROKEN())
        self._add_collection(SpecialCollection.TRASH())

    def _add_children_for(
        self,
        parent: Collection,
        indent: int = 0,
    ) -> None:
        """Add child collections for the given collection.

        Args:
            parent: The parent collection to add the children for.
            indent: The indent level of the parent.
        """
        assert self.data is not None
        indent += 1
        for collection in self.data.collections:
            if collection.parent == parent.identity:
                self._add_children_for(self._add_collection(collection, indent), indent)

    def _main_navigation(self) -> None:
        """Set up the main navigation."""
        with self.preserved_highlight:
            # First off, clear out the display of the user's groups.
            self.clear_options()._add_specials()
            # If we don't have data or we don't know the user, we're all done
            # here.
            if self.data is None or self.data.user is None:
                return
            # Populate the groups.
            for group in self.data.user.groups:
                self.add_option(Title(f"{group.title} ({len(self.data.collections)})"))
                for collection in group.collections:
                    self._add_children_for(
                        self._add_collection(self.data.collection(collection))
                    )

    @staticmethod
    def _by_name(tags: list[TagData]) -> list[TagData]:
        """Return a given list of tags sorted by tag name.

        Args:
            tags: The tags to sort.

        Returns:
            The sorted list of tags.
        """
        return sorted(tags, key=TagData.the_tag())

    @staticmethod
    def _by_count(tags: list[TagData]) -> list[TagData]:
        """Return a given list of tags sorted by count.

        Args:
            tags: The tags to sort.

        Returns:
            The sorted list of tags.
        """
        return sorted(tags, key=TagData.the_count(), reverse=True)

    def _show_tags_for(self, collection: Raindrops) -> None:
        """Show tags relating a given collection.

        Args:
            collection: The collection to show the tags for.
        """
        with self.preserved_highlight:
            self._main_navigation()
            if self.data is not None and (tags := collection.tags):
                self.add_option(Title(f"Tags ({len(tags)})"))
                for tag in (self._by_count if self.tags_by_count else self._by_name)(
                    tags
                ):
                    self.add_option(TagView(tag))

    def watch_data(self) -> None:
        """Handle the data being changed."""
        self._main_navigation()
        self.active_collection = self.active_collection

    def watch_active_collection(self) -> None:
        """React to the currently-active collection being changed."""
        self._show_tags_for(self.active_collection)
        self._refresh_lines()  # https://github.com/Textualize/textual/issues/5431

    def watch_tags_by_count(self) -> None:
        """React to the tags sort ordering being changed."""
        self.active_collection = self.active_collection

    @on(OptionList.OptionSelected)
    def _collection_selected(self, message: OptionList.OptionSelected) -> None:
        """Handle the user selecting a collection.

        Args:
            message: The message associated with the request.
        """
        message.stop()
        if isinstance(message.option, CollectionView):
            self.post_message(ShowCollection(message.option.collection))
        elif isinstance(message.option, TagView):
            self.post_message(ShowTagged(message.option.tag))


### navigation.py ends here
