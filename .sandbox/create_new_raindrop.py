"""Test out making a new Raindrop."""

from asyncio import run

from rich.pretty import pprint as print

from braindrop.app.data import token_file
from braindrop.raindrop import API, Raindrop


async def make_it_rain() -> None:
    print(
        await API(token_file().read_text().strip()).add_raindrop(
            Raindrop(
                title="My API Test", link="http://example.com", note="This is the note"
            )
        )
    )


run(make_it_rain())

### create_new_raindrop.py ends here
