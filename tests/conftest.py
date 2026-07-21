"""Shared pytest fixtures for the andersen-tales skill test suite."""
import importlib.util
from pathlib import Path
from unittest.mock import MagicMock

import pytest

_INIT_PATH = Path(__file__).resolve().parents[1] / "__init__.py"
_spec = importlib.util.spec_from_file_location("andersen_tales_skill", _INIT_PATH)
_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_module)

AndersenTales = _module.AndersenTales
StoryFetchError = _module.StoryFetchError
COMMON_TALES_SEARCH_RESPONSE = _module.COMMON_TALES_SEARCH_RESPONSE
COMMON_TALES_FETCH_STORY_RESPONSE = _module.COMMON_TALES_FETCH_STORY_RESPONSE


class FakeFileSystem:
    def __init__(self, base):
        self.base = base
        self.path = str(base)

    def exists(self, name):
        return (self.base / name).exists()

    def open(self, name, mode="r"):
        return open(self.base / name, mode)


@pytest.fixture
def skill(tmp_path, monkeypatch):
    s = AndersenTales.__new__(AndersenTales)
    s.log = MagicMock()
    s.skill_id = "ovos-skill-andersen-tales.test"
    s.status = MagicMock()
    s._bus = MagicMock()
    s._settings = {}
    monkeypatch.setattr(AndersenTales, "lang", "en-us", raising=False)
    s.file_system = FakeFileSystem(tmp_path)
    s.index = {}
    s._story_text_cache = {}
    return s
