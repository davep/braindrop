"""Provides the main navigation widget."""

##############################################################################
# Textual imports.
from textual.app import ComposeResult
from textual.containers import Vertical

##############################################################################
# Local imports.
from ...raindrop import API, Collection
from .group import Group


##############################################################################
class Navigation(Vertical):
    """The main application navigation widget."""

    def __init__(
        self, api: API, classes: str | None = None, disabled: bool = False
    ) -> None:
        """Initialise the widget.

        Args:
            api: A reference to the Raindrop API client.
            classes: The CSS classes of the widget description.
            disabled: Whether the widget description is disabled or not.
        """
        super().__init__(classes=classes, disabled=disabled)
        self._api = api
        """The Raindrop API client object."""

    def compose(self) -> ComposeResult:
        """Compose the content of the widget."""
        yield Group(id="special")
        yield Vertical(id="user-groups")

    def _add_children_for(
        self,
        parent: Collection,
        group: Group,
        collections: dict[int, Collection],
        indent: int = 0,
    ) -> None:
        """Add child collections for the given collection.

        Args:
            parent: The parent collection to add the children for.
            group: The group to add the children to.
            collections: A dictionary of all known collections.
            indent: The indent level of the parent.
        """
        indent += 1
        for collection in collections.values():
            if collection.parent == parent.identity:
                group.add_collection(collection, indent)
                self._add_children_for(collection, group, collections, indent)

    async def refresh_user_groups(self) -> None:
        """Refresh the user groups display."""
        user_groups = self.query_one("#user-groups")
        user_groups.remove_children()
        if user := await self._api.user():
            collections = {
                collection.identity: collection
                for collection in await self._api.collections("all")
            }
            for group in user.groups:
                new_group = Group(group.title)
                await user_groups.mount(new_group)
                for collection in group.collections:
                    new_group.add_collection(collections[collection])
                    self._add_children_for(
                        collections[collection], new_group, collections
                    )

    async def on_mount(self) -> None:
        """Configure the widget once the DOM is mounted."""
        self.query_one("#special", Group).add_collection(API.SpecialCollection.ALL())
        self.query_one("#special", Group).add_collection(
            API.SpecialCollection.UNSORTED()
        )
        self.query_one("#special", Group).add_collection(API.SpecialCollection.TRASH())
        await self.refresh_user_groups()


### navigation.py ends here
