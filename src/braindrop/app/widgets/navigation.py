"""Provides the main navigation widget."""

##############################################################################
# Backward compatibility.
from __future__ import annotations

##############################################################################
# Python imports.
from types import TracebackType
from typing import Self

##############################################################################
# Rich imports.
from rich.align import Align

##############################################################################
# Textual imports.
from textual import on
from textual.reactive import var
from textual.widgets import OptionList
from textual.widgets.option_list import Option, OptionDoesNotExist

##############################################################################
# Local imports.
from ...raindrop import API, Collection, Raindrop, Tag, TagData
from ..data import Raindrops
from ..messages import ShowCollection, ShowTagged


##############################################################################
class CollectionView(Option):
    """Class that holds details of the collection to view."""

    def __init__(self, collection: Collection, indent: int = 0) -> None:
        """Initialise the object.

        Args:
            collection: The collection to show.
            indent: The indent level for the collection.
        """
        super().__init__(f"{'[dim]>[/dim] ' * indent}{collection.title}")
        self._collection = collection
        """The collection being viewed."""

    @property
    def collection(self) -> Collection:
        """The collection."""
        return self._collection


##############################################################################
class TagView(Option):
    """Option for showing a tag."""

    def __init__(self, tag: TagData) -> None:
        """Initialise the object.

        Args:
            tag: The tag to show.
        """
        super().__init__(f"{tag.tag} [dim]({tag.count})[/]", id=f"_tag_{tag.tag}")
        self._tag = tag
        """The tag being viewed."""

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
        super().__init__(Align.right(title), disabled=True, id=title)


##############################################################################
class PreservedHighlight:
    """Context manager class to preserve an `OptionList` location.

    If the highlighted option has an ID, an attempt will be made to get back
    to that option; otherwise we return to the option in the same location.
    """

    def __init__(self, option_list: OptionList) -> None:
        """Initialise the object.

        Args:
            option_list: The `OptionList` to preserve the location for.
        """
        self._option_list = option_list
        """The option list we're preserving the location for."""
        self._highlighted = option_list.highlighted
        """The highlight that we should try to go back to."""
        self._option_id = (
            option_list.get_option_at_index(self._highlighted).id
            if self._highlighted is not None
            else None
        )
        """The ID of the option to try and get back to, or `None`."""

    def __enter__(self) -> Self:
        """Handle entry to the context."""
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_traceback: TracebackType | None,
    ) -> None:
        """Handle exit from the context."""
        del exc_type, exc_val, exc_traceback
        try:
            self._option_list.highlighted = (
                self._highlighted
                if self._option_id is None
                else self._option_list.get_option_index(self._option_id)
            )
        except OptionDoesNotExist:
            self._option_list.highlighted = self._highlighted


##############################################################################
class Navigation(OptionList):
    """The main application navigation widget."""

    data: var[Raindrops | None] = var(None)
    """Holds a reference to the Raindrop data we're going to handle."""

    active_collection: var[list[Raindrop]] = var(list, always_update=True)
    """The currently-active collection being displayed."""

    tags_by_count: var[bool] = var(False)
    """Should the tags be sorted by count?"""

    def __init__(
        self,
        api: API,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ):
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

    def _add_collection(self, collection: Collection, indent: int = 0) -> Collection:
        """Add a collection to the widget.

        Args:
            collection: The collection to add.
            indent: The indent level to add it at.

        Returns:
            The collection.
        """
        self.add_option(CollectionView(collection, indent))
        return collection

    def _add_collections(self, *collections: Collection, indent: int = 0) -> None:
        """Add many collections to the widget.

        Args:
            collections: The collections to add to the widget.
            indent: The indent level to add it at.
        """
        for collection in collections:
            self._add_collection(collection, indent)

    def _add_specials(self) -> None:
        """Add the special collections."""
        self._add_collections(
            API.SpecialCollection.ALL(),
            API.SpecialCollection.UNSORTED(),
            API.SpecialCollection.TRASH(),
        )

    def _add_children_for(
        self,
        parent: Collection,
        indent: int = 0,
    ) -> None:
        """Add child collections for the given collection.

        Args:
            parent: The parent collection to add the children for.
            group: The group to add the children to.
            indent: The indent level of the parent.
        """
        assert self.data is not None
        indent += 1
        for collection in self.data.collections:
            if collection.parent == parent.identity:
                self._add_collection(collection, indent)
                self._add_children_for(collection, indent)

    def _main_navigation(self) -> None:
        """Set up the main navigation."""
        with PreservedHighlight(self):
            # First off, clear out the display of the user's groups.
            self.clear_options()._add_specials()
            # If we don't have data or we don't know the user, we're all done
            # here.
            if self.data is None or self.data.user is None:
                return
            # Populate the groups.
            for group in self.data.user.groups:
                self.add_option(Title(group.title))
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

    def _show_tags_for(self, collection: list[Raindrop]) -> None:
        """Show tags relating a given collection.

        Args:
            collection: The collection to show the tags for.
        """
        with PreservedHighlight(self):
            self._main_navigation()
            if self.data is not None and (tags := self.data.tags_of(collection)):
                self.add_option(Title("Tags"))
                for tag in (self._by_count if self.tags_by_count else self._by_name)(
                    tags
                ):
                    self.add_option(TagView(tag))

    def watch_data(self) -> None:
        """Handle the data being changed."""
        self._main_navigation()

    def watch_tags_by_count(self) -> None:
        """React to the tags sort ordering being changed."""
        self.active_collection = self.active_collection

    def watch_active_collection(self) -> None:
        """React to the currently-active collection being changed."""
        self._show_tags_for(self.active_collection)

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
