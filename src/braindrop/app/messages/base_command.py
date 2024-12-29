"""Provides the base class for all application command messages."""

##############################################################################
# Python imports.
from re import Pattern, compile
from typing import Final

##############################################################################
# Textual imports.
from textual.binding import Binding
from textual.message import Message


##############################################################################
class Command(Message):
    """Base class for all application command messages."""

    COMMAND: str | None = None
    """The text for the command.

    Notes:
        If no `COMMAND` is provided the class name will be used.
    """

    FOOTER_TEXT: str | None = None
    """The text to show in the footer.

    Notes:
        If no `FOOTER_TEXT` is provided the `command` will be used.
    """

    BINDING_KEY: str | tuple[str, str] | None = None
    """The binding key for the command.

    This can either be a string, which is the keys to bind, a tuple of the
    keys and also an overriding display value, or `None`.
    """

    _SPLITTER: Final[Pattern[str]] = compile("[A-Z][^A-Z]*")
    """Regular expression for splitting up a command name."""

    @classmethod
    def command(cls) -> str:
        """The text for the command.

        Returns:
            The command's textual name.
        """
        return cls.COMMAND or " ".join(cls._SPLITTER.findall(cls.__name__))

    @classmethod
    def tooltip(cls) -> str:
        """The tooltip for the command."""
        return cls.__doc__ or ""

    @classmethod
    def _default_action_name(cls) -> str:
        """Get the default action name for the command.

        Returns:
            The default action name.
        """
        return f"{'_'.join(cls._SPLITTER.findall(cls.__name__))}_command".lower()

    @classmethod
    def binding(
        cls,
        action: str | None = None,
        show: bool = True,
    ) -> Binding:
        """Create a binding object for the command.

        Args:
            action: The optional action to call for the binding.
            show: Should the binding be shown in the footer?
        """
        if not cls.BINDING_KEY:
            raise ValueError("No binding key defined, unable to create a binding")
        keys, display = (
            cls.BINDING_KEY
            if isinstance(cls.BINDING_KEY, tuple)
            else (cls.BINDING_KEY, None)
        )
        return Binding(
            keys,
            action or cls._default_action_name(),
            description=cls.FOOTER_TEXT or cls.command(),
            tooltip=cls.tooltip(),
            show=show,
            key_display=display,
        )

    @property
    def has_binding(self) -> bool:
        """Does this command have a binding?"""
        return self.BINDING_KEY is not None


### base_command.py ends here
