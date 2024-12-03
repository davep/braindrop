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
from ...raindrop import API, Raindrop
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
        """Initialise the object."""
        self._api = api
        """The API client object."""
        self._all: list[Raindrop] = []
        """All non-trashed Raindrops."""
        self._trash: list[Raindrop] = []
        """All Raindrops in trash."""
        self._last_downloaded: datetime | None = None

    @property
    def last_downloaded(self) -> datetime | None:
        """The time the Raindrops were downloaded, or `None` if not yet."""
        return self._last_downloaded

    def mark_downloaded(self) -> Self:
        """Mark the bookmarks as having being downloaded at the time of calling."""
        self._last_downloaded = datetime.now(UTC)
        return self

    async def download(self) -> Self:
        """Download all available Raindrops from the server.

        Args:
            api: The API to download via.

        Returns:
            Self.
        """
        self._all = await self._api.raindrops()
        self._trash = await self._api.raindrops(API.SpecialCollection.ALL)
        return self.mark_downloaded()

    @property
    def _local_json(self) -> dict[str, Any]:
        """All the Raindrops in a JSON-friendly format."""
        return {
            "last_downloaded": None
            if self._last_downloaded is None
            else self._last_downloaded.isoformat(),
            "all": [raindrop.raw for raindrop in self._all],
            "trash": [raindrop.raw for raindrop in self._trash],
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
            self._last_downloaded = data["last_downloaded"]
            self._all = data["all"]
            self._trash = data["trash"]
        return self


### raindrops.py ends here
