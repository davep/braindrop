"""Tests for saving and loading local data."""

##############################################################################
# Pytest imports.
from pytest import MonkeyPatch

##############################################################################
# Python imports.
from pathlib import Path

##############################################################################
# Application imports.
from braindrop.app.data.local import LocalData
from braindrop.raindrop import API, get_time


##############################################################################
def test_get_time_with_null_value() -> None:
    """A null value should result in no time, rather than an error."""
    assert get_time({"when": None}, "when") is None
    assert get_time({}, "when") is None


##############################################################################
def test_load_freshly_saved_data_with_no_user(
    tmp_path: Path, monkeypatch: MonkeyPatch
) -> None:
    """Loading data saved before anything was downloaded should not fail."""
    monkeypatch.setattr(
        "braindrop.app.data.local.local_data_file",
        lambda: tmp_path / "raindrops.json",
    )
    LocalData(API("dummy-token")).save()
    reloaded = LocalData(API("dummy-token")).load()
    assert reloaded.user is None
    assert reloaded.last_downloaded is None


### test_local_data.py ends here
