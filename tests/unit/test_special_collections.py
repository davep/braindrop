"""Test the special collection enum."""

##############################################################################
# Pytest imports.
from pytest import mark

##############################################################################
# Local imports.
from braindrop.raindrop import SpecialCollection


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


### test_special_collections.py ends here
