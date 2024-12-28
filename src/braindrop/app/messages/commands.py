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
class Command(Message):
    """Base class for all application command messages."""


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
    """A message that requests that the 'logout' action takes placed."""


### commands.py ends here
