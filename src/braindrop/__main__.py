"""Main entry point for the application."""

##############################################################################
# Python imports.
from argparse import ArgumentParser, Namespace
from inspect import cleandoc
from operator import attrgetter

##############################################################################
# Textual enhanced imports.
from textual_enhanced.commands import Command

##############################################################################
# Local imports.
from . import __doc__, __version__
from .app import Braindrop
from .app.data import ExitState


##############################################################################
def get_args() -> Namespace:
    """Get the command line arguments.

    Returns:
        The arguments.
    """

    # Build the parser.
    parser = ArgumentParser(
        prog="braindrop",
        description=__doc__,
        epilog=f"v{__version__}",
    )

    # Add --version
    parser.add_argument(
        "-v",
        "--version",
        help="Show version information",
        action="version",
        version=f"%(prog)s v{__version__}",
    )

    # Add --license
    parser.add_argument(
        "--license",
        "--licence",
        help="Show license information",
        action="store_true",
    )

    # Add --bindings
    parser.add_argument(
        "-b",
        "--bindings",
        help="List commands that can have their bindings changed",
        action="store_true",
    )

    # Add --theme
    parser.add_argument(
        "-t",
        "--theme",
        help="Set the theme for the application (set to ? to list available themes)",
    )

    # Finally, parse the command line.
    return parser.parse_args()


##############################################################################
def show_bindable_commands() -> None:
    """Show the commands that can have bindings applied."""
    from rich.console import Console
    from rich.markup import escape

    from .app.screens import Main

    console = Console(highlight=False)
    command: type[Command]
    for command in sorted(Main.COMMAND_MESSAGES, key=attrgetter("__name__")):
        if command().has_binding:
            console.print(
                f"[bold]{escape(command.__name__)}[/] [dim italic]- {escape(command.tooltip())}[/]"
            )
            console.print(
                f"    [dim italic]Default: {escape(command.binding().key)}[/]"
            )


##############################################################################
def show_themes() -> None:
    """Show the available themes."""
    for theme in sorted(Braindrop(Namespace(theme=None)).available_themes):
        if theme != "textual-ansi":
            print(theme)


##############################################################################
def main() -> None:
    """Main entry point."""
    args = get_args()
    if args.license:
        print(cleandoc(Braindrop.HELP_LICENSE))
    elif args.bindings:
        show_bindable_commands()
    elif args.theme == "?":
        show_themes()
    else:
        match Braindrop(args).run():
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
