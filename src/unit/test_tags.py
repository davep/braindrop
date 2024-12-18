"""Tests for handling tags."""

##############################################################################
# Python imports.
from collections import Counter

##############################################################################
# Pytest imports.
import pytest

##############################################################################
# Application imports.
from braindrop.raindrop.tag import Tag


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
    assert Tag(tag) == string
    assert string == Tag(tag)


##############################################################################
@pytest.mark.parametrize(
    "tag0, tag1",
    [
        ("test", "test"),
        ("Test", "test"),
        ("test", "Test"),
        ("test", "test"),
        ("Test", "test"),
        ("test", "Test"),
    ],
)
def test_tag_vs_tag_equality(tag0: str, tag1: str) -> None:
    """A `Tag` should be able to compare against another `Tag`."""
    assert Tag(tag0) == Tag(tag1)


##############################################################################
def test_tags_in_set() -> None:
    """A set of the same tag with different case should be one item."""
    assert len({Tag(tag) for tag in ("foo", "FOO", "Foo", "foO")}) == 1


##############################################################################
def test_counting_tags() -> None:
    """A count of the same tag with different case should count the one tag."""
    source = ("foo", "FOO", "Foo", "foO")
    count = Counter(Tag(tag) for tag in source)
    assert len(count) == 1
    assert list(count.values()) == [len(source)]


##############################################################################
def test_sort_tags() -> None:
    """We would be able to sort a list of tags."""
    assert sorted((Tag("c"), Tag("b"), Tag("a"), Tag("A"))) == ["A", "a", "b", "c"]


### test_tags.py ends here
