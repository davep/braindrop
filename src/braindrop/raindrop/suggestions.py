"""Provides a class for holding raindrop suggestions."""

##############################################################################
# Backward compatibility.
from __future__ import annotations

##############################################################################
# Python imports.
from dataclasses import dataclass
from typing import Any

##############################################################################
# Local imports.
from .tag import Tag


##############################################################################
@dataclass(frozen=True)
class Suggestions:
    """Class that holds suggestions for a Raindrop."""

    raw: dict[str, Any]
    """The raw data."""
    collections: list[int]
    """A list of suggested collection IDs."""
    tags: list[Tag]
    """A list of suggested tags."""

    @staticmethod
    def from_json(data: dict[str, Any]) -> Suggestions:
        """Create a Suggestions object from JSON-sourced data.

        Args:
            data: The data to create the object from.

        Returns:
            A fresh `Suggestions` instance.
        """
        return Suggestions(
            raw=data,
            collections=[
                collection.get("$id", None)
                for collection in data.get("collections", [])
                if collection.get("$id", None) is not None
            ],
            tags=[Tag(tag) for tag in data.get("tags", []) if tag],
        )


### suggestions.py ends here
