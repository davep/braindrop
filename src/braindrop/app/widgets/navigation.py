"""Provides the main navigation widget."""

##############################################################################
# Textual imports.
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.reactive import var

##############################################################################
# Local imports.
from ...raindrop import API, Collection
from ..data import Raindrops
from .group import Group


##############################################################################
class Navigation(Vertical):
    """The main application navigation widget."""

    data: var[Raindrops | None] = var(None)
    """Holds a reference to the Raindrop data we're going to handle."""

    def compose(self) -> ComposeResult:
        """Compose the content of the widget."""
        yield Group(id="special")
        yield Vertical(id="user-groups")

    def _add_children_for(
        self,
        parent: Collection,
        group: Group,
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
                group.add_collection(collection, indent)
                self._add_children_for(collection, group, indent)

    async def watch_data(self) -> None:
        """Handle the data being changed."""

        # First off, clear out the display of the user's groups.
        user_groups = self.query_one("#user-groups")
        user_groups.remove_children()

        # If we don't have data or we don't know the user, we're all done
        # here.
        if self.data is None or self.data.user is None:
            return

        # Populate the groups.
        for group in self.data.user.groups:
            new_group = Group(group.title)
            await user_groups.mount(new_group)
            for collection in group.collections:
                new_group.add_collection(self.data.collection(collection))
                self._add_children_for(self.data.collection(collection), new_group)

    def on_mount(self) -> None:
        """Configure the widget once the DOM is mounted."""
        self.query_one("#special", Group).add_collections(
            API.SpecialCollection.ALL(),
            API.SpecialCollection.UNSORTED(),
            API.SpecialCollection.TRASH(),
        )


### navigation.py ends here
