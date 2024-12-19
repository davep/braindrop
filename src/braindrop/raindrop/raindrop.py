"""Provides a class for holding the content of a Raindrop."""

##############################################################################
# Backward compatibility.
from __future__ import annotations

##############################################################################
# Python imports.
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Literal, TypeAlias

##############################################################################
# Local imports.
from .parse_time import get_time
from .tag import Tag

##############################################################################
RaindropType: TypeAlias = Literal[
    "link", "article", "image", "video", "document", "audio"
]
"""The type of a Raindrop."""


##############################################################################
@dataclass(frozen=True)
class Media:
    """Class that holds media details."""

    link: str
    """The link for the media."""
    type: RaindropType
    """The type of the media."""

    @staticmethod
    def from_json(data: dict[str, Any]) -> Media:
        """Create a `Media` instance from JSON-sourced data.

        Args:
            data: The data to create the object from.

        Returns:
            A fresh `Media` instance.
        """
        return Media(link=data["link"], type=data["type"])


##############################################################################
@dataclass(frozen=True)
class Raindrop:
    """Class that holds the details of a Raindrop."""

    raw: dict[str, Any]
    """The raw data for the Raindrop."""
    identity: int
    """The ID of the raindrop."""
    collection: int
    """The ID of the collection that this raindrop belongs to."""
    cover: str
    """The URL to the cover."""
    created: datetime | None
    """The time when the Raindrop was created."""
    domain: str
    """The domain for a link."""
    excerpt: str
    """The excerpt for the Raindrop."""
    note: str
    """The note for the Raindrop."""
    last_update: datetime | None
    """The time the Raindrop was last updated."""
    link: str
    """The URL of the link for the Raindrop."""
    media: list[Media]
    """A list of media associated with the Raindrop."""
    tags: list[Tag]
    """The tags for the Raindrop."""
    title: str
    """The title of the Raindrop."""
    type: RaindropType
    """The type of the raindrop."""
    user: int
    """The ID of the owner of the Raindrop."""
    # TODO: More fields here.

    @staticmethod
    def from_json(data: dict[str, Any]) -> Raindrop:
        """Create a `Raindrop` instance from JSON-sourced data.

        Args:
            data: The data to create the object from.

        Returns:
            A fresh `Raindrop` instance.
        """
        return Raindrop(
            raw=data,
            identity=data["_id"],
            collection=data.get("collection", {}).get("$id", 0),
            cover=data.get("cover", ""),
            created=get_time(data, "created"),
            domain=data.get("domain", ""),
            excerpt=data.get("excerpt", ""),
            note=data.get("note", ""),
            last_update=get_time(data, "lastUpdate"),
            link=data.get("link", ""),
            media=[Media.from_json(media) for media in data.get("media", [])],
            tags=[Tag(tag) for tag in data.get("tags", [])],
            title=data.get("title", ""),
            type=data.get("type", "link"),
            user=data.get("user", {}).get("$id", ""),
        )


### raindrop.py ends here
