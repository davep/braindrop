"""Class that handles the local Raindrop data."""

##############################################################################
# Python imports.
from datetime import datetime
from json import dumps, loads
from pathlib import Path
from typing import Any, Callable, Final, Iterable, Iterator

##############################################################################
# pytz imports.
from pytz import UTC

##############################################################################
# Typing extension imports.
from typing_extensions import Self

##############################################################################
# Local imports.
from ...raindrop import (
    API,
    Collection,
    Group,
    Raindrop,
    SpecialCollection,
    User,
    get_time,
)
from .locations import data_dir
from .raindrops import Raindrops


##############################################################################
def local_data_file() -> Path:
    """The path to the file holds the local Raindrop data.

    Returns:
        The path to the local data file.
    """
    return data_dir() / "raindrops.json"


##############################################################################
class LocalData:
    """Holds and manages the local copy of the Raindrop data."""

    VERSION: Final[int] = 0
    """The version of the format of the local data."""

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
        self._trash: Raindrops = Raindrops(
            "Trash", root_collection=SpecialCollection.TRASH()
        )
        """All Raindrops in trash."""
        self._collections: dict[int, Collection] = {}
        """An index of all of the Raindrops we know about."""
        self._last_downloaded: datetime | None = None
        """The time the data was last downloaded from the server."""
        self._version: int | None = None
        """The version of the format of the data."""

    @property
    def last_downloaded(self) -> datetime | None:
        """The time the data was downloaded, or `None` if not yet."""
        return self._last_downloaded

    @property
    def outdated_format(self) -> bool:
        """Is the format of the local data outdated?"""
        return self._version is None or self._version < self.VERSION

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
            (raindrop for raindrop in self._all if raindrop.is_unsorted),
            root_collection=SpecialCollection.UNSORTED(),
        )

    @property
    def untagged(self) -> Raindrops:
        """A non-trashed untagged raindrops."""
        return Raindrops(
            "Untagged",
            (raindrop for raindrop in self._all if not raindrop.tags),
            root_collection=SpecialCollection.UNTAGGED(),
        )

    @property
    def broken(self) -> Raindrops:
        """All non-trashed broken raindrops."""
        return Raindrops(
            "Broken",
            (raindrop for raindrop in self._all if raindrop.broken),
            root_collection=SpecialCollection.BROKEN(),
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
            case SpecialCollection.ALL:
                return self.all
            case SpecialCollection.UNSORTED:
                return self.unsorted
            case SpecialCollection.UNTAGGED:
                return self.untagged
            case SpecialCollection.TRASH:
                return self.trash
            case SpecialCollection.BROKEN:
                return self.broken
            case user_collection:
                return Raindrops(
                    collection.title,
                    [
                        raindrop
                        for raindrop in self._all
                        if raindrop.collection == user_collection
                    ],
                    root_collection=collection,
                )

    def rebuild(self, raindrops: Raindrops) -> Raindrops:
        """Rebuild the given Raindrops from the current data.

        Args:
            raindrops: The `Raindrops` instance to rebuild.

        Returns:
            The `Raindrops` instance remade with the current data.
        """
        return raindrops.refilter(self.in_collection(raindrops.originally_from))

    def collection_size(self, collection: Collection) -> int:
        """Get the size of a given collection.

        Args:
            collection: The collection to get the count for.

        Returns:
            The count of raindrops in the collection.
        """
        # Favour the collection's own idea of its count, but if it doesn't
        # have one then do an actual count. The main reason for this is that
        # real collections have real counts, "special" ones don't (but we
        # can work it out).
        return collection.count or len(self.in_collection(collection))

    class UnknownCollection(Exception):
        """Exception raised if we encounter a collection ID we don't know about."""

    def collection(self, identity: int) -> Collection:
        """Get a collection from its ID.

        Args:
            identity: The identity of the collection.

        Returns:
            The collection with that identity.

        Raises:
            UnknownCollection: When a collection isn't known.
        """
        try:
            return (
                SpecialCollection(identity)()
                if identity in SpecialCollection
                else self._collections[identity]
            )
        except KeyError:
            raise self.UnknownCollection(
                f"Unknown collection identity: {identity}"
            ) from None

    @property
    def collections(self) -> list[Collection]:
        """A list of all known collections.

        Notes:
            This is just the list of user-defined collections.
        """
        return list(self._collections.values())

    def collections_within(self, group: Group) -> list[Collection]:
        """Find all the collections contained within a root.

        Args:
            group: The group to look within.

        Returns:
            The collections found within that group.

        Notes:
            The returned list is a flat list of *all* the collections within
            the group; no specific order is guaranteed.

            The Raindrop API has been known to apparently include IDs for
            collections, within a group, where the collection no longer
            exists. With this in mind any unknown collections are pruned.
        """

        def _collections(collection_ids: Iterable[int]) -> Iterator[Collection]:
            for collection in collection_ids:
                try:
                    yield self.collection(collection)
                    yield from _collections(
                        candidate.identity
                        for candidate in self.collections
                        if candidate.parent == collection
                    )
                except self.UnknownCollection:
                    pass

        return list(_collections(group.collections))

    def mark_downloaded(self) -> Self:
        """Mark the raindrops as having being downloaded at the time of calling."""
        self._last_downloaded = datetime.now(UTC)
        return self

    @staticmethod
    def _update_raindrop_count(
        status_update: Callable[[str], None], message: str
    ) -> Callable[[int], None]:
        """Create a raindrop download count update function.

        Args:
            status_update: The function that updates the status.
            message: The message to show against the count.

        Returns:
            A callable that can be passed to the API wrapper.
        """

        def _update(count: int) -> None:
            if count >= 0:
                status_update(f"{message} ({count})")
            else:
                # A negative count means that we're downloading things, but
                # we've paused for a moment at this point to let the
                # Raindrop.IO API have a breather.
                status_update(
                    f"{message} ({abs(count)})\n\nPaused - Waiting for Raindrop.IO"
                )

        return _update

    async def download(self, user: User, status_update: Callable[[str], None]) -> Self:
        """Download all available Raindrops from the server.

        Args:
            user: The user details we're downloading for.

        Returns:
            Self.
        """
        self._user = user
        self._all.set_to(
            await self._api.raindrops(
                SpecialCollection.ALL,
                self._update_raindrop_count(status_update, "Downloading all Raindrops"),
            )
        )
        self._trash.set_to(
            await self._api.raindrops(
                SpecialCollection.TRASH,
                self._update_raindrop_count(status_update, "Downloading trash"),
            )
        )
        status_update("Downloading all collections")
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
            "version": self.VERSION,
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
            self._version = data.get("version")
            if self.outdated_format:
                # The version is unknown, or older than we're expecting, so
                # let's pretend it doesn't exist.
                return self
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

    def add(self, raindrop: Raindrop) -> Self:
        """Add a raindrop to the local data.

        Args:
            raindrop: The raindrop to add.

        Notes:
            As a side effect the data is saved to storage.
        """
        # Add the raindrop to the start of the list of Raindrops.
        self._all.push(raindrop)
        return self.mark_downloaded().save()

    def update(self, raindrop: Raindrop) -> Self:
        """Update a raindrop in the local data.

        Args:
            raindrop: The raindrop to update.

        Notes:
            As a side-effect the data is saved to storage.
        """
        if raindrop in self._all and raindrop.collection == SpecialCollection.TRASH:
            # Looks like the raindrop is currently not in trash, but the
            # update puts it there; so trash it.
            return self.delete(raindrop)
        elif raindrop in self._trash and raindrop.collection != SpecialCollection.TRASH:
            # Looks like the raindrop is currently in trash, and the update
            # moves it out of there; so restore it.
            self._trash.remove(raindrop)
            self._all.push(raindrop)
        else:
            # Just a normal update.
            self._all.replace(raindrop)
        return self.mark_downloaded().save()

    def delete(self, raindrop: Raindrop) -> Self:
        """Delete a raindrop in the local data.

        Args:
            raindrop: The raindrop to delete.

        Notes:
            This method mimics out raindrop.io works when you remove a
            raindrop: if the raindrop isn't in trash, it is moved to trash;
            if it is in trash it is fully removed.

            As a side-effect the data is saved to storage.
        """
        if raindrop in self._all:
            self._trash.push(raindrop.move_to(SpecialCollection.TRASH))
            self._all.remove(raindrop)
        else:
            self._trash.remove(raindrop)
        return self.mark_downloaded().save()


### local.py ends here
