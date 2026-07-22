"""Smoke tests + the load-time language gate in initialize()."""
from unittest.mock import MagicMock

from conftest import AndersenTales, StoryFetchError


def test_imports_cleanly():
    assert AndersenTales is not None
    assert issubclass(StoryFetchError, Exception)


def test_andersen_tales_is_an_ovos_skill():
    from ovos_workshop.skills import OVOSSkill
    assert issubclass(AndersenTales, OVOSSkill)


def test_initialize_stays_inert_for_unsupported_language(skill, monkeypatch):
    """The key behavior requested: don't just decline searches at
    runtime - never even build the index or register bus events at all
    for a language this provider can't serve (and doesn't translate)."""
    monkeypatch.setattr(type(skill), "lang", "pl-pl", raising=False)
    skill.refresh_index = MagicMock()
    skill.add_event = MagicMock()

    skill.initialize()

    skill.refresh_index.assert_not_called()
    skill.add_event.assert_not_called()
    assert skill.index == {}


def test_initialize_loads_normally_for_supported_language(skill, monkeypatch):
    monkeypatch.setattr(type(skill), "lang", "da-dk", raising=False)
    skill.refresh_index = MagicMock()
    skill._load_collection_meta = MagicMock()
    skill.add_event = MagicMock()

    skill.initialize()

    skill.refresh_index.assert_called_once()
    skill._load_collection_meta.assert_called_once()
    assert skill.add_event.call_count == 3

