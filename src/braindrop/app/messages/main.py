"""The main application messages."""

##############################################################################
# Python imports.
from dataclasses import dataclass

##############################################################################
# Textual imports.
from textual.message import Message

##############################################################################
# Local imports.
from ...raindrop import Collection, RaindropType, Tag


##############################################################################
@dataclass
class ShowCollection(Message):
    """A message that requests that a particular collection is shown."""

    collection: Collection
    """The collection to show."""


##############################################################################
@dataclass
class ShowOfType(Message):
    """A message that requests that Raindrops of a particular type are shown."""

    raindrop_type: RaindropType
    """The raindrop type to filter on."""


##############################################################################
@dataclass
class ShowTagged(Message):
    """A message that requests that Raindrops with a particular tag are shown."""

    tag: Tag
    """The tag to show."""


### main.py ends here
