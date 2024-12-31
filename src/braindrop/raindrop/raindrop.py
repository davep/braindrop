"""Provides a class for holding the content of a Raindrop."""

##############################################################################
# Backward compatibility.
from __future__ import annotations

##############################################################################
# Python imports.
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Literal, TypeAlias

##############################################################################
# Local imports.
from .collection import SpecialCollection
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

    raw: dict[str, Any] = field(default_factory=dict)
    """The raw data for the Raindrop."""
    identity: int = -1
    """The ID of the raindrop."""
    collection: int = SpecialCollection.UNSORTED
    """The ID of the collection that this raindrop belongs to."""
    cover: str = ""
    """The URL to the cover."""
    created: datetime | None = None
    """The time when the Raindrop was created."""
    domain: str = ""
    """The domain for a link."""
    excerpt: str = ""
    """The excerpt for the Raindrop."""
    note: str = ""
    """The note for the Raindrop."""
    last_update: datetime | None = None
    """The time the Raindrop was last updated."""
    link: str = ""
    """The URL of the link for the Raindrop."""
    media: list[Media] = field(default_factory=list)
    """A list of media associated with the Raindrop."""
    tags: list[Tag] = field(default_factory=list)
    """The tags for the Raindrop."""
    title: str = ""
    """The title of the Raindrop."""
    type: RaindropType = "link"
    """The type of the raindrop."""
    user: int = -1
    """The ID of the owner of the Raindrop."""
    broken: bool = False
    """Is the Raindrop a broken link?"""
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
            broken=data.get("broken", False),
        )

    @property
    def as_json(self) -> dict[str, Any]:
        """The Raindrop as a JSON-friendly dictionary."""
        return {
            "collection": {"$id": self.collection},
            "cover": self.cover,
            "created": self.created,
            "domain": self.domain,
            "excerpt": self.excerpt,
            "note": self.note,
            "lastUpdate": self.last_update,
            "link": self.link,
            # media
            "tags": [str(tag) for tag in self.tags],
            "title": self.title,
            "type": self.type,
            # user
            "broken": False,
        }

    @property
    def is_unsorted(self) -> bool:
        """Is this raidnrop unsorted?"""
        return self.collection == SpecialCollection.UNSORTED

    def is_tagged(self, *tags: Tag) -> bool:
        """Is the Raindrop tagged with the given tags?

        Args:
            tags: The tags to look for.

        Returns:
            `True` if the Raindrop contains those tags, `False` if not.
        """
        return set(tags) <= set(self.tags)

    def __contains__(self, search_text: str) -> bool:
        """Performs a case-insensitive search for the text anywhere in the Raindrop.

        Args:
            search_text: The text to search for.

        Returns:
            `True` if the text can be found, `False` if not.
        """
        return search_text.casefold() in (
            f"{self.excerpt.casefold()} {self.title.casefold()} {self.note.casefold()} "
            f"{' '.join(str(tag) for tag in self.tags).casefold()}"
        )


### raindrop.py ends here
