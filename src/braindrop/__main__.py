"""Main entry point for the application."""

##############################################################################
# Local imports.
from .app import Braindrop
from .app.data import ExitState


##############################################################################
def main() -> None:
    """Main entry point."""
    match Braindrop().run():
        case ExitState.TOKEN_FORGOTTEN:
            if Braindrop.environmental_token():
                print(
                    "It looks like your token is held in an environment variable. "
                    "If you wish to have that forgotten you will need to remove it yourself."
                )
            else:
                print("The locally-held copy of your API token has been removed.")
        case ExitState.TOKEN_NEEDED:
            print("An API token is needed to be able to connect to raindrop.io.")


##############################################################################
if __name__ == "__main__":
    main()

### __main__.py ends here
