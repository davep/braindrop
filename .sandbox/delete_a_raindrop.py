"""Test out making a new Raindrop then removing it."""

from asyncio import run

from rich.pretty import pprint as print

from braindrop.app.data import token_file
from braindrop.raindrop import API, Raindrop


async def make_it_rain() -> None:
    api = API(token_file().read_text().strip())
    raindrop = await api.add_raindrop(
        Raindrop(
            title="My remove test",
            link="http://example.com",
            excerpt="This should end up in trash",
        )
    )
    if raindrop:
        print(await api.remove_raindrop(raindrop))
    else:
        print("Add didn't happen so remove can't happen.")


run(make_it_rain())

### delete_a_raindrop.py ends here
