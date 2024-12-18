"""Defines a class for handling a tag."""

##############################################################################
# Backward compatibility.
from __future__ import annotations

##############################################################################
# Python imports.
from dataclasses import dataclass
from typing import Any


##############################################################################
@dataclass(frozen=True)
class Tag:
    """Holds details of a tag."""

    name: str
    """The name of the tag."""
    count: int
    """The number of Raindrops using this tag."""

    def __eq__(self, value: object, /) -> bool:
        if isinstance(value, Tag):
            return self == value.name
        if isinstance(value, str):
            return self.name.casefold() == value.casefold()
        raise NotImplemented

    @staticmethod
    def from_json(data: dict[str, Any]) -> Tag:
        """Create a tag from JSON-sourced data."""
        return Tag(
            name=data["_id"],
            count=data.get("count", 0),
        )


### tag.py ends here
