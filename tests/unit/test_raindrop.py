"""Tests for the Raindrop class."""

##############################################################################
# Pytest imports.
import pytest

##############################################################################
# Local imports.
from braindrop.raindrop import Raindrop, Tag


##############################################################################
def test_make_tag_string() -> None:
    """Given a list of tags we should be able to make a string."""
    assert Raindrop.tags_to_string([Tag("a"), Tag("b")]) == "a, b"


##############################################################################
def test_make_tag_string_squishes_duplicates() -> None:
    """When making a string from a list of tags, it will squish duplicates."""
    assert Raindrop.tags_to_string([Tag("a"), Tag("a"), Tag("b")]) == "a, b"


##############################################################################
def test_make_tag_string_squishes_duplicates_including_case() -> None:
    """When making a string from a list of tags, it will case-insensitive squish duplicates."""
    assert Raindrop.tags_to_string([Tag("a"), Tag("A"), Tag("b")]) == "a, b"


##############################################################################
def test_make_tag_list() -> None:
    """Given a string of tags, we should get a list of them back."""
    target = [Tag("a"), Tag("b")]
    assert Raindrop.string_to_tags("a,b") == target
    assert Raindrop.string_to_tags("a, b") == target
    assert Raindrop.string_to_tags(",,a,,, b,,,") == target


##############################################################################
@pytest.mark.parametrize(
    "string",
    (
        "a,a,a,b",
        "a, a, a, b",
        ",,a,,,a,,a,a,, b,,,",
    ),
)
def test_make_tag_list_squishes_duplicates(string: str) -> None:
    """When making a list from a string of tags, it will squish duplicates."""
    assert Raindrop.string_to_tags(string) == [Tag("a"), Tag("b")]


##############################################################################
def test_make_tag_list_squishes_duplicates_including_case() -> None:
    """When making a list from a string of tags, it will case-insensitive squish duplicates."""
    target = [Tag("a"), Tag("b")]
    assert Raindrop.string_to_tags("a,A,a,b") == target
    assert Raindrop.string_to_tags("a, A, a, b") == target
    assert Raindrop.string_to_tags(",,a,,,A,,a,A,, b,,,") == target


### test_raindrop.py ends here
