"""The commands used within the application."""

##############################################################################
# Python imports.
from dataclasses import dataclass

##############################################################################
# Textual imports.
from textual.message import Message

##############################################################################
# Local imports.
from ...raindrop import Collection, Tag


##############################################################################
class SearchCollections(Message):
    """A message that requests the collection-based command palette is shown."""


##############################################################################
@dataclass
class ShowCollection(Message):
    """A message that requests that a particular collection is shown."""

    collection: Collection
    """The collection to show."""


##############################################################################
class SearchTags(Message):
    """A message that requests that the tag-based command palette is shown."""


##############################################################################
@dataclass
class ShowTagged(Message):
    """A message that requests that Raindrops with a particular tag are shown."""

    tag: Tag
    """The tag to show."""


##############################################################################
class Logout(Message):
    """A message that requests that the 'logout' action takes placed."""


### commands.py ends here
