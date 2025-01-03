"""Test out getting suggestions."""

from asyncio import run

from rich.pretty import pprint as print

from braindrop.app.data import token_file
from braindrop.raindrop import API, Raindrop


async def make_it_rain() -> None:
    api = API(token_file().read_text().strip())
    print(await api.suggestions_for("http://example.com"))
    print(await api.suggestions_for(Raindrop(identity=935383666)))


run(make_it_rain())

### get_suggestions.py ends here
