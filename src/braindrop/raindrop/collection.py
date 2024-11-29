"""Classes for holding collection information."""

##############################################################################
# Backward compatibility.
from __future__ import annotations

##############################################################################
# Python imports.
from dataclasses import dataclass
from datetime import datetime
from typing import Any

##############################################################################
# Local imports.
from .parse_time import get_time


##############################################################################
@dataclass
class Collection:
    """Class that holds the details of a collection."""

    identity: int
    """The ID of the collection."""
    # access
    # collaborators
    color: str
    """The colour for the collection."""
    count: int
    """The number of items in the collection."""
    cover: list[str]
    """Cover images for the collection."""
    created: datetime | None
    """When the collection was created."""
    expanded: bool
    """Is the collection expanded?"""
    last_update: datetime | None
    """When the collection was last updated."""
    public: bool
    """Is the collection visible to the public?"""
    sort: int
    """The sort value for the collection."""
    title: str
    """The title of the collection."""
    # user
    view: str
    """The view method for the collection."""
    parent: int | None
    """The ID of the parent collection, if there is one."""

    @staticmethod
    def from_json(data: dict[str, Any]) -> Collection:
        """Create a collection from JSON-sourced data.

        Returns:
            A fresh `Collection` instance.
        """
        return Collection(
            identity=data["_id"],
            color=data.get("color", ""),
            count=data["count"],
            cover=data["cover"],
            created=get_time(data, "created"),
            expanded=data["expanded"],
            last_update=get_time(data, "lastUpdate"),
            public=data["public"],
            sort=data["sort"],
            title=data["title"],
            view=data["view"],
            parent=data.get("parent", {}).get("$id"),
        )


### collection.py ends here
