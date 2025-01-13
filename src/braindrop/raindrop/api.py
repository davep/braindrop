"""Provides a simple raindrop.io client.

NOTE: For the moment rate-limit handling, while it is in the core method
here, is only taken care of when it comes to downloading raindrops. At some
point I want to clean this up and ensure that *all* calls have such
protection. Mostly though this is good enough for what I need.

Also note that the status update callback is a wee bit janky in that it lets
the caller know that we're paused by sending a negative raindrop count.
Again, for now, this is good enough for my needs.
"""

##############################################################################
# Python imports.
from asyncio import sleep
from dataclasses import dataclass
from http import HTTPStatus
from json import loads
from ssl import SSLCertVerificationError
from typing import Any, Awaitable, Callable, Final, Literal

##############################################################################
# HTTPX imports.
from httpx import AsyncClient, HTTPStatusError, RequestError, Response

##############################################################################
# Local imports.
from .collection import Collection, SpecialCollection
from .raindrop import Raindrop
from .suggestions import Suggestions
from .user import User


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

    @dataclass
    class RateLimit(Error):
        """Exception raised when we hit a rate limit."""

        retry_after: int | None = None
        """The number of seconds to wait to retry."""

        def __str__(self) -> str:
            return f"Rate limit hit; retry after {self.retry_after} seconds"

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

    async def _call(
        self, method: Callable[..., Awaitable[Response]], *path: str, **params: Any
    ) -> str:
        """Call on the Raindrop API.

        Args:
            method: The method to use to make the call.
            path: The path for the API call.
            params: The parameters for the call.

        Returns:
            The text returned from the call.

        Raises:
            API.RequestError: If there was a problem with the request.
            API.RateLimit: If a rate limit was hit.
        """
        payload: dict[str, Any] = (
            {
                "json"
                if method in (self._client.post, self._client.put)
                else "params": params
            }
            if params
            else {}
        )
        try:
            response = await method(
                self._api_url(*path),
                **payload,
                headers={
                    "user-agent": self.AGENT,
                    "Authorization": f"Bearer {self._token}",
                },
            )
        except (RequestError, SSLCertVerificationError) as error:
            raise self.RequestError(str(error)) from None

        try:
            response.raise_for_status()
        except HTTPStatusError as error:
            # If we've hit a rate limit...
            if error.response.status_code == HTTPStatus.TOO_MANY_REQUESTS:
                # ...we'll raise an exception to let the caller know and let
                # them decide what to do.
                #
                # NOTE: https://developer.raindrop.io/#rate-limiting says
                # that X-RateLimit-Reset should be available and should tell
                # us when it's safe to make a fresh request. In testing I'm
                # not seeing this at all, but I *am* seeing Retry-After.
                raise self.RateLimit(
                    int(error.response.headers["Retry-After"])
                    if "Retry-After" in error.response.headers
                    else None
                )
            else:
                raise self.RequestError(str(error)) from None

        return response.text

    async def _get(self, *path: str, **params: Any) -> str:
        """Perform a GET call against the Raindrop API.

        Args:
            path: The path for the API call.
            params: The parameters for the call.

        Returns:
            The string result of the call.
        """
        return await self._call(self._client.get, *path, **params)

    async def _post(self, *path: str, **params: Any) -> str:
        """Perform a POST call against the Raindrop API.

        Args:
            path: The path for the API call.
            params: The parameters for the call.

        Returns:
            The string result of the call.
        """
        return await self._call(self._client.post, *path, **params)

    async def _put(self, *path: str, **params: Any) -> str:
        """Perform a PUT call against the Raindrop API.

        Args:
            path: The path for the API call.
            params: The parameters for the call.

        Returns:
            The string result of the call.
        """
        return await self._call(self._client.put, *path, **params)

    async def _delete(self, *path: str, **params: Any) -> str:
        """Perform a DELETE call against the Raindrop API.

        Args:
            path: The path for the API call.
            params: The parameters for the call.

        Returns:
            The string result of the call.
        """
        return await self._call(self._client.delete, *path, **params)

    async def _result_of(
        self,
        method: Callable[..., Awaitable[str]],
        value: str | None,
        *path: str,
        **params: Any,
    ) -> tuple[bool, Any]:
        """Get the result of a call to the Raindrop API.

        Args:
            method: The method for the call.
            value: The name of the value to pull from the result.
            path: The path for the API call.
            params: The parameters for the call.

        Returns:
            A tuple of a bool that is the result plus any data from the call.
        """
        result = loads(await method(*path, **params))
        return (
            result["result"],
            result[value] if value is not None and value in result else None,
        )

    async def _items_of(
        self, method: Callable[..., Awaitable[str]], *path: str, **params: str
    ) -> tuple[bool, list[Any] | None]:
        """Get the items of a call to the Raindrop API.

        Args:
            method: The method for the call.
            path: The path for the API call.
            params: The parameters for the call.

        Returns:
            A tuple of a bool that is the result plus any items from the call.
        """
        return await self._result_of(method, "items", *path, **params)

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
            self._get, f"collections{'' if level == 'root' else '/childrens'}"
        )
        return [Collection.from_json(collection) for collection in collections or []]

    async def user(self) -> User | None:
        """Get the user details.

        Returns:
            The details of the current user, or `None` if the details could
            not be fetched.
        """
        result, user = await self._result_of(self._get, "user", "user")
        return User.from_json(user) if result and user is not None else None

    @staticmethod
    def maybe_on_the_server(collection: int | SpecialCollection) -> bool:
        """Check if the given collection is likely to be on the server.

        Args:
            collection: The collection to check.

        Returns:
            `True` if likely on the server, `False` if not.

        Notes:
            This method doesn't check that the collection *is* on the
            server, it just helps check that it might be.
        """
        try:
            collection = SpecialCollection(collection)
        except ValueError:
            return collection > 0
        return not collection.is_local

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

            If a negative value is passed to `count_update`, this is the
            number of raindrops that have been downloaded, but at that point
            the download has been paused due to a rate limit.
        """
        if not self.maybe_on_the_server(collection):
            raise self.Error(f"{collection} is not a valid collection ID")
        page = 0
        raindrops: list[Raindrop] = []
        if count_update is None:

            def gndn(_: int) -> None:
                pass

            count_update = gndn
        count_update(0)
        while True:
            try:
                _, data = await self._items_of(
                    self._get,
                    "raindrops",
                    str(int(collection)),
                    page=str(page),
                    pagesize="50",
                )
            except self.RateLimit as limit:
                if limit.retry_after is None:
                    raise self.RequestError(
                        "Raindrop.io API limit exceeded with no option to retry"
                    )
                count_update(-len(raindrops))
                await sleep(limit.retry_after)
                continue
            if data:
                raindrops += [Raindrop.from_json(raindrop) for raindrop in data]
                count_update(len(raindrops))
                page += 1
            else:
                break
        count_update(len(raindrops))
        return raindrops

    async def add_raindrop(self, raindrop: Raindrop) -> Raindrop | None:
        """Add a raindrop.

        Args:
            raindrop: The raindrop to add.

        Returns:
            The posted raindrop data, or `None` if there was a problem.

        Raises:
            RequestError: If there was a problem with the request.
        """
        result, resulting_raindrop = await self._result_of(
            self._post, "item", "raindrop", **raindrop.as_json
        )
        return Raindrop.from_json(resulting_raindrop) if result else None

    async def update_raindrop(self, raindrop: Raindrop) -> Raindrop | None:
        """Update a raindrop.

        Args:
            raindrop: The raindrop to update.

        Returns:
            The updated raindrop data, or `None` if there was a problem.

        Raises:
            RequestError: If there was a problem with the request.
        """
        result, resulting_raindrop = await self._result_of(
            self._put, "item", "raindrop", str(raindrop.identity), **raindrop.as_json
        )
        return Raindrop.from_json(resulting_raindrop) if result else None

    async def remove_raindrop(self, raindrop: Raindrop) -> bool:
        """Remove a raindrop.

        Args:
            raindrop: The raindrop to remove.

        Returns:
            `True` if the delete worked, `False` if not.

        Raises:
            RequestError: If there was a problem with the request.

        Notes:
            The Raindrop API itself will move the raindrop to the trash
            folder if it isn't in trash; the raindrop being removed is in
            trash it will be permanently deleted.
        """
        result, _ = await self._result_of(
            self._delete, None, "raindrop", str(raindrop.identity)
        )
        return result

    async def suggestions_for(self, link: Raindrop | str) -> Suggestions:
        """Get suggestions for a link.

        Args:
            link: The link to get suggestions for.

        Returns:
            The suggestions for the link.

        Raises:
            RequestError: If there was a problem with the request.
        """
        if isinstance(link, Raindrop):
            getter = self._result_of(
                self._get, "item", "raindrop", str(link.identity), "suggest"
            )
        else:
            getter = self._result_of(
                self._post, "item", "raindrop", "suggest", link=link
            )
        _, suggestions = await getter
        return Suggestions.from_json(suggestions)


### api.py ends here
