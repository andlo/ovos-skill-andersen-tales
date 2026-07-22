"""Tests for _load_collection_meta() against the real locale/<lang>/
collection.voc + collection_meta.json files - not mocked, since the
whole point is verifying the actual bundled translations load and
parse correctly for every supported language (see
ovos-common-reading-pipeline-plugin#26)."""
import pytest


@pytest.mark.parametrize("lang,expected_author,expected_collection", [
    ("en-us", "Hans Christian Andersen", "Andersen's Fairy Tales"),
    ("da-dk", "H.C. Andersen", "H.C. Andersens Eventyr"),
    ("de-de", "Hans Christian Andersen", "Andersens Märchen"),
    ("es-es", "Hans Christian Andersen", "Cuentos de Andersen"),
    ("fr-fr", "Hans Christian Andersen", "Contes d'Andersen"),
    ("it-it", "Hans Christian Andersen", "Fiabe di Andersen"),
    ("nl-nl", "Hans Christian Andersen", "Andersens Sprookjes"),
])
def test_load_collection_meta_per_language(skill, monkeypatch, lang, expected_author, expected_collection):
    monkeypatch.setattr(type(skill), "lang", lang, raising=False)

    skill._load_collection_meta()

    assert skill._author_name == expected_author
    assert skill._collection_name == expected_collection
    assert "andersen" in skill._collection_aliases


def test_load_collection_meta_falls_back_for_english_variant(skill, monkeypatch):
    """en-gb has no dedicated locale folder - OVOS's own resource
    resolution (langcodes.tag_distance) should fall back to en-us
    automatically, with no special-casing needed here."""
    monkeypatch.setattr(type(skill), "lang", "en-gb", raising=False)

    skill._load_collection_meta()

    assert skill._author_name == "Hans Christian Andersen"
    assert skill._collection_name == "Andersen's Fairy Tales"


def test_danish_alias_matches_danish_phrasing(skill, monkeypatch):
    """Regression guard for the actual bug this fixes: a Danish
    collection_hint should match against Danish aliases - see
    ovos-common-reading-pipeline-plugin#26."""
    monkeypatch.setattr(type(skill), "lang", "da-dk", raising=False)
    skill._load_collection_meta()

    assert skill._matches_collection_hint("h.c. andersen") is True


def test_german_alias_matches_german_phrasing(skill, monkeypatch):
    monkeypatch.setattr(type(skill), "lang", "de-de", raising=False)
    skill._load_collection_meta()

    assert skill._matches_collection_hint("hans christian andersen") is True
