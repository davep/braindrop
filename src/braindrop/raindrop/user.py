"""Class for holding user information."""

##############################################################################
# Backward compatibility.
from __future__ import annotations

##############################################################################
# Python imports.
from dataclasses import dataclass
from typing import Any


##############################################################################
@dataclass
class Group:
    """The class that holds details of a user's group."""

    title: str
    """The title of the group."""
    hidden: bool
    """Is the group hidden?"""
    sort: int
    """The sort position for the group."""
    collections: list[int]
    """The list of collection IDs for collections within this group."""

    @staticmethod
    def from_json(data: dict[str, Any]) -> Group:
        """Create a group from JSON-sourced data.

        Returns:
            A fresh `Group` instance.
        """
        return Group(
            title=data["title"],
            hidden=data["hidden"],
            sort=data["sort"],
            collections=data["collections"],
        )


##############################################################################
@dataclass
class User:
    """Class that holds the details of a Raindrop user."""

    identity: int
    """The user's ID."""
    # config
    # dropbox
    email: str
    """The user's email address."""
    email_md5: str
    """The MD5 hash of the user's email address."""
    # files
    full_name: str
    """The user's full name."""
    # gdrive
    groups: list[Group]
    """The user's groups."""
    password: bool
    """Password flag (docs don't seem to say what it's for)."""
    pro: bool
    """Is the user a pro user?"""
    pro_expire: str  # TODO make datetime
    """When the current pro subscription expires."""
    registered: str  # TODO make datetime
    """When the user first registered their account."""

    @staticmethod
    def from_json(data: dict[str, Any]) -> User:
        """Create a user from JSON-sourced data.

        Returns:
            A fresh `User` instance.
        """
        return User(
            identity=data["_id"],
            email=data["email"],
            email_md5=data.get("email_MD5", ""),
            full_name=data["fullName"],
            groups=[Group.from_json(group) for group in data["groups"]],
            password=data["password"],
            pro=data["pro"],
            pro_expire=data.get("proExpire", ""),
            registered=data["registered"],
        )


### user.py ends here
