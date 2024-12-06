"""Provides a widget that shows the content of a group."""

##############################################################################
# Textual imports.
from textual import on
from textual.widgets import OptionList
from textual.widgets.option_list import Option

##############################################################################
# Local imports.
from ...raindrop import Collection
from ..commands import ShowCollection


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
class Group(OptionList):
    """Widget for showing a Raindrop group."""

    DEFAULT_CSS = """
    Group {
        border-title-align: right;
        border-title-color: $text-accent;
        border: none;
        border-top: panel $surface;

        &:focus {
            border: none;
            border-top: panel $surface;
        }
    }
    """

    def __init__(
        self,
        title: str = "",
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        """Initialise the widget.

        Args:
            title: The title of the group.
            id: The ID of the widget description in the DOM.
            classes: The CSS classes of the widget description.
            disabled: Whether the widget description is disabled or not.
        """
        super().__init__(id=id, classes=classes, disabled=disabled)
        self.border_title = title

    def add_collection(self, collection: Collection, indent: int = 0) -> None:
        """Add a collection to the widget.

        Args:
            collection: The collection to add.
            indent: The indent level to add it at.
        """
        self.add_option(CollectionView(collection, indent))

    def add_collections(self, *collections: Collection, indent: int = 0) -> None:
        """Add many collections to the widget.

        Args:
            collections: The collections to add to the widget.
            indent: The indent level to add it at.
        """
        for collection in collections:
            self.add_collection(collection, indent)

    @on(OptionList.OptionSelected)
    def _collection_selected(self, message: OptionList.OptionSelected) -> None:
        """Handle the user selecting a collection.

        Args:
            message: The message associated with the request.
        """
        assert isinstance(message.option, CollectionView)
        message.stop()
        self.post_message(ShowCollection(message.option.collection))


### group.py ends here
