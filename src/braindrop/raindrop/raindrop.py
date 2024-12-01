"""Provides a class for holding the content of a Raindrop."""

##############################################################################
# Python imports.
from dataclasses import dataclass
from datetime import datetime
from typing import Literal, TypeAlias

##############################################################################
RaindropType: TypeAlias = Literal[
    "link", "article", "image", "video", "document", "audio"
]
"""The type of a Raindrop."""


##############################################################################
@dataclass
class Media:
    """Class that holds media details."""

    link: str
    """The link for the media."""
    type: RaindropType
    """The type of the media."""


##############################################################################
@dataclass
class Raindrop:
    """Class that holds the details of a Raindrop."""

    identity: int
    """The ID of the raindrop."""
    collection: int
    """The ID of the collection that this raindrop belongs to."""
    cover: str
    """The URL to the cover."""
    created: datetime
    """The time when the Raindrop was created."""
    domain: str
    """The domain for a link."""
    excerpt: str
    """The excerpt for the Raindrop."""
    note: str
    """The note for the Raindrop."""
    last_update: datetime
    """The time the Raindrop was last updated."""
    link: str
    """The URL of the link for the Raindrop."""
    media: list[Media]
    """A list of media associated with the Raindrop."""
    tags: list[str]
    """The tags for the Raindrop."""
    title: str
    """The title of the Raindrop."""
    type: RaindropType
    """The type of the raindrop."""
    user: int
    """The ID of the owner of the Raindrop."""
    # TODO: More fields here.


### raindrop.py ends here
