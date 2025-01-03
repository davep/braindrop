"""Provides a function for parsing time."""

##############################################################################
# Python imports.
from datetime import datetime


##############################################################################
def parse_time(text: str) -> datetime:
    """Parse a time from the Raindrop API.

    Args:
        text: The text version of the time to parse.

    Returns:
        The parsed time.

    Raindrop returns times ending in a `Z`. Python doesn't seem capable of
    parsing that. So we swap that for a `+00:00` and then parse.
    """
    return datetime.fromisoformat(
        (text.removesuffix("Z") + "+00:00") if "Z" in text else text
    )


##############################################################################
def get_time(data: dict[str, str], name: str) -> datetime | None:
    """Get a datetime value from a given dictionary.

    Args:
        data: The data to get the value from.
        name: The name of the value to get from the data.

    Returns:
        A `datetime` parsed from the `str` value if it exists, otherwise
        `None`.
    """
    return parse_time(data[name]) if name in data else None


##############################################################################
def json_time(time: datetime | None) -> str | None:
    """Convert a time value into a JSON-friendly string.

    Args:
        time: The time to convert.

    Returns:
        The time formatted as a string, if not `None`, else `None.
    """
    return time if time is None else time.isoformat()


### time_tools.py ends here
