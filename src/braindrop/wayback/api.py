"""Provides a function for checking an URL in the wayback machine."""

##############################################################################
# Python imports.
from json import loads
from typing import Final, NamedTuple

##############################################################################
# HTTPX imports.
import httpx

##############################################################################
# Local imports.
from ..raindrop import API


##############################################################################
class Availability(NamedTuple):
    """The availability data for a URL in the wayback machine."""

    available: bool
    """Is the URL available in the archive?"""

    url: str
    """The URL that was checked."""

    archive_url: str = ""
    """The URL that is available in the archive."""

    timestamp: str = ""
    """The timestamp of the archive entry."""

    status: str = ""
    """The status in the archive."""


##############################################################################
API_URL: Final[str] = "http://archive.org/wayback/available?url="
"""The URL of the API for getting availability."""


##############################################################################
class WaybackError(Exception):
    """Error raised when there is a problem connecting to the wayback machine."""


##############################################################################
async def availability(url: str) -> Availability:
    """Check if a URL is available in the wayback machine.

    Args:
        url: The URL to check.

    Returns:
        An `Availability` object.
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{API_URL}{url}",
                headers={"user-agent": API.AGENT},
            )
        except httpx.RequestError as error:
            raise WaybackError(str(error)) from error
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as error:
            raise WaybackError(str(error)) from error

        result = loads(response.text)
        if "archived_snapshots" in result and "closest" in result["archived_snapshots"]:
            return Availability(
                available=True,
                url=url,
                archive_url=result["archived_snapshots"]["closest"]["url"],
                timestamp=result["archived_snapshots"]["closest"]["timestamp"],
                status=result["archived_snapshots"]["closest"]["status"],
            )
        return Availability(available=False, url=url)


### api.py ends here
