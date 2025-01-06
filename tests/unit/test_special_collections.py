"""Test the special collection enum."""

##############################################################################
# Pytest imports.
from pytest import mark

##############################################################################
# Local imports.
from braindrop.raindrop import API, SpecialCollection


##############################################################################
@mark.parametrize(
    "collection, is_local",
    (
        (SpecialCollection.ALL, False),
        (SpecialCollection.UNSORTED, False),
        (SpecialCollection.TRASH, False),
        (SpecialCollection.UNTAGGED, True),
        (SpecialCollection.BROKEN, True),
    ),
)
def test_local_collections(collection: SpecialCollection, is_local: bool) -> None:
    """Does each collection ID correctly report if it's local or not?"""
    assert collection.is_local is is_local


##############################################################################
@mark.parametrize(
    "collection, maybe_available",
    (
        (0, True),
        (1, True),
        (99, True),
        (-1, True),
        (-2, False),
        (SpecialCollection.ALL, True),
        (SpecialCollection.UNSORTED, True),
        (SpecialCollection.TRASH, True),
        (SpecialCollection.UNTAGGED, False),
        (SpecialCollection.BROKEN, False),
    ),
)
def test_maybe_on_the_server(
    collection: int | SpecialCollection, maybe_available: bool
) -> None:
    """The API class should help us decide if we can ask for a collection."""
    assert API.maybe_on_the_server(collection) is maybe_available


### test_special_collections.py ends here
