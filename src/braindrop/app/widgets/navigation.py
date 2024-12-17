"""Provides the main navigation widget."""

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
from ...raindrop import API, Collection, Group, Raindrop, Tag
from ..commands import ShowCollection
from ..data import Raindrops


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

    def __init__(self, tag: Tag) -> None:
        """Initialise the object.

        Args:
            tag: The tag to show.
        """
        super().__init__(f"{tag.name} [dim]({tag.count})[/]", id=f"_tag_{tag.name}")


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
class Navigation(OptionList):
    """The main application navigation widget."""

    data: var[Raindrops | None] = var(None)
    """Holds a reference to the Raindrop data we're going to handle."""

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
        highlighted = self.highlighted
        try:
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
        finally:
            self.highlighted = highlighted

    def watch_data(self) -> None:
        """Handle the data being changed."""
        self._main_navigation()

    def _show_tags_for(self, collection: list[Raindrop]) -> None:
        """Show tags relating a given collection.

        Args:
            collection: The collection to show the tags for.
        """
        self._main_navigation()
        if (
            self.data is not None
            and (tags := self.data.tags_of(collection)) is not None
        ):
            self.add_option(Title("Tags"))
            for tag in tags:
                self.add_option(TagView(tag))

    def now_showing(self, collection: list[Raindrop]) -> None:
        """Configure the navigation based on the given collection.

        Args:
            collection: The collection that is now showing.
        """
        self._show_tags_for(collection)

    @on(OptionList.OptionSelected)
    def _collection_selected(self, message: OptionList.OptionSelected) -> None:
        """Handle the user selecting a collection.

        Args:
            message: The message associated with the request.
        """
        message.stop()
        if isinstance(message.option, CollectionView):
            self.post_message(ShowCollection(message.option.collection))


### navigation.py ends here
