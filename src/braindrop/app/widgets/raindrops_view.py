"""Provides a widget for viewing a collection of Raindrops."""

##############################################################################
# Textual imports.
from textual.widgets import OptionList

##############################################################################
# Local imports.
from ...raindrop import Raindrop


##############################################################################
class RaindropsView(OptionList):
    """A widget for viewing a collection of Raindrops."""

    def show(self, raindrops: list[Raindrop]) -> None:
        """Show the given raindrops.

        Args:
            raindrops: The raindrops to show.
        """
        self.clear_options().add_options([raindrop.title for raindrop in raindrops])


### raindrops_view.py ends here
