"""Class that holds all known Raindrops."""

##############################################################################
# Python imports.
from datetime import datetime
from json import dumps, loads
from pathlib import Path
from typing import Any, Self

##############################################################################
# pytz imports.
from pytz import UTC

##############################################################################
# Local imports.
from ...raindrop import API, Collection, Raindrop, User, get_time
from .locations import data_dir


##############################################################################
def raindrops_file() -> Path:
    """The path to the file that the local Raindrops are held in.

    Returns:
        The path to the Raindrops file.
    """
    return data_dir() / "raindrops.json"


##############################################################################
class Raindrops:
    """Holds and manages the local copy of all Raindrops."""

    def __init__(self, api: API) -> None:
        """Initialise the object.

        Args:
            api: The Raindrop API client object.
        """
        self._api = api
        """The API client object."""
        self._user: User | None = None
        """The details of the user who is the owner of the Raindrops."""
        self._all: list[Raindrop] = []
        """All non-trashed Raindrops."""
        self._trash: list[Raindrop] = []
        """All Raindrops in trash."""
        self._collections: dict[int, Collection] = {}
        """An index of all of the Raindrops we know about."""
        self._last_downloaded: datetime | None = None
        """The time the data was last downloaded from the server."""

    @property
    def last_downloaded(self) -> datetime | None:
        """The time the Raindrops were downloaded, or `None` if not yet."""
        return self._last_downloaded

    @property
    def user(self) -> User | None:
        """The user that the data relates to."""
        return self._user

    @property
    def all(self) -> list[Raindrop]:
        """All non-trashed raindrops."""
        return self._all

    @property
    def unsorted(self) -> list[Raindrop]:
        """All unsorted raindrops."""
        return [
            raindrop
            for raindrop in self._all
            if raindrop.collection == API.SpecialCollection.UNSORTED
        ]

    @property
    def trash(self) -> list[Raindrop]:
        """All trashed raindrops."""
        return self._trash

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
        self._all = await self._api.raindrops(API.SpecialCollection.ALL)
        self._trash = await self._api.raindrops(API.SpecialCollection.TRASH)
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
        raindrops_file().write_text(dumps(self._local_json, indent=4), encoding="utf-8")
        return self

    def load(self) -> Self:
        """Load the local copy of the Raindrop data.

        Returns:
            Self.
        """
        if raindrops_file().exists():
            data = loads(raindrops_file().read_text(encoding="utf-8"))
            self._last_downloaded = get_time(data, "last_downloaded")
            self._user = User.from_json(data.get("user", {}))
            self._all = [
                Raindrop.from_json(raindrop) for raindrop in data.get("all", [])
            ]
            self._trash = [
                Raindrop.from_json(raindrop) for raindrop in data.get("trash", [])
            ]
            self._collections = {
                int(k): Collection.from_json(v)
                for k, v in data.get("collections", {}).items()
            }
        return self


### raindrops.py ends here
