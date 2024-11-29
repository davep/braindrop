"""Provides a widget for displaying and handling a user's groups."""

##############################################################################
# Python imports.
from typing import Final

##############################################################################
# Rich imports.
from rich.emoji import Emoji

##############################################################################
# Textual imports.
from textual.widgets import OptionList
from textual.widgets.option_list import Option, Separator

##############################################################################
# Local imports.
from ...raindrop import Collection, Raindrop, User


##############################################################################
class CollectionOption(Option):
    """OptionList option class for holding details of a collection."""

    COLLECTION_ICON: Final[str] = Emoji.replace(":file_folder:")
    """The icon to use for a collection."""

    def __init__(self, collection: Collection, indent: int = 0) -> None:
        """Initialise the object.

        Args:
            collection: The collection to display with this option.
        """
        super().__init__(
            f"{'  ' * indent}{self.COLLECTION_ICON} {collection.title}",
            id=f"collection-{collection.identity}",
        )
        self.collection = collection
        """The reference to the collection."""


##############################################################################
class Groups(OptionList):
    """A widget for displaying a Raindrop user's groups."""

    def __init__(
        self,
        api: Raindrop,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ):
        """Initialise the object.

        Args:
            api: A reference to the Raindrop API client.
            id: The ID of the groups widget in the DOM.
            classes: The CSS classes of the groups widget.
            disabled: Whether the groups widget is disabled or not.
        """
        super().__init__(id=id, classes=classes, disabled=disabled)
        self._api = api
        """A reference to the Raindrop API client object."""

    def _add_children_for(
        self, parent: int, collections: dict[int, Collection], indent: int = 0
    ) -> None:
        """Add child collections for the given collection.

        Args:
            parent: The ID of the parent collection.
            collections: The dictionary of known collections.
            indent: The indent level of the parent.
        """
        indent += 1
        for _, collection in collections.items():
            if collection.parent == parent:
                self.add_option(CollectionOption(collection, indent))._add_children_for(
                    collection.identity, collections, indent
                )

    async def show_for_user(self, user: User) -> None:
        """Show the groups and their content for the given user.

        Args:
            The user to show the groups for.
        """
        collections = {
            collection.identity: collection
            for collection in await self._api.collections("all")
        }
        self.clear_options()
        for group in user.groups:
            self.add_options([Separator(), f"[b]{group.title}[/b]", Separator()])
            for collection_id in group.collections:
                self.add_option(
                    CollectionOption(collections[collection_id])
                )._add_children_for(collection_id, collections)


### groups.py ends here
