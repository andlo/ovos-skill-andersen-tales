"""Tests for the ovos.common_tales.* bus protocol handlers."""
from unittest.mock import MagicMock

from conftest import COMMON_TALES_SEARCH_RESPONSE, COMMON_TALES_FETCH_STORY_RESPONSE, StoryFetchError


def make_message(data=None, msg_type="ovos.common_tales.search"):
    m = MagicMock()
    m.data = data or {}
    m.msg_type = msg_type
    m.reply = MagicMock(side_effect=lambda mtype, d: MagicMock(msg_type=mtype, data=d))
    return m


def test_handle_search_matches_by_phrase(skill):
    skill.index = {"The Ugly Duckling": "http://x/duckling", "The Little Mermaid": "http://x/mermaid"}

    skill.handle_search(make_message({"phrase": "ugly duckling"}))

    reply_type, data = skill.bus.emit.call_args[0][0].msg_type, skill.bus.emit.call_args[0][0].data
    assert reply_type == COMMON_TALES_SEARCH_RESPONSE
    assert data["title"] == "The Ugly Duckling"
    assert data["story_id"] == "The Ugly Duckling"
    assert data["skill_id"] == skill.skill_id
    assert data["source"] == "andersenstories.com"
    assert 0.0 <= data["confidence"] <= 1.0


def test_handle_search_stays_silent_on_empty_index(skill):
    skill.index = {}
    skill.handle_search(make_message({"phrase": "anything"}))
    skill.bus.emit.assert_not_called()


def test_handle_search_stays_silent_when_collection_hint_does_not_match(skill):
    skill.index = {"The Ugly Duckling": "http://x/duckling"}
    skill.handle_search(make_message({"phrase": "ugly duckling", "collection_hint": "grimm"}))
    skill.bus.emit.assert_not_called()


def test_handle_search_responds_when_collection_hint_matches(skill):
    skill.index = {"The Ugly Duckling": "http://x/duckling"}
    skill.handle_search(make_message({"phrase": "ugly duckling", "collection_hint": "hans christian andersen"}))
    skill.bus.emit.assert_called_once()


def test_handle_search_surprise_me_with_matching_hint_and_no_phrase(skill):
    skill.index = {"The Ugly Duckling": "http://x/duckling"}
    skill.handle_search(make_message({"phrase": None, "collection_hint": "andersen"}))
    skill.bus.emit.assert_called_once()
    data = skill.bus.emit.call_args[0][0].data
    assert data["title"] == "The Ugly Duckling"
    assert data["confidence"] == 1.0


def test_handle_search_no_phrase_no_hint_stays_silent(skill):
    skill.index = {"The Ugly Duckling": "http://x/duckling"}
    skill.handle_search(make_message({"phrase": None, "collection_hint": None}))
    skill.bus.emit.assert_not_called()


def test_handle_fetch_story_success(skill):
    skill.index = {"The Ugly Duckling": "http://x/duckling"}
    skill.get_story = MagicMock(return_value="Once upon a time.\n\nThe end.")

    skill.handle_fetch_story(make_message({"story_id": "The Ugly Duckling"}))

    sent = skill.bus.emit.call_args[0][0]
    assert sent.msg_type == COMMON_TALES_FETCH_STORY_RESPONSE
    assert sent.data["paragraphs"] == ["Once upon a time.", "The end."]


def test_handle_fetch_story_unknown_id_returns_empty(skill):
    skill.index = {}
    skill.handle_fetch_story(make_message({"story_id": "Nonexistent"}))
    sent = skill.bus.emit.call_args[0][0]
    assert sent.data["paragraphs"] == []


def test_handle_fetch_story_fetch_error_returns_empty(skill):
    skill.index = {"The Ugly Duckling": "http://x/duckling"}
    skill.get_story = MagicMock(side_effect=StoryFetchError("boom"))

    skill.handle_fetch_story(make_message({"story_id": "The Ugly Duckling"}))

    sent = skill.bus.emit.call_args[0][0]
    assert sent.data["paragraphs"] == []
