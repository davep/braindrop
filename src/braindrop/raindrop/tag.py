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

    @staticmethod
    def from_json(data: dict[str, Any]) -> Tag:
        """Create a tag from JSON-sourced data."""
        return Tag(
            name=data["_id"],
            count=data.get("count", 0),
        )


### tag.py ends here
