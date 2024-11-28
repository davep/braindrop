"""Main entry point for the application."""

from pathlib import Path

##############################################################################
# Local imports.
from .raindrop import Raindrop

##############################################################################
def main() -> None:
    """Main entry point."""
    print(Raindrop(Path(".test_token").read_text().strip()))

##############################################################################
if __name__ == "__main__":
    main()

### __main__.py ends here
