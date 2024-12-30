"""Provides a simple raindrop.io client."""

##############################################################################
# Python imports.
from enum import IntEnum
from json import loads
from ssl import SSLCertVerificationError
from typing import Any, Callable, Final, Literal

##############################################################################
# HTTPX imports.
from httpx import AsyncClient, HTTPStatusError, RequestError

##############################################################################
# Local imports.
from ..raindrop.user import User
from .collection import Collection, SpecialCollection
from .raindrop import Raindrop
from .tag import TagData


##############################################################################
class API:
    """API client class for raindrop.io."""

    AGENT: Final[str] = "Braindrop (https://github.com/davep/braindrop)"
    """The agent string to use when talking to the API."""

    _BASE: Final[str] = "https://api.raindrop.io/rest/v1/"
    """The base of the URL for the API."""

    class Error(Exception):
        """Base class for Raindrop errors."""

    class RequestError(Error):
        """Exception raised if there was a problem making an API request."""

    def __init__(self, access_token: str) -> None:
        """Initialise the client object.

        Args:
            access_token: The access token for the Raindrop API.
        """
        self._token = access_token
        """The API access token."""
        self._client_: AsyncClient | None = None
        """The internal reference to the HTTPX client."""

    @property
    def _client(self) -> AsyncClient:
        """The HTTPX client."""
        if self._client_ is None:
            self._client_ = AsyncClient()
        return self._client_

    def _api_url(self, *path: str) -> str:
        """Construct a URL for calling on the API.

        Args:
            *path: The path to the endpoint.

        Returns:
            The URL to use.
        """
        return f"{self._BASE}{'/'.join(path)}"

    async def _call(self, *path: str, **params: str) -> str:
        """Call on the Raindrop API.

        Args:
            path: The path for the API call.
            params: The parameters for the call.

        Returns:
            The text returned from the call.
        """
        try:
            response = await self._client.get(
                self._api_url(*path),
                params=params,
                headers={
                    "user-agent": self.AGENT,
                    "Authorization": f"Bearer {self._token}",
                },
            )
        except (RequestError, SSLCertVerificationError) as error:
            raise self.RequestError(str(error))

        try:
            response.raise_for_status()
        except HTTPStatusError as error:
            raise self.RequestError(str(error))

        return response.text

    async def _result_of(
        self, value: str, *path: str, **params: str
    ) -> tuple[bool, Any]:
        """Get the result of a call to the Raindrop API.

        Args:
            value: The name of the value to pull from the result.
            path: The path for the API call.
            params: The parameters for the call.

        Returns:
            A tuple of a bool that is the result plus any data from the call.
        """
        result = loads(await self._call(*path, **params))
        return (
            (result["result"], result[value])
            if value in result
            else (result[value], None)
        )

    async def _items_of(
        self, *path: str, **params: str
    ) -> tuple[bool, list[Any] | None]:
        """Get the items of a call to the Raindrop API.

        Args:
            path: The path for the API call.
            params: The parameters for the call.

        Returns:
            A tuple of a bool that is the result plus any items from the call.
        """
        return await self._result_of("items", *path, **params)

    async def collections(
        self, level: Literal["root", "children", "all"] = "all"
    ) -> list[Collection]:
        """Get collections from Raindrop.

        Args:
            level: Either `root`, `children` or `all`.

        Returns:
            The collections.
        """
        if level == "all":
            return await self.collections("root") + await self.collections("children")
        _, collections = await self._items_of(
            f"collections{'' if level == 'root' else '/childrens'}"
        )
        return [Collection.from_json(collection) for collection in collections or []]

    async def user(self) -> User | None:
        """Get the user details.

        Returns:
            The details of the current user, or `None` if the details could
            not be fetched.
        """
        result, user = await self._result_of("user", "user")
        return User.from_json(user) if result and user is not None else None

    async def raindrops(
        self,
        collection: int = SpecialCollection.ALL,
        count_update: Callable[[int], None] | None = None,
    ) -> list[Raindrop]:
        """Get a list of Raindrops.

        Args:
            collection: The collection to get the Raindrops from. Defaults
                to all Raindrops.
            count_update: Optional callable that takes a count of the
                download progress.

        Returns:
            A list of Raindrops.

        Note:
            The following constants are available for specific special collections:

            - `SpecialCollection.ALL` - All non-trashed `Raindrop`s.
            - `SpecialCollection.UNSORTED` - All `Raindrop`s not in a `Collection`.
            - `SpecialCollection.TRASH` - All trashed `Raindrop`s.
        """
        assert collection not in (
            SpecialCollection.UNTAGGED,
            SpecialCollection.BROKEN,
        ), f"{collection} is not a valid collection ID"
        page = 0
        raindrops: list[Raindrop] = []
        if count_update is not None:
            count_update(0)
        while True:
            _, data = await self._items_of(
                "raindrops", str(collection), page=str(page), pagesize="50"
            )
            if data:
                raindrops += [Raindrop.from_json(raindrop) for raindrop in data]
                if count_update is not None:
                    count_update(len(raindrops))
                page += 1
            else:
                break
        if count_update is not None:
            count_update(len(raindrops))
        return raindrops

    async def tags(self, collection: int | None = None) -> list[TagData]:
        """Get a list of tags.

        Args:
            collection: The optional collection to get the tags for.

        Returns:
            A list of tags.
        """
        _, tags = await self._items_of(
            "/tags" if collection is None else f"/tags/{collection}"
        )
        return [TagData.from_json(tag) for tag in tags or []]


### api.py ends here
