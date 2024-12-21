"""Class that handles the local Raindrop data."""

##############################################################################
# Backward compatibility.
from __future__ import annotations

##############################################################################
# Python imports.
from datetime import datetime
from json import dumps, loads
from pathlib import Path
from typing import Any, Counter, Iterable, Iterator, Self

##############################################################################
# pytz imports.
from pytz import UTC

##############################################################################
# Local imports.
from ...raindrop import API, Collection, Raindrop, Tag, TagData, User, get_time
from .locations import data_dir


##############################################################################
def local_data_file() -> Path:
    """The path to the file holds the local Raindrop data.

    Returns:
        The path to the local data file.
    """
    return data_dir() / "raindrops.json"


##############################################################################
class Raindrops:
    """Class that holds a group of Raindrops."""

    def __init__(
        self, title: str = "", raindrops: Iterable[Raindrop] | None = None
    ) -> None:
        """Initialise the Raindrop grouping.

        Args:
            title: The title for the Raindrop grouping.
            raindrops: The raindrops to hold in the group.
        """
        self.title = title
        """The title for the group of Raindrops."""
        self._raindrops = [] if raindrops is None else list(raindrops)
        """The raindrops."""

    def set_to(self, raindrops: Iterable[Raindrop]) -> Self:
        """Set the group to the given group of Raindrops.

        Args:
            raindrops: The raindrops to set the group to.

        Returns:
            Self.
        """
        self._raindrops = list(raindrops)
        return self

    def __iter__(self) -> Iterator[Raindrop]:
        return iter(self._raindrops)


##############################################################################
class LocalData:
    """Holds and manages the local copy of the Raindrop data."""

    def __init__(self, api: API) -> None:
        """Initialise the object.

        Args:
            api: The Raindrop API client object.
        """
        self._api = api
        """The API client object."""
        self._user: User | None = None
        """The details of the user who is the owner of the Raindrops."""
        self._all: Raindrops = Raindrops("All")
        """All non-trashed Raindrops."""
        self._trash: Raindrops = Raindrops("Trash")
        """All Raindrops in trash."""
        self._collections: dict[int, Collection] = {}
        """An index of all of the Raindrops we know about."""
        self._last_downloaded: datetime | None = None
        """The time the data was last downloaded from the server."""

    @property
    def last_downloaded(self) -> datetime | None:
        """The time the data was downloaded, or `None` if not yet."""
        return self._last_downloaded

    @property
    def user(self) -> User | None:
        """The user that the data relates to."""
        return self._user

    @property
    def all(self) -> Raindrops:
        """All non-trashed raindrops."""
        return self._all

    @property
    def unsorted(self) -> Raindrops:
        """All unsorted raindrops."""
        return Raindrops(
            "Unsorted",
            (
                raindrop
                for raindrop in self._all
                if raindrop.collection == API.SpecialCollection.UNSORTED
            ),
        )

    @property
    def trash(self) -> Raindrops:
        """All trashed raindrops."""
        return self._trash

    def in_collection(self, collection: Collection) -> Raindrops:
        """Get all Raindrops within a given collection.

        Args:
            collection: The collection to get the Raindrops for.

        Returns:
            The raindrops within that collection.
        """
        match collection.identity:
            case API.SpecialCollection.ALL:
                return self.all
            case API.SpecialCollection.UNSORTED:
                return self.unsorted
            case API.SpecialCollection.TRASH:
                return self.trash
            case user_collection:
                return Raindrops(
                    collection.title,
                    [
                        raindrop
                        for raindrop in self._all
                        if raindrop.collection == user_collection
                    ],
                )

    def tagged(self, *tags: Tag, within: Raindrops | None = None) -> Raindrops:
        """Get all Raindrops that have a given tag.

        Args:
            tags: The tags to look for.
            within: Optional list of raindrops to look within. If not
                supplied then all will be looked at.

        Returns:
            The list of raindrops that are tagged with the given tags.
        """
        if within is None:
            within = self._all
        return Raindrops(
            within.title,
            [
                raindrop
                for raindrop in (self._all if within is None else within)
                if set(tags) <= set(raindrop.tags)
            ],
        )

    def tags_of(self, collection: Collection | Raindrops) -> list[TagData]:
        """Get the tags of a collection.

        Args:
            collection: The collection to get the tags of.

        Returns:
            A list of the tags found in the collection.
        """
        if isinstance(collection, (int, Collection)):
            return self.tags_of(self.in_collection(collection))
        tags: list[Tag] = []
        for raindrop in collection:
            tags.extend(set(raindrop.tags))
        return [TagData(name, count) for name, count in Counter(tags).items()]

    def collection(self, identity: int) -> Collection:
        """Get a collection from its ID.

        Args:
            identity: The identity of the collection.

        Returns:
            The collection with that identity.
        """
        return self._collections[identity]

    @property
    def collections(self) -> list[Collection]:
        """A list of all known collections."""
        return list(self._collections.values())

    def mark_downloaded(self) -> Self:
        """Mark the bookmarks as having being downloaded at the time of calling."""
        self._last_downloaded = datetime.now(UTC)
        return self

    async def download(self, user: User) -> Self:
        """Download all available Raindrops from the server.

        Args:
            user: The user details we're downloading for.

        Returns:
            Self.
        """
        self._user = user
        self._all.set_to(await self._api.raindrops(API.SpecialCollection.ALL))
        self._trash.set_to(await self._api.raindrops(API.SpecialCollection.TRASH))
        self._collections = {
            collection.identity: collection
            for collection in await self._api.collections("all")
        }
        return self.mark_downloaded()

    @property
    def _local_json(self) -> dict[str, Any]:
        """All the Raindrops in a JSON-friendly format."""
        return {
            "last_downloaded": None
            if self._last_downloaded is None
            else self._last_downloaded.isoformat(),
            "user": None if self._user is None else self._user.raw,
            "all": [raindrop.raw for raindrop in self._all],
            "trash": [raindrop.raw for raindrop in self._trash],
            "collections": {k: v.raw for k, v in self._collections.items()},
        }

    def save(self) -> Self:
        """Save a local copy of the Raindrop data.

        Returns:
            Self.
        """
        local_data_file().write_text(
            dumps(self._local_json, indent=4), encoding="utf-8"
        )
        return self

    def load(self) -> Self:
        """Load the local copy of the Raindrop data.

        Returns:
            Self.
        """
        if local_data_file().exists():
            data = loads(local_data_file().read_text(encoding="utf-8"))
            self._last_downloaded = get_time(data, "last_downloaded")
            self._user = User.from_json(data.get("user", {}))
            self._all.set_to(
                Raindrop.from_json(raindrop) for raindrop in data.get("all", [])
            )
            self._trash.set_to(
                Raindrop.from_json(raindrop) for raindrop in data.get("trash", [])
            )
            self._collections = {
                int(k): Collection.from_json(v)
                for k, v in data.get("collections", {}).items()
            }
        return self


### local.py ends here