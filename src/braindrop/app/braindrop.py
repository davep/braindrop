"""The main application class."""

##############################################################################
# Python imports.
import os

##############################################################################
# Textual imports.
from textual.app import InvalidThemeError

##############################################################################
# Textual enhanced imports.
from textual_enhanced.app import EnhancedApp

##############################################################################
# Local imports.
from .. import __version__
from ..raindrop import API
from .data import (
    ExitState,
    load_configuration,
    token_file,
    update_configuration,
)
from .screens import Main, TokenInput


##############################################################################
class Braindrop(EnhancedApp[ExitState]):
    """The Braindrop application class."""

    HELP_TITLE = f"Braindrop v{__version__}"
    HELP_ABOUT = """
    `Braindrop` is a terminal-based client for
    [raindrop.io](https://raindrop.io/); it was created by and is maintained
    by [Dave Pearson](https://www.davep.org/); it is Free Software and can
    be [found on GitHub](https://github.com/davep/braindrop).
    """
    HELP_LICENSE = """
    Braindrop - A client for the Raindrop bookmarking service.  \n    Copyright (C) 2024-2025 Dave Pearson

    This program is free software: you can redistribute it and/or modify it
    under the terms of the GNU General Public License as published by the Free
    Software Foundation, either version 3 of the License, or (at your option)
    any later version.

    This program is distributed in the hope that it will be useful, but WITHOUT
    ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
    FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
    more details.

    You should have received a copy of the GNU General Public License along with
    this program. If not, see <https://www.gnu.org/licenses/>.
    """

    COMMANDS = set()

    def __init__(self) -> None:
        """Initialise the application."""
        super().__init__()
        configuration = load_configuration()
        if configuration.theme is not None:
            try:
                self.theme = configuration.theme
            except InvalidThemeError:
                pass

    def watch_theme(self) -> None:
        """Save the application's theme when it's changed."""
        with update_configuration() as config:
            config.theme = self.theme

    @staticmethod
    def environmental_token() -> str | None:
        """Try and get an API token from the environment.

        Returns:
           An API token found in the environment, or `None` if one wasn't found.
        """
        return os.environ.get("BRAINDROP_API_TOKEN")

    @property
    def api_token(self) -> str | None:
        """The API token for talking to Raindrop.

        If the token is found in the environment, it will be used. If not a
        saved token will be looked for and used. If one doesn't exist the
        value will be `None`.
        """
        try:
            return self.environmental_token() or token_file().read_text(
                encoding="utf-8"
            )
        except IOError:
            pass
        return None

    def token_bounce(self, token: str | None) -> None:
        """Handle the result of asking the user for their API token.

        Args:
            token: The resulting token.
        """
        if token:
            token_file().write_text(token, encoding="utf-8")
            self.push_screen(Main(API(token)))
        else:
            self.exit(ExitState.TOKEN_NEEDED)

    def on_mount(self) -> None:
        """Display the main screen.

        Note:
            If the Raindrop API token isn't known, the token input dialog
            will first be shown; the main screen will then only be shown
            once the token has been acquired.
        """
        if token := self.api_token:
            self.push_screen(Main(API(token)))
        else:
            self.push_screen(TokenInput(), callback=self.token_bounce)


### app.py ends here
