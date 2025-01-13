"""Defines a class for handling a tag."""

##############################################################################
# Backward compatibility.
from __future__ import annotations

##############################################################################
# Python imports.
from functools import total_ordering


##############################################################################
@total_ordering
class Tag:
    """A class for holding a tag."""

    def __init__(self, tag: str | Tag) -> None:
        """Initialise the object.

        Args:
            tag: The tag to hold.
        """
        self._tag = str(tag)

    def startswith(self, other: str | Tag) -> bool:
        """Does this tag start with the other tag?

        Args:
            other: The other tag to test against.

        Returns:
            `True` if this tag starts with the other, `False` if not.
        """
        return Tag(str(self)[: len(other)]) == Tag(other)

    def __repr__(self) -> str:
        """The representation of the tag."""
        return self._tag

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
            return self._tag.casefold() > value.casefold()
        raise NotImplementedError

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
            return self._tag.casefold() == value.casefold()
        raise NotImplementedError

    def __hash__(self) -> int:
        """Ensure that Tag objects hash case-insensitive.

        Returns:
            The hash.
        """
        return hash(self._tag.casefold())

    def __len__(self) -> int:
        """The length of the tag."""
        return len(self._tag)


### tag.py ends here
