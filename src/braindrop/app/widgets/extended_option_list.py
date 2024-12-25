"""A version of Textual's OptionList with some more navigation options."""

##############################################################################
# Textual imports.
from textual.binding import Binding
from textual.widgets import OptionList


##############################################################################
class OptionListEx(OptionList):
    """The Textual `OptionList` with more navigation keys."""

    BINDINGS = [
        Binding("j", "cursor_down", show=False),
        Binding("k", "cursor_up", show=False),
    ]


### extended_option_list.py ends here
