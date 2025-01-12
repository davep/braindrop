"""Tests for the Raindrop class."""

##############################################################################
# Pytest imports.
from pytest import mark, raises

##############################################################################
# Local imports.
from braindrop.raindrop import Raindrop, SpecialCollection, Tag


##############################################################################
def test_brand_new_randrop_reports_brand_new() -> None:
    """A brand new Raindrop should report itself as brand new."""
    assert Raindrop().is_brand_new is True


##############################################################################
def test_a_raindrop_with_an_identity_is_not_brand_new() -> None:
    """A Raindrop with an identity isn't seen as new."""
    assert Raindrop(identity=1).is_brand_new is False


##############################################################################
def test_editing_a_raindrop() -> None:
    """Test using the edit method to change a value in a Raindrop."""
    TITLE = "This is a test"
    raindrop = Raindrop(title=TITLE)
    updated = raindrop.edit(title="Changed")
    assert raindrop.title == TITLE
    assert updated.title != TITLE


##############################################################################
def test_an_edited_raindrop_should_be_a_different_instance() -> None:
    """When you edit a Raindrop it should result in a new instance."""
    raindrop = Raindrop()
    assert raindrop.edit(title="Changed") is not raindrop


##############################################################################
def test_editing_a_raindrop_property_that_does_not_exist() -> None:
    """Attempting to edit a property that doesn't exist should be an error."""
    with raises(TypeError):
        Raindrop().edit(not_a_property=42)


##############################################################################
@mark.parametrize(
    "collection, is_unsorted",
    (
        (SpecialCollection.ALL, False),
        (SpecialCollection.TRASH, False),
        (SpecialCollection.UNSORTED, True),
        (SpecialCollection.UNTAGGED, False),
        (SpecialCollection.BROKEN, False),
        (42, False),
    ),
)
def test_detect_unsorted(
    collection: SpecialCollection | int, is_unsorted: bool
) -> None:
    """Only Raindrops in the unsorted collection should report as such."""
    assert Raindrop(collection=collection).is_unsorted is is_unsorted


##############################################################################
@mark.parametrize(
    "tags, look_for, result",
    (
        (("tag",), ("tag",), True),
        (("Tag",), ("tag",), True),
        (("tag",), ("Tag",), True),
        (("t a g",), ("T a g",), True),
        (("tag", "tag"), ("tag",), True),
        (("Tag", "tag"), ("tag",), True),
        (("tag", "tag"), ("Tag",), True),
        (("tag",), ("tag", "tag"), True),
        (("Tag",), ("tag", "tag"), True),
        (("tag",), ("Tag", "tag"), True),
        (("gat", "tag", "gta"), ("tag",), True),
        (("gat", "tag", "gta"), ("tag", "gat"), True),
        (("gat", "tag", "gta"), ("TAG", "GAT"), True),
        (("gat",), ("tag",), False),
        (("gat", "tag"), ("gattag",), False),
        (("gat", "tag"), ("gat tag",), False),
        (("gat", "tag"), ("gat,tag",), False),
        (("gat", "tag"), ("gat, tag",), False),
    ),
)
def test_is_tagged(
    tags: tuple[str, ...], look_for: tuple[str, ...], result: bool
) -> None:
    """We should be able to check that a Raindrop has certain tags."""
    assert (
        Raindrop(tags=[Tag(tag) for tag in tags]).is_tagged(
            *(Tag(tag) for tag in look_for)
        )
        is result
    )


##############################################################################
@mark.parametrize(
    "needle, title, excerpt, note, link, domain, tags, result",
    (
        ("title", "title", "excerpt", "note", "link", "domain", ("tag",), True),
        ("Title", "title", "excerpt", "note", "link", "domain", ("tag",), True),
        ("excerpt", "title", "excerpt", "note", "link", "domain", ("tag",), True),
        ("Excerpt", "title", "excerpt", "note", "link", "domain", ("tag",), True),
        ("note", "title", "excerpt", "note", "link", "domain", ("tag",), True),
        ("Note", "title", "excerpt", "note", "link", "domain", ("tag",), True),
        ("tag", "title", "excerpt", "note", "link", "domain", ("tag",), True),
        ("Tag", "title", "excerpt", "note", "link", "domain", ("tag",), True),
        ("link", "title", "excerpt", "note", "link", "domain", ("tag",), True),
        ("Link", "title", "excerpt", "note", "link", "domain", ("tag",), True),
        ("domain", "title", "excerpt", "note", "link", "domain", ("tag",), True),
        ("Domain", "title", "excerpt", "note", "link", "domain", ("tag",), True),
        (
            "here",
            "ishere",
            "andhere",
            "alsohere",
            "herealso",
            "ohsohere",
            ("heretoo",),
            True,
        ),
        # Originally I was just smushing all the text-like parts of a
        # Raindrop together, which could result in false positives (actually
        # actual positives but they'd seem false to the average user). This
        # tests that I don't make that mistake again.
        (
            "excerpt title",
            "title",
            "excerpt",
            "note",
            "link",
            "domain",
            ("tag",),
            False,
        ),
        ("title note", "title", "excerpt", "note", "link", "domain", ("tag",), False),
        ("note tag", "title", "excerpt", "note", "link", "domain", ("tag",), False),
        (
            "tag1 tag2",
            "title",
            "excerpt",
            "note",
            "link",
            "domain",
            ("tag1", "tag2"),
            False,
        ),
    ),
)
def test_contains(
    needle: str,
    title: str,
    excerpt: str,
    note: str,
    link: str,
    domain: str,
    tags: tuple[str, ...],
    result: bool,
) -> None:
    """We should be able to test if some text is in a Raindrop."""
    assert (
        needle
        in Raindrop(
            title=title,
            excerpt=excerpt,
            note=note,
            link=link,
            domain=domain,
            tags=[Tag(tag) for tag in tags],
        )
    ) is result


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
