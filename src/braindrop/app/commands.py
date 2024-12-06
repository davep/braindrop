"""The commands used within the application."""

##############################################################################
# Python imports.
from dataclasses import dataclass

##############################################################################
# Textual imports.
from textual.message import Message

##############################################################################
# Local imports.
from ..raindrop import Collection


##############################################################################
@dataclass
class ShowCollection(Message):
    """A message that requests that a particular collection is shown."""

    collection: Collection
    """The collection to show."""


### commands.py ends here
