"""The commands used within the application."""

##############################################################################
# Python imports.
from dataclasses import dataclass

##############################################################################
# Local imports.
from ...raindrop import Collection, Tag
from ..data import Raindrops
from .base_command import Command


##############################################################################
class SearchCollections(Command):
    """Search for a collection by name and show its contents"""

    BINDING_KEY = "C"
    SHOW_IN_FOOTER = False


##############################################################################
@dataclass
class ShowCollection(Command):
    """A message that requests that a particular collection is shown."""

    collection: Collection
    """The collection to show."""


##############################################################################
@dataclass
class SearchTags(Command):
    """A message that requests that the tag-based command palette is shown."""

    BINDING_KEY = "t"
    SHOW_IN_FOOTER = False

    active_collection: Raindrops = Raindrops()
    """The active collection to search within."""

    @property
    def context_command(self) -> str:
        """The command in context."""
        return "Also tagged..." if self.active_collection.is_filtered else "Tagged..."

    @property
    def context_tooltip(self) -> str:
        """The tooltip in context."""
        return (
            "Add another tag to the current filter"
            if self.active_collection.is_filtered
            else "Filter the current collection with a tag"
        )


##############################################################################
@dataclass
class ShowTagged(Command):
    """A message that requests that Raindrops with a particular tag are shown."""

    tag: Tag
    """The tag to show."""


##############################################################################
class Logout(Command):
    """Forget your API token and remove the local raindrop cache"""

    BINDING_KEY = "f12"
    SHOW_IN_FOOTER = False


##############################################################################
class ClearFilters(Command):
    """Clear all tags and other filters."""

    BINDING_KEY = "f"
    SHOW_IN_FOOTER = False


##############################################################################
class VisitRaindrop(Command):
    """Open the web-based raindrop.io application in your default web browser"""

    COMMAND = "Visit raindrop.io"
    BINDING_KEY = "f2"
    FOOTER_TEXT = "raindrop.io"


##############################################################################
class Search(Command):
    """Search for text anywhere in the raindrops"""

    BINDING_KEY = "/"
    SHOW_IN_FOOTER = False


##############################################################################
class Details(Command):
    """Toggle the view of the current Raindrop's details"""

    BINDING_KEY = "f3"


##############################################################################
class TagOrder(Command):
    "Toggle the tags sort order between by-name and by-count"

    BINDING_KEY = "f4"


##############################################################################
class CompactMode(Command):
    "Toggle the compact mode for the Raindrop list"

    BINDING_KEY = "f5"


##############################################################################
class Redownload(Command):
    "Download a fresh copy of all data from raindrop.io"

    BINDING_KEY = "ctrl+r"
    SHOW_IN_FOOTER = False


##############################################################################
class ShowAll(Command):
    """Show all Raindrops"""

    BINDING_KEY = "a"
    SHOW_IN_FOOTER = False


##############################################################################
class ShowUnsorted(Command):
    "Show all unsorted Raindrops"

    BINDING_KEY = "u"
    SHOW_IN_FOOTER = False


##############################################################################
class ShowUntagged(Command):
    """Show all Raindrops that are lacking tags"""

    BINDING_KEY = "U"
    SHOW_IN_FOOTER = False


##############################################################################
class Escape(Command):
    "Back up through the panes, right to left, or exit the app if the navigation pane has focus"

    BINDING_KEY = "escape"
    SHOW_IN_FOOTER = False


##############################################################################
class Help(Command):
    """Show help for and information about the application"""

    BINDING_KEY = "f1, ?"


##############################################################################
class ChangeTheme(Command):
    """Change the application's theme"""

    BINDING_KEY = "f9"
    SHOW_IN_FOOTER = False


##############################################################################
class Quit(Command):
    """Quit the application"""

    BINDING_KEY = "f10, ctrl+q"


##############################################################################
class CopyLinkToClipboard(Command):
    """Copy the currently-highlighted link to the clipboard"""

    BINDING_KEY = "c"
    SHOW_IN_FOOTER = False


##############################################################################
class CheckTheWaybackMachine(Command):
    """Check if the currently-highlighted Raindrop is archived in the Wayback Machine"""

    BINDING_KEY = "w"
    SHOW_IN_FOOTER = False


##############################################################################
class AddRaindrop(Command):
    """Add a new raindrop"""

    BINDING_KEY = "n"
    SHOW_IN_FOOTER = False


##############################################################################
class EditRaindrop(Command):
    """Edit the currently-highlighted raindrop"""

    BINDING_KEY = "e"
    SHOW_IN_FOOTER = False


##############################################################################
class DeleteRaindrop(Command):
    """Delete the currently-highlighted raindrop"""

    BINDING_KEY = "d, delete"
    SHOW_IN_FOOTER = False


### commands.py ends here
