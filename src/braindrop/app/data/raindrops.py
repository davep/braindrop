"""Provides a class for handling a collection of raindrops."""

##############################################################################
# Backward compatibility.
from __future__ import annotations

##############################################################################
# Python imports.
from dataclasses import dataclass
from functools import total_ordering
from typing import Callable, Counter, Iterable, Iterator, TypeAlias

##############################################################################
# Typing extension imports.
from typing_extensions import Self

##############################################################################
# Local imports.
from ...raindrop import (
    Collection,
    Raindrop,
    RaindropType,
    SpecialCollection,
    Tag,
)


##############################################################################
@dataclass(frozen=True)
class TagCount:
    """Holds count details of a tag."""

    tag: Tag
    """The name of the tag."""
    count: int
    """The number of Raindrops using this tag."""

    @staticmethod
    def the_tag() -> Callable[[TagCount], Tag]:
        """Returns a function for getting the tag from a `TagCount` instance.

        Returns:
            A function to get the tag of a `TagCount` instance.
        """

        def _getter(data: TagCount) -> Tag:
            return data.tag

        return _getter

    @staticmethod
    def the_count() -> Callable[[TagCount], int]:
        """Returns a function for getting the count from a `TagCount` instance.

        Returns:
            A function to get the count of a `TagCount` instance.
        """

        def _getter(data: TagCount) -> int:
            return data.count

        return _getter


##############################################################################
@dataclass(frozen=True)
@total_ordering
class TypeCount:
    """Holds the count details of a raindrop type."""

    type: RaindropType
    """The type."""
    count: int
    """The count of raindrops of that type."""

    def __gt__(self, value: object, /) -> bool:
        if isinstance(value, TypeCount):
            return self.type > value.type
        raise NotImplementedError

    def __eq__(self, value: object, /) -> bool:
        if isinstance(value, TypeCount):
            return self.type == value.type
        raise NotImplementedError


##############################################################################
Filters: TypeAlias = tuple["Filter", ...]
"""The type of a collection of filters."""


##############################################################################
class Filter:
    """Base class for the raindrop filters."""

    def __rand__(self, _: Raindrop) -> bool:
        return False

    def __radd__(self, filters: Filters) -> Filters:
        return (*filters, self)

    def __eq__(self, value: object) -> bool:
        if isinstance(value, Filter):
            return False
        raise NotImplementedError


##############################################################################
class Raindrops:
    """Class that holds a group of Raindrops."""

    class Tagged(Filter):
        """Filter class to check if a raindrop has a particular tag."""

        def __init__(self, tag: Tag | str) -> None:
            """Initialise the object.

            Args:
                tag: The tag to filter on.
            """
            self._tag = Tag(tag)
            """The tag to filter on."""

        def __rand__(self, raindrop: Raindrop) -> bool:
            return raindrop.is_tagged(self._tag)

        def __str__(self) -> str:
            return str(self._tag)

        def __eq__(self, value: object) -> bool:
            if isinstance(value, Raindrops.Tagged):
                return str(value) == self._tag
            return super().__eq__(value)

    class IsOfType(Filter):
        """Filter class to check if a raindrop is of a given type."""

        def __init__(self, raindrop_type: RaindropType) -> None:
            """Initialise the object.

            Args:
                raindrop_type: The raindrop type to filter on.
            """
            self._type = raindrop_type
            """The type of raindrop to filter for."""

        def __rand__(self, raindrop: Raindrop) -> bool:
            return raindrop.type == self._type

        def __str__(self) -> str:
            return str(self._type)

        def __eq__(self, value: object) -> bool:
            if isinstance(value, Raindrops.IsOfType):
                return str(value) == self._type
            return super().__eq__(value)

    class Containing(Filter):
        """Filter class to check if a raindrop contains some specific text."""

        def __init__(self, text: str) -> None:
            """Initialise the object.

            Args:
                text: The text to filter for.
            """
            self._text = text
            """The text to look for."""

        def __rand__(self, raindrop: Raindrop) -> bool:
            return self._text in raindrop

        def __str__(self) -> str:
            return self._text

        def __eq__(self, value: object) -> bool:
            if isinstance(value, Raindrops.Containing):
                return str(value).casefold() == self._text.casefold()
            return super().__eq__(value)

    def __init__(
        self,
        title: str = "",
        raindrops: Iterable[Raindrop] | None = None,
        filters: Filters | None = None,
        source: Raindrops | None = None,
        root_collection: Collection | None = None,
    ) -> None:
        """Initialise the Raindrop grouping.

        Args:
            title: The title for the Raindrop grouping.
            raindrops: The raindrops to hold in the group.
            filters: The filters that got to this set of raindrops.
            source: The source data for the raindrops.
            root_collection: The root collection for the raindrops.
        """
        self._title = title
        """The title for the group of Raindrops."""
        self._raindrops = [] if raindrops is None else list(raindrops)
        """The raindrops."""
        self._index: dict[int, int] = {}
        """The index of IDs to locations in the list."""
        self._filters = () if filters is None else filters
        """The filters that got to this set of raindrops."""
        self._source = source or self
        """The original source for the Raindrops."""
        self._root_collection = (
            SpecialCollection.ALL() if root_collection is None else root_collection
        )
        """The collection that was the root."""
        self._reindex()

    def _reindex(self) -> Self:
        """Reindex the raindrops.

        Returns:
            Self.
        """
        self._index = {
            raindrop.identity: location
            for location, raindrop in enumerate(self._raindrops)
        }
        return self

    def set_to(self, raindrops: Iterable[Raindrop]) -> Self:
        """Set the group to the given group of Raindrops.

        Args:
            raindrops: The raindrops to set the group to.

        Returns:
            Self.
        """
        self._raindrops = list(raindrops)
        return self._reindex()

    @property
    def originally_from(self) -> Collection:
        """The collection these raindrops originally came from."""
        return self._root_collection

    def push(self, raindrop: Raindrop) -> Self:
        """Push a new Raindrop into the contained raindrops.

        Args:
            raindrop: The Raindrop to push.

        Returns:
            Self.
        """
        self._raindrops.insert(0, raindrop)
        return self._reindex()

    def replace(self, raindrop: Raindrop) -> Self:
        """Replace a raindrop with a new version.

        Args:
            raindrop: The raindrop to replace.

        Returns:
            Self.
        """
        self._raindrops[self._index[raindrop.identity]] = raindrop
        return self

    def remove(self, raindrop: Raindrop) -> Self:
        """Remove a raindrop.

        Args:
            raindrop: The raindrop to remove.

        Returns:
            Self.
        """
        del self._raindrops[self._index[raindrop.identity]]
        return self._reindex()

    @property
    def title(self) -> str:
        """The title of the group."""
        return self._title

    @property
    def is_filtered(self) -> bool:
        """Are the Raindrops filtered in some way?"""
        return bool(self._filters)

    @property
    def unfiltered(self) -> Raindrops:
        """The original source of the Raindrops, unfiltered."""
        return self._source

    @property
    def description(self) -> str:
        """The description of the content of the Raindrop grouping."""
        filters = []
        if raindrop_types := [
            f"{raindrop_type}"
            for raindrop_type in self._filters
            if isinstance(raindrop_type, self.IsOfType)
        ]:
            filters.append(f"type {' and '.join(raindrop_types)}")
        if search_text := [
            f'"{text}"' for text in self._filters if isinstance(text, self.Containing)
        ]:
            filters.append(f"contains {' and '.join(search_text)}")
        if tags := [str(tag) for tag in self._filters if isinstance(tag, self.Tagged)]:
            filters.append(f"tagged {', '.join(tags)}")
        return f"{'; '.join((self._title, *filters))} ({len(self)})"

    @property
    def tags(self) -> list[TagCount]:
        """The list of unique tags found amongst the Raindrops."""
        tags: list[Tag] = []
        for raindrop in self:
            tags.extend(set(raindrop.tags))
        return [TagCount(name, count) for name, count in Counter(tags).items()]

    @property
    def types(self) -> list[TypeCount]:
        """The list of types found amongst the Raindrops."""
        return [
            TypeCount(name, count)
            for name, count in Counter[RaindropType](
                raindrop.type for raindrop in self
            ).items()
        ]

    def __and__(self, new_filter: Filter) -> Raindrops:
        """Get the raindrops that match a given filter.

        Args:
            new_filter: The new filter to apply.

        Returns:
            The subset of Raindrops that match the given filter.
        """
        # Don't bother applying a filter we already know about.
        if new_filter in self._filters:
            return self
        # Novel filter, apply it.
        return Raindrops(
            self.title,
            (raindrop for raindrop in self if raindrop & new_filter),
            self._filters + new_filter,
            self._source,
            self._root_collection,
        )

    def tagged(self, tag: Tag | str) -> Raindrops:
        """Get the raindrops with the given tags.

        Args:
            tag: The tag to look for.

        Returns:
            The subset of Raindrops that have the given tag.
        """
        return self & self.Tagged(tag)

    def of_type(self, raindrop_type: RaindropType) -> Raindrops:
        """Get the raindrops of a given type.

        Args:
            raindrop_type: The type to look for.

        Returns:
            The subset of Raindrops that are of the type.
        """
        return self & self.IsOfType(raindrop_type)

    def containing(self, search_text: str) -> Raindrops:
        """Get the raindrops containing the given text.

        Args:
            search_text: The text to search for.

        Returns:
            The subset of Raindrops that contain the given text.
        """
        return self & self.Containing(search_text)

    def refilter(self, raindrops: Raindrops | None = None) -> Raindrops:
        """Reapply any filtering.

        Args:
            raindrops: An optional list of raindrops to apply to.

        Returns:
            The given raindrops with this object's filters applied.
        """
        raindrops = (self if raindrops is None else raindrops).unfiltered
        for next_filter in self._filters:
            raindrops = raindrops & next_filter
        return raindrops

    def __contains__(self, raindrop: Raindrop) -> bool:
        """Is the given raindrop in here?"""
        return raindrop.identity in self._index

    def __iter__(self) -> Iterator[Raindrop]:
        """The object as an iterator."""
        return iter(self._raindrops)

    def __len__(self) -> int:
        """The count of raindrops in the object."""
        return len(self._raindrops)


### raindrops.py ends here
