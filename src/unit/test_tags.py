"""Tests for handling tags."""

##############################################################################
# Pytest imports.
import pytest

##############################################################################
# Application imports.
from braindrop.raindrop import Tag


##############################################################################
@pytest.mark.parametrize(
    "tag, string",
    [
        ("test", "test"),
        ("Test", "test"),
        ("test", "Test"),
    ],
)
def test_tag_vs_str_equality(tag: str, string: str) -> None:
    """A `Tag` should be able to compare against a string."""
    assert Tag(tag, 0) == string
    assert string == Tag(tag, 0)


##############################################################################
@pytest.mark.parametrize(
    "tag0, tag1, count0, count1",
    [
        ("test", "test", 1, 1),
        ("Test", "test", 1, 1),
        ("test", "Test", 1, 1),
        ("test", "test", 1, 2),
        ("Test", "test", 1, 2),
        ("test", "Test", 1, 2),
    ],
)
def test_tag_vs_tag_equality(tag0: str, tag1: str, count0: int, count1: int) -> None:
    """A `Tag` should be able to compare against another `Tag`."""
    assert Tag(tag0, count0) == Tag(tag1, count1)


### test_tags.py ends here
