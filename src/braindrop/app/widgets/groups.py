"""Provides a widget for displaying and handling a user's groups."""

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

    def __init__(self, collection: Collection) -> None:
        """Initialise the object.

        Args:
            collection: The collection to display with this option.
        """
        super().__init__(collection.title, id=f"collection-{collection.identity}")


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
            self.add_options([Separator(), group.title, Separator()])
            for collection_id in group.collections:
                self.add_option(CollectionOption(collections[collection_id]))


### groups.py ends here
