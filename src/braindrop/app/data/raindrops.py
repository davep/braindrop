"""Provides a class for handling a collection of raindrops."""

##############################################################################
# Backward compatibility.
from __future__ import annotations

##############################################################################
# Python imports.
from typing import Counter, Iterable, Iterator

##############################################################################
# Typing extension imports.
from typing_extensions import Self

##############################################################################
# Local imports.
from ...raindrop import (
    Collection,
    Raindrop,
    SpecialCollection,
    Tag,
    TagData,
)


##############################################################################
class Filter:
    """Base class for the raindrop filters."""

    def __eq__(self, raindrop: object) -> bool:
        del raindrop
        return False


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

        def __eq__(self, raindrop: object) -> bool:
            if isinstance(raindrop, Raindrop):
                return raindrop.is_tagged(self._tag)
            raise NotImplementedError

        def __str__(self) -> str:
            return str(self._tag)

    class Containing(Filter):
        """Filter class to check if a raindrop contains some specific text."""

        def __init__(self, text: str) -> None:
            """Initialise the object.

            Args:
                text: The text to filter for.
            """
            self._text = text
            """The text to look for."""

        def __eq__(self, raindrop: object) -> bool:
            if isinstance(raindrop, Raindrop):
                return self._text in raindrop
            raise NotImplementedError

        def __str__(self) -> str:
            return self._text

    def __init__(
        self,
        title: str = "",
        raindrops: Iterable[Raindrop] | None = None,
        filters: tuple[Filter, ...] | None = None,
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
        if search_text := [
            f'"{text}"' for text in self._filters if isinstance(text, self.Containing)
        ]:
            filters.append(f"contains {' and '.join(search_text)}")
        if tags := [str(tag) for tag in self._filters if isinstance(tag, self.Tagged)]:
            filters.append(f"tagged {', '.join(tags)}")
        return f"{'; '.join((self._title, *filters))} ({len(self)})"

    @property
    def tags(self) -> list[TagData]:
        """The list of unique tags found amongst the Raindrops."""
        tags: list[Tag] = []
        for raindrop in self:
            tags.extend(set(raindrop.tags))
        return [TagData(name, count) for name, count in Counter(tags).items()]

    def filter(self, new_filter: Filter) -> Raindrops:
        """Get the raindrops that match a given filter.

        Args:
            new_filter: The new filter to apply.

        Returns:
            The subset of Raindrops that match the given filter.
        """
        return Raindrops(
            self.title,
            (raindrop for raindrop in self if raindrop == new_filter),
            (*self._filters, new_filter),
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
        return self.filter(self.Tagged(tag))

    def containing(self, search_text: str) -> Raindrops:
        """Get the raindrops containing the given text.

        Args:
            search_text: The text to search for.

        Returns:
            The subset of Raindrops that contain the given text.
        """
        return self.filter(self.Containing(search_text))

    def refilter(self, raindrops: Raindrops | None = None) -> Raindrops:
        """Reapply any filtering.

        Args:
            raindrops: An optional list of raindrops to apply to.

        Returns:
            The given raindrops with this object's filters applied.
        """
        raindrops = (self if raindrops is None else raindrops).unfiltered
        for next_filter in self._filters:
            raindrops = raindrops.filter(next_filter)
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
