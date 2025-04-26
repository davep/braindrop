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
from textual.message import Message
from textual.reactive import var
from textual.widgets import OptionList
from textual.widgets.option_list import Option

##############################################################################
# Textual enhanced imports.
from textual_enhanced.widgets import EnhancedOptionList

##############################################################################
# Local imports.
from ...raindrop import API, Collection, SpecialCollection
from ..commands import ShowAll, ShowUnsorted, ShowUntagged
from ..data import LocalData, Raindrops, TagCount, TypeCount
from ..messages import ShowCollection, ShowOfType, ShowTagged


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
class NavigationView(Option):
    """Base class for navigation options."""

    @property
    def message(self) -> Message:
        """The message for this option."""
        raise NotImplementedError

    def build_prompt(
        self,
        title: str,
        count: int,
        indent: int = 0,
        key: str | None = None,
        key_colour: str | None = None,
    ) -> RenderableType:
        """The prompt for the option.

        Args:
            title: The title for the prompt.
            count: The count for the prompt.
            key: The optional key for the prompt.
            key_colour: The optional colour for the key.

        Returns:
            A renderable that is the prompt.
        """
        prompt = Table.grid(expand=True)
        prompt.add_column(ratio=1)
        prompt.add_column(justify="right")
        prompt.add_row(
            f"{'[dim]>[/dim] ' * indent}{title}"
            + (f" [{key_colour or 'dim'}]\\[{key or ''}][/]" if key else ""),
            f"[dim i]{count}[/]",
        )
        return prompt


##############################################################################
class CollectionView(NavigationView):
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
        super().__init__(
            self.build_prompt(
                collection.title,
                count or collection.count,
                indent,
                key,
                key_colour,
            ),
            id=self.id_of(collection),
        )

    @property
    def message(self) -> Message:
        """The message for this option."""
        return ShowCollection(self._collection)


##############################################################################
class TypeView(NavigationView):
    """Option for showing a raindrop type."""

    def __init__(self, raindrop_type: TypeCount) -> None:
        """Initialise the object.

        Args:
           raindrop_type: The type to show.
        """
        self._type = raindrop_type
        """The type being viewed."""
        super().__init__(
            self.build_prompt(
                raindrop_type.type.capitalize(),
                raindrop_type.count,
            ),
            id=f"_type_{self._type.type}",
        )

    @property
    def message(self) -> Message:
        """The message for this option."""
        return ShowOfType(self._type.type)


##############################################################################
class TagView(NavigationView):
    """Option for showing a tag."""

    def __init__(self, tag: TagCount) -> None:
        """Initialise the object.

        Args:
            tag: The tag to show.
        """
        self._tag = tag
        """The tag being viewed."""
        super().__init__(
            self.build_prompt(str(tag.tag), tag.count), id=f"_tag_{tag.tag}"
        )

    @property
    def message(self) -> Message:
        """The message for this option."""
        return ShowTagged(self._tag.tag)


##############################################################################
class Navigation(EnhancedOptionList):
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
                self.add_option(
                    Title(f"{group.title} ({len(self.data.collections_within(group))})")
                )
                for collection in group.collections:
                    try:
                        self._add_children_for(
                            self._add_collection(self.data.collection(collection))
                        )
                    except self.data.UnknownCollection:
                        # It seems that the Raindrop API can sometimes say
                        # there's a collection ID in a group where the
                        # collection ID isn't in the actual collections the
                        # API gives us. So here we just ignore it.
                        #
                        # https://github.com/davep/braindrop/issues/104
                        pass

    @staticmethod
    def _by_name(tags: list[TagCount]) -> list[TagCount]:
        """Return a given list of tags sorted by tag name.

        Args:
            tags: The tags to sort.

        Returns:
            The sorted list of tags.
        """
        return sorted(tags, key=TagCount.the_tag())

    @staticmethod
    def _by_count(tags: list[TagCount]) -> list[TagCount]:
        """Return a given list of tags sorted by count.

        Args:
            tags: The tags to sort.

        Returns:
            The sorted list of tags.
        """
        return sorted(tags, key=TagCount.the_count(), reverse=True)

    def _show_types_for(self, collection: Raindrops) -> None:
        """Show types relating to a given collection.

        Args:
            collection: The collection to show the types for.
        """
        with self.preserved_highlight:
            if self.data is not None and (types := collection.types):
                self.add_option(Title(f"Types ({len(types)})"))
                for raindrop_type in sorted(types):
                    self.add_option(TypeView(raindrop_type))

    def _show_tags_for(self, collection: Raindrops) -> None:
        """Show tags relating a given collection.

        Args:
            collection: The collection to show the tags for.
        """
        with self.preserved_highlight:
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
        with self.preserved_highlight:
            self._main_navigation()
            self._show_types_for(self.active_collection)
            self._show_tags_for(self.active_collection)

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
        assert isinstance(message.option, NavigationView)
        self.post_message(message.option.message)


### navigation.py ends here
