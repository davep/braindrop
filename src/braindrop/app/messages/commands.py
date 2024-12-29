"""The commands used within the application."""

##############################################################################
# Python imports.
from dataclasses import dataclass

##############################################################################
# Local imports.
from ...raindrop import Collection, Tag
from .base_command import Command


##############################################################################
class SearchCollections(Command):
    """A message that requests the collection-based command palette is shown."""


##############################################################################
@dataclass
class ShowCollection(Command):
    """A message that requests that a particular collection is shown."""

    collection: Collection
    """The collection to show."""


##############################################################################
class SearchTags(Command):
    """A message that requests that the tag-based command palette is shown."""


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


##############################################################################
class ClearFilters(Command):
    """Clear all tags and other filters."""

    BINDING_KEY = "c"
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
class Escape(Command):
    "Back up through the panes, right to left, or exit the app if the navigation pane has focus"

    BINDING_KEY = "escape"
    SHOW_IN_FOOTER = False


### commands.py ends here
