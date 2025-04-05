"""Tests for handling tags."""

##############################################################################
# Python imports.
from collections import Counter

##############################################################################
# Pytest imports.
from pytest import mark

##############################################################################
# Application imports.
from braindrop.raindrop.tag import Tag

##############################################################################
COMBINATIONS = (
    ("test", "test"),
    ("Test", "test"),
    ("test", "Test"),
)
"""The combination of things to test."""


##############################################################################
@mark.parametrize("tag, string", COMBINATIONS)
def test_tag_vs_str_equality(tag: str, string: str) -> None:
    """A `Tag` should be able to compare against a string."""
    assert Tag(tag) == string
    assert string == Tag(tag)


##############################################################################
@mark.parametrize("tag0, tag1", COMBINATIONS)
def test_tag_vs_tag_equality(tag0: str, tag1: str) -> None:
    """A `Tag` should be able to compare against another `Tag`."""
    assert Tag(tag0) == Tag(tag1)
    assert Tag(Tag(tag0)) == Tag(Tag(tag1))


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
    source = (Tag("c"), Tag("b"), Tag("a"), Tag("A"))
    assert sorted(source) == ["A", "a", "b", "c"]
    assert sorted(source) == ["a", "A", "b", "c"]


##############################################################################
@mark.parametrize("string", ("", "1"))
def test_tag_length(string: str) -> None:
    """We should be able to get the len of a tag."""
    assert len(Tag(string)) == len(string)


##############################################################################
@mark.parametrize("string, expected", (("", False), ("1", True)))
def test_tag_as_bool(string: str, expected: bool) -> None:
    """We should be able to treat a tag as a bool, in respect to its length."""
    assert bool(Tag(string)) is expected


##############################################################################
@mark.parametrize(
    "tag, startswith, expected",
    (
        ("foo", "bar", False),
        ("foo", "foo", True),
        ("FOO", "foo", True),
        ("foobarbaz", "foo", True),
        ("FOOBARBAZ", "foo", True),
        ("foobarbaz", "bar", False),
    ),
)
def test_tag_startswith(tag: str, startswith: str, expected: bool) -> None:
    """We should be able to see if one tag starts with another."""
    assert Tag(tag).startswith(startswith) is expected
    assert Tag(tag).startswith(Tag(startswith)) is expected


### test_tags.py ends here
