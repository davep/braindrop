"""A version of Textual's OptionList with some more navigation options."""

##############################################################################
# Python imports.
from types import TracebackType

##############################################################################
# Textual imports.
from textual.binding import Binding
from textual.widgets import OptionList
from textual.widgets.option_list import OptionDoesNotExist

##############################################################################
# Typing extension imports.
from typing_extensions import Self


##############################################################################
class PreservedHighlight:
    """Context manager class to preserve an `OptionList` location.

    If the highlighted option has an ID, an attempt will be made to get back
    to that option; otherwise we return to the option in the same location.
    """

    def __init__(self, option_list: OptionList) -> None:
        """Initialise the object.

        Args:
            option_list: The `OptionList` to preserve the location for.
        """
        self._option_list = option_list
        """The option list we're preserving the location for."""
        self._highlighted = option_list.highlighted
        """The highlight that we should try to go back to."""
        self._option_id = (
            option_list.get_option_at_index(self._highlighted).id
            if self._highlighted is not None
            else None
        )
        """The ID of the option to try and get back to, or `None`."""

    def __enter__(self) -> Self:
        """Handle entry to the context."""
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_traceback: TracebackType | None,
    ) -> None:
        """Handle exit from the context."""
        del exc_type, exc_val, exc_traceback
        # Attempt to get back to the same option, or an option in a similar
        # location.
        try:
            self._option_list.highlighted = (
                self._highlighted
                if self._option_id is None
                else self._option_list.get_option_index(self._option_id)
            )
        except OptionDoesNotExist:
            self._option_list.highlighted = self._highlighted
        # If we still haven't landed anywhere and there are options, select
        # the first one.
        if self._option_list.highlighted is None and self._option_list.option_count:
            self._option_list.highlighted = 0


##############################################################################
class OptionListEx(OptionList):
    """The Textual `OptionList` with more features."""

    DEFAULT_CSS = """
    OptionListEx {
        &:focus {
            background-tint: initial;
        }
    }
    """

    BINDINGS = [
        Binding("j, right", "cursor_down", show=False),
        Binding("k, left", "cursor_up", show=False),
    ]

    @property
    def preserved_highlight(self) -> PreservedHighlight:
        """Provides a context that preserves the highlight location."""
        return PreservedHighlight(self)


### extended_option_list.py ends here
