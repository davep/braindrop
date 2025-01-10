"""Provides a class for handling a collection of raindrops."""

##############################################################################
# Backward compatibility.
from __future__ import annotations

##############################################################################
# Python imports.
from typing import Counter, Iterable, Iterator, Sequence

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
class Raindrops:
    """Class that holds a group of Raindrops."""

    def __init__(
        self,
        title: str = "",
        raindrops: Iterable[Raindrop] | None = None,
        tags: Sequence[Tag] | None = None,
        search_text: tuple[str, ...] | None = None,
        source: Raindrops | None = None,
        root_collection: Collection | None = None,
    ) -> None:
        """Initialise the Raindrop grouping.

        Args:
            title: The title for the Raindrop grouping.
            raindrops: The raindrops to hold in the group.
            tags: Any tags associated with the given raindrops.
            search_text: Any search text associated with the given raindrops.
            source: The source data for the raindrops.
            root_collection: The root collection for the raindrops.
        """
        self._title = title
        """The title for the group of Raindrops."""
        self._raindrops = [] if raindrops is None else list(raindrops)
        """The raindrops."""
        self._index: dict[int, int] = {}
        """The index of IDs to locations in the list."""
        self._tags = () if tags is None else tags
        """The list of tags that resulted in this Raindrop group."""
        self._search_text = () if search_text is None else search_text
        """The search text related to this Raindrop group."""
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
        return bool(self._tags) or bool(self._search_text)

    @property
    def unfiltered(self) -> Raindrops:
        """The original source of the Raindrops, unfiltered."""
        return self._source

    @property
    def description(self) -> str:
        """The description of the content of the Raindrop grouping."""
        filters = []
        if search_text := [f'"{text}"' for text in self._search_text]:
            filters.append(f"contains {' and '.join(search_text)}")
        if self._tags:
            filters.append(f"tagged {', '.join(str(tag) for tag in self._tags)}")
        return f"{'; '.join((self._title, *filters))} ({len(self)})"

    @property
    def tags(self) -> list[TagData]:
        """The list of unique tags found amongst the Raindrops."""
        tags: list[Tag] = []
        for raindrop in self:
            tags.extend(set(raindrop.tags))
        return [TagData(name, count) for name, count in Counter(tags).items()]

    def tagged(self, *tags: Tag) -> Raindrops:
        """Get the raindrops with the given tags.

        Args:
            tags: The tags to look for.

        Returns:
            The subset of Raindrops that have the given tags.
        """
        return Raindrops(
            self.title,
            (raindrop for raindrop in self if raindrop.is_tagged(*tags)),
            tuple(set((*self._tags, *tags))),
            self._search_text,
            self._source,
            self._root_collection,
        )

    def containing(self, search_text: str) -> Raindrops:
        """Get the raindrops containing the given text.

        Args:
            search_text: The text to search for.

        Returns:
            The subset of Raindrops that contain the given text.
        """
        return Raindrops(
            self.title,
            (raindrop for raindrop in self if search_text in raindrop),
            self._tags,
            (*self._search_text, search_text),
            self._source,
            self._root_collection,
        )

    def refilter(self, raindrops: Raindrops | None = None) -> Raindrops:
        """Reapply any filtering.

        Args:
            raindrops: An optional list of raindrops to apply to.

        Returns:
            The given raindrops with this object's filters applied.
        """
        raindrops = (self if raindrops is None else raindrops).unfiltered.tagged(
            *self._tags
        )
        for search_text in self._search_text:
            raindrops = raindrops.containing(search_text)
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
