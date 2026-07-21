"""Smoke tests + language fallback in update_index()."""
from unittest.mock import MagicMock

from conftest import AndersenTales, StoryFetchError


def test_imports_cleanly():
    assert AndersenTales is not None
    assert issubclass(StoryFetchError, Exception)


def test_andersen_tales_is_an_ovos_skill():
    from ovos_workshop.skills import OVOSSkill
    assert issubclass(AndersenTales, OVOSSkill)


def test_update_index_falls_back_to_english_for_unsupported_language(skill, monkeypatch):
    monkeypatch.setattr(type(skill), "lang", "xx-xx", raising=False)
    requested_urls = []

    def fake_get_index(url):
        requested_urls.append(url)
        return {}

    skill.get_index = fake_get_index
    skill.update_index()

    assert requested_urls == ["https://www.andersenstories.com/en/andersen_fairy-tales/list"]
