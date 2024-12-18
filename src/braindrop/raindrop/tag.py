"""Defines a class for handling a tag."""

##############################################################################
# Backward compatibility.
from __future__ import annotations

##############################################################################
# Python imports.
from dataclasses import dataclass
from functools import total_ordering
from typing import Any


##############################################################################
@total_ordering
class Tag:
    """A class for holding a tag."""

    def __init__(self, tag: str) -> None:
        """Initialise the object.

        Args:
            tag: The tag to hold.
        """
        self.__tag = tag

    def __repr__(self) -> str:
        """The representation of the tag."""
        return self.__tag

    def __gt__(self, value: object, /) -> bool:
        """Is the tag greater than another value?

        Args:
            value: The value to compare against.

        Returns:
            `True` if the tag is the same, `False` if not.

        Raises:
            NotImplemented: If compared against anything that isn't a `str`
                or a `Tag`.
        """
        if isinstance(value, Tag):
            return self > str(value)
        if isinstance(value, str):
            return self.__tag.casefold() > value.casefold()
        raise NotImplemented

    def __eq__(self, value: object, /) -> bool:
        """Is the tag equal to another value.

        Args:
            value: The value to compare against.

        Returns:
            `True` if the tag is the same, `False` if not.

        Raises:
            NotImplemented: If compared against anything that isn't a `str`
                or a `Tag`.
        """
        if isinstance(value, Tag):
            return self == str(value)
        if isinstance(value, str):
            return self.__tag.casefold() == value.casefold()
        raise NotImplemented

    def __hash__(self) -> int:
        """Ensure that Tag objects hash case-insensitive.

        Returns:
            The hash.
        """
        return hash(self.__tag.casefold())


##############################################################################
@dataclass(frozen=True)
class TagData:
    """Holds details of a tag."""

    tag: Tag
    """The name of the tag."""
    count: int
    """The number of Raindrops using this tag."""

    @staticmethod
    def from_json(data: dict[str, Any]) -> TagData:
        """Create a tag from JSON-sourced data."""
        return TagData(
            tag=Tag(data["_id"]),
            count=data.get("count", 0),
        )


### tag.py ends here
