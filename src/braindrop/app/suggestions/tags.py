"""Provides a suggester for tags."""

##############################################################################
# Python imports.
import re
from typing import Final, Iterable, Pattern

##############################################################################
# Textual imports.
from textual.suggester import Suggester

##############################################################################
# Local imports.
from ...raindrop import Raindrop, Tag
from ..data import TagCount


##############################################################################
class SuggestTags(Suggester):
    """A Textual `Input` suggester that suggests tags."""

    def __init__(self, tags: Iterable[Tag | TagCount], use_cache: bool = True) -> None:
        """Initialise the suggester.

        Args:
            tags: The collection of tags to suggest from.
        """
        # Note that we're going to be doing a case-insensitive match, but
        # the suggester API doesn't provide the raw value if you're not
        # being case-sensitive; so here we say we *are* going to be case
        # sensitive and then in get_suggestion we'll handle it ourselves.
        super().__init__(use_cache=use_cache, case_sensitive=True)
        self._tags = [tag.tag if isinstance(tag, TagCount) else tag for tag in tags]
        """The tags to take suggestions from."""

    _SUGGESTABLE: Final[Pattern[str]] = re.compile(r".*[^,\s]$")
    """Regular expression to test if a value deserves a suggestion."""

    async def get_suggestion(self, value: str) -> str | None:
        """Get suggestions for the given value.

        Args:
            value: The value to make a suggestion for.

        Returns:
            A suggested completion, or `None` if none could be made.
        """
        if self._SUGGESTABLE.match(value):
            try:
                *used_tags, last_tag = Raindrop.string_to_raw_tags(value)
            except ValueError:
                return None
            for candidate_index, candidate in enumerate(self._tags):
                if candidate.startswith(last_tag) and candidate not in used_tags:
                    return value[: -len(last_tag)] + str(self._tags[candidate_index])
        return None


### tags.py ends here
