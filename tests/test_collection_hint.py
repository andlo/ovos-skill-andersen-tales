"""Tests for fuzzy collection_hint matching."""
import pytest


@pytest.mark.parametrize("hint", [
    "andersen", "Andersen", "hans christian andersen", "h c andersen",
    "h.c. andersen", "hans andersen", "HC Andersen",
])
def test_matches_known_aliases(skill, hint):
    assert skill._matches_collection_hint(hint) is True


@pytest.mark.parametrize("hint", ["grimm", "the brothers grimm", "andrew lang"])
def test_does_not_match_other_collections(skill, hint):
    assert skill._matches_collection_hint(hint) is False


def test_none_hint_matches_everyone(skill):
    assert skill._matches_collection_hint(None) is True


def test_empty_string_hint_matches_everyone(skill):
    assert skill._matches_collection_hint("") is True
