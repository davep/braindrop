"""Test out making a new Raindrop then updating it."""

from asyncio import run

from rich.pretty import pprint as print

from braindrop.app.data import token_file
from braindrop.raindrop import API, Raindrop


async def make_it_rain() -> None:
    api = API(token_file().read_text().strip())
    raindrop = await api.add_raindrop(
        Raindrop(
            title="My edit test", link="http://example.com", excerpt="This is the note"
        )
    )
    if raindrop:
        print(
            await api.update_raindrop(
                raindrop.edit(
                    note="This was added as an edit",
                    collection=46742381,
                ),
            )
        )
    else:
        print("Add didn't happen so edit can't happen.")


run(make_it_rain())

### update_a_raindrop.py ends here
