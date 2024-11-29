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
class Toggle:
    """Holds the details of a value that can be toggled."""

    enabled: bool
    """Is the toggle enabled?"""

    @staticmethod
    def from_json(data: Any) -> Toggle:
        """Create a toggle from JSON-sourced data.

        Returns:
            A fresh `Group` instance.
        """
        return Toggle(enabled=data.get("enabled", False) if data else False)


##############################################################################
@dataclass
class User:
    """Class that holds the details of a Raindrop user."""

    identity: int
    """The user's ID."""
    # config
    dropbox: Toggle
    """Is the user configured to backup to Dropbox?"""
    gdrive: Toggle
    """Is the user configured to backup to GDrive?"""
    email: str
    """The user's email address."""
    email_md5: str
    """The MD5 hash of the user's email address."""
    # files
    full_name: str
    """The user's full name."""
    groups: list[Group]
    """The user's groups."""
    tfa: Toggle
    """Is the user configured to use TFA?."""
    apple: Toggle
    """Is the user configured to login with an Apple ID?"""
    password: bool
    """Is the user configured to login with a password?"""
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
            dropbox=Toggle.from_json(data.get("dropbox")),
            gdrive=Toggle.from_json(data.get("gdrive")),
            email=data["email"],
            email_md5=data.get("email_MD5", ""),
            full_name=data["fullName"],
            groups=[Group.from_json(group) for group in data["groups"]],
            tfa=Toggle.from_json(data.get("fta")),
            apple=Toggle.from_json(data.get("apple")),
            password=data["password"],
            pro=data["pro"],
            pro_expire=data.get("proExpire", ""),
            registered=data["registered"],
        )


### user.py ends here
