"""Main entry point for the application."""

##############################################################################
# Python imports.
from asyncio import run
from pathlib import Path

##############################################################################
# Local imports.
from .raindrop import Raindrop


##############################################################################
def main() -> None:
    """Main entry point."""

    async def tester() -> None:
        for collection in await Raindrop(
            Path(".test_token").read_text().strip()
        ).root_collections():
            print(collection.title)

    run(tester())


##############################################################################
if __name__ == "__main__":
    main()

### __main__.py ends here
