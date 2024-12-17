"""Provides the main navigation widget."""

##############################################################################
# Rich imports.
from rich.align import Align

##############################################################################
# Textual imports.
from textual import on
from textual.reactive import var
from textual.widgets import OptionList
from textual.widgets.option_list import Option

##############################################################################
# Local imports.
from ...raindrop import API, Collection, Group
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
class GroupTitle(Option):
    """Option for showing the title of a group."""

    def __init__(self, group: Group) -> None:
        """Initialise the object.

        Args:
            group: The group to show the title for.
        """
        super().__init__(Align.right(group.title), disabled=True)
        self._group = group
        """The group this title is associated with."""


##############################################################################
class Navigation(OptionList):
    """The main application navigation widget."""

    data: var[Raindrops | None] = var(None)
    """Holds a reference to the Raindrop data we're going to handle."""

    def _add_collection(self, collection: Collection, indent: int = 0) -> None:
        """Add a collection to the widget.

        Args:
            collection: The collection to add.
            indent: The indent level to add it at.
        """
        self.add_option(CollectionView(collection, indent))

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

    def watch_data(self) -> None:
        """Handle the data being changed."""

        # First off, clear out the display of the user's groups.
        self.clear_options()._add_specials()

        # If we don't have data or we don't know the user, we're all done
        # here.
        if self.data is None or self.data.user is None:
            return

        # Populate the groups.
        for group in self.data.user.groups:
            self.add_option(GroupTitle(group))
            for collection in group.collections:
                self._add_collection(self.data.collection(collection))
                self._add_children_for(self.data.collection(collection))

    @on(OptionList.OptionSelected)
    def _collection_selected(self, message: OptionList.OptionSelected) -> None:
        """Handle the user selecting a collection.

        Args:
            message: The message associated with the request.
        """
        assert isinstance(message.option, CollectionView)
        message.stop()
        self.post_message(ShowCollection(message.option.collection))


### navigation.py ends here
