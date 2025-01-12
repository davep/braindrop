"""Provides a class for holding the content of a Raindrop."""

##############################################################################
# Backward compatibility.
from __future__ import annotations

##############################################################################
# Python imports.
from dataclasses import dataclass, field, replace
from datetime import datetime
from typing import Any, Final, Iterable, Literal, TypeAlias

##############################################################################
# Local imports.
from .collection import SpecialCollection
from .tag import Tag
from .time_tools import get_time, json_time

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
UNSAVED_IDENTITY: Final[int] = -1
"""The ID used to mark a Raindrop as unsaved."""


##############################################################################
@dataclass(frozen=True)
class Raindrop:
    """Class that holds the details of a Raindrop."""

    raw: dict[str, Any] = field(default_factory=dict)
    """The raw data for the Raindrop."""
    identity: int = UNSAVED_IDENTITY
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
        """The Raindrop as a JSON-friendly dictionary.

        Notes:
            The data in here is a subset of all of the data and is only
            intended for use with returning to the raindrop.io API.
        """
        return {
            "collection": {"$id": self.collection},
            "cover": self.cover,
            "created": json_time(self.created),
            "domain": self.domain,
            "excerpt": self.excerpt,
            "note": self.note,
            "lastUpdate": json_time(self.last_update),
            "link": self.link,
            # media
            "tags": [str(tag) for tag in self.tags],
            "title": self.title,
            "type": self.type,
            # user
            "broken": False,
        }

    def edit(self, **replacements: Any) -> Raindrop:
        """Edit some values in the raindrop.

        Args:
            replacement: Values to replace while cloning.

        Returns:
            A copy of the raindrop with the edits made.

        Notes:
            This DOES NOT update the raw data, which should be considered
            stale and unsafe to use. If you wish to use the `raw` property
            after using this method you should update the server and pull
            back a fresh copy of the raindrop.
        """
        return replace(self, **replacements)

    def move_to(self, collection: int | SpecialCollection) -> Raindrop:
        """Move the raindrop to a different collection.

        Args:
            The collection to move the raindrop into.

        Returns:
            A copy of the raindrop with its collection changed.
        """
        moved = self.edit(collection=int(collection))
        moved.raw.get("collection", {})["$id"] = collection
        return moved

    @property
    def is_brand_new(self) -> bool:
        """Is this a brand new Raindrop that hasn't been saved yet?"""
        return self.identity == UNSAVED_IDENTITY

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
        search_text = search_text.casefold()
        return (
            search_text in self.title.casefold()
            or search_text in self.excerpt.casefold()
            or search_text in self.note.casefold()
            or search_text in self.link.casefold()
            or search_text in self.domain.casefold()
            or self.is_tagged(Tag(search_text))
        )

    TAG_STRING_SEPARATOR: Final[str] = ","
    """The separator for a string version of the tags."""

    TAG_STRING_SEPARATOR_TITLE: Final[str] = "comma"
    """The title of the separator for the string version of tags."""

    @classmethod
    def tags_to_string(cls, tags: Iterable[Tag]) -> str:
        """Convert a sequence of tags to a string.

        This method should be used when you wish to create a single string
        that can be edited in something like an `Input` field.

        Args:
            tags: The sequence of tags to convert.

        Returns:
            A comma-separated string of tags.

        Notes:
            The resulting string will ensure that duplicate tags are
            stripped and that the order is natural sort order.
        """
        return f"{cls.TAG_STRING_SEPARATOR} ".join(
            str(tag) for tag in sorted(set(tags))
        )

    @classmethod
    def string_to_raw_tags(cls, tags: str) -> list[Tag]:
        """Convert a string of tags into a list of tags.

        Args:
            tags: The tags in a string.

        Returns:
            A list of `Tag` objects.

        Notes:
            Unlike `string_to_tags` this method keeps the order of the tags
            in the string and also keeps any duplicates.
        """
        return [
            Tag(tag.strip())
            for tag in tags.split(cls.TAG_STRING_SEPARATOR)
            if tag.strip()
        ]

    @classmethod
    def string_to_tags(cls, tags: str) -> list[Tag]:
        """Convert a string of tags into a list of tags.

        This method should be used when you have a comma-separated string of
        tags and want to turn it into a list of `Tag` objects.

        Args:
            tags: The tags in a string.

        Returns:
            A list of `Tag` objects.

        Notes:
            This method guarantees that there will be no repeats of a tag,
            even if the input string has repeats.
        """
        return sorted(set(cls.string_to_raw_tags(tags)))


### raindrop.py ends here
