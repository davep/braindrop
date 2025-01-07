"""Provides icons used within the widgets."""

##############################################################################
# Python imports.
from typing import Final

##############################################################################
# Rich imports.
from rich.emoji import Emoji

##############################################################################
# The various icons.

BROKEN_ICON: Final[str] = Emoji.replace(":skull:")
"""The icon for broken links."""

UNSORTED_ICON: Final[str] = Emoji.replace(":thinking_face:")
"""The icon for unsorted raindrops."""

PUBLIC_ICON: Final[str] = Emoji.replace(":globe_with_meridians:")
"""The icon to use for a public raindrop."""

PRIVATE_ICON: Final[str] = Emoji.replace(":lock:")
"""The icon to use for a private raindrop."""

### icons.py ends here
