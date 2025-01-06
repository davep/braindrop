"""Tests for the Raindrop class."""

##############################################################################
# Pytest imports.
from pytest import mark, raises

##############################################################################
# Local imports.
from braindrop.raindrop import Raindrop, Tag


##############################################################################
def test_brand_new_randrop_reports_brand_new() -> None:
    """A brand new Raindrop should report itself as brand new."""
    assert Raindrop().is_brand_new is True


##############################################################################
def test_editing_a_raindrop() -> None:
    """Test using the edit method to change a value in a Raindrop."""
    TITLE = "This is a test"
    raindrop = Raindrop(title=TITLE)
    assert raindrop.title == TITLE
    assert raindrop.edit(title="Changed").title != TITLE


##############################################################################
def test_editing_a_raindrop_property_that_does_not_exist() -> None:
    """Attempting to edit a property that doesn't exist should be an error."""
    with raises(TypeError):
        Raindrop().edit(not_a_property=42)


##############################################################################
def test_an_edited_raindrop_should_be_a_different_instance() -> None:
    """When you edit a Raindrop it should result in a new instance."""
    raindrop = Raindrop()
    assert raindrop.edit(title="Changed") is not raindrop


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
@mark.parametrize(
    "string",
    (
        "a,b",
        "a, b",
        ",,a,,, b,,,",
    ),
)
def test_make_tag_list(string: str) -> None:
    """Given a string of tags, we should get a list of them back."""
    assert Raindrop.string_to_tags(string) == [Tag("a"), Tag("b")]


##############################################################################
@mark.parametrize(
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
@mark.parametrize(
    "string",
    (
        "a,A,a,b",
        "a, A, a, b",
        ",,a,,,A,,a,A,, b,,,",
    ),
)
def test_make_tag_list_squishes_duplicates_including_case(string: str) -> None:
    """When making a list from a string of tags, it will case-insensitive squish duplicates."""
    assert Raindrop.string_to_tags(string) == [Tag("a"), Tag("b")]


##############################################################################
@mark.parametrize(
    "string",
    (
        "a,A,b,B,a,a",
        "A,A,B,B,A,A",
        "a,,A,b,,B,,a,,a,,",
        "a , , A , b , , B , , a , , a , , ",
    ),
)
def test_make_raw_tag_list(string: str) -> None:
    target = [Tag("a"), Tag("A"), Tag("b"), Tag("B"), Tag("a"), Tag("A")]
    assert Raindrop.string_to_raw_tags(string) == target


### test_raindrop.py ends here
