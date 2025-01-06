"""Tests for the tag suggestions class."""

##############################################################################
# Python imports.
from typing import Final

##############################################################################
# Pytest imports.
from pytest import fixture, mark

##############################################################################
# Local imports.
from braindrop.app.suggestions import SuggestTags
from braindrop.raindrop import Tag

##############################################################################
TAGS: Final[dict[str, Tag]] = {tag: Tag(tag * 10) for tag in "abcdefg"}
"""The tags to test with."""


##############################################################################
@fixture
def suggest_tags() -> SuggestTags:
    """Fixture for the tag suggestion object."""
    return SuggestTags(TAGS.values(), use_cache=False)


##############################################################################
async def test_empty_value_no_suggestion(suggest_tags: SuggestTags) -> None:
    """An empty value should get no suggestion."""
    assert (await suggest_tags.get_suggestion("")) is None


##############################################################################
async def test_simple_suggestion(suggest_tags: SuggestTags) -> None:
    """We should get the first suggestion when value implies it."""
    assert await suggest_tags.get_suggestion("a") == TAGS["a"]


##############################################################################
@mark.parametrize("tail", (",", ", ", " , ", ",  "))
async def test_no_suggestion_when_no_next_tag(
    suggest_tags: SuggestTags, tail: str
) -> None:
    """There should be no suggestion if no subsequent tag is being typed."""
    assert await suggest_tags.get_suggestion(f"{TAGS['a']}{tail}") is None


##############################################################################
async def test_no_repeat_suggestion(suggest_tags: SuggestTags) -> None:
    """The same tag should not be suggested once it's in the value."""
    assert await suggest_tags.get_suggestion(f"{TAGS['a']}, a") is None


##############################################################################
async def test_subsequent_suggestion(suggest_tags: SuggestTags) -> None:
    """A subsequent suggestion should be made."""
    assert (
        await suggest_tags.get_suggestion(f"{TAGS['a']}, d")
        == f"{TAGS['a']}, {TAGS['d']}"
    )


##############################################################################
async def test_order_should_not_matter(suggest_tags: SuggestTags) -> None:
    """The sort order of entered tags should not matter."""
    assert (
        await suggest_tags.get_suggestion(f"{TAGS['d']}, a")
        == f"{TAGS['d']}, {TAGS['a']}"
    )


### test_tag_suggestions.py ends here
