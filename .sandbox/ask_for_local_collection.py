"""Ensure asking for a 'local' collection is a failure."""

from asyncio import run

from rich.pretty import pprint as print

from braindrop.app.data import token_file
from braindrop.raindrop import API, SpecialCollection


async def make_it_rain() -> None:
    try:
        print(
            await API(token_file().read_text().strip()).raindrops(
                SpecialCollection.TRASH
            )
        )
        print(
            await API(token_file().read_text().strip()).raindrops(
                SpecialCollection.BROKEN
            )
        )
    except API.Error as error:
        print(error)


run(make_it_rain())

### create_new_raindrop.py ends here
