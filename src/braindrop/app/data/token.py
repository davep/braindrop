"""Code relating to the token file."""

##############################################################################
# Python imports.
from pathlib import Path

##############################################################################
# Local imports.
from .locations import data_dir


##############################################################################
def token_file() -> Path:
    """The file where the API token is held.

    Returns:
        The path to the token file.
    """
    return data_dir() / ".token"


### token.py ends here
