"""
skill OVOS Andersen Tales
Copyright (C) 2026  Andreas Lorensen

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

---

Provider skill for ovos-skill-common-tales: implements the
ovos.common_tales.* bus protocol and registers NO intents of its own.
See https://github.com/andlo/ovos-skill-common-tales for the full
protocol, and why this skill has no standalone voice interface - it is
not meant to be used without the orchestrator installed.
"""

from ovos_workshop.skills import OVOSSkill
from ovos_utils.parse import match_one
from ovos_utils import classproperty
from ovos_utils.process_utils import RuntimeRequirements

import requests
from bs4 import BeautifulSoup
import time
import json
import random


class StoryFetchError(Exception):
    """Raised when a story/index page could not be fetched or parsed
    from andersenstories.com."""


# ovos.common_tales.* bus protocol - see ovos-skill-common-tales/README.md
COMMON_TALES_SEARCH = "ovos.common_tales.search"
COMMON_TALES_SEARCH_RESPONSE = "ovos.common_tales.search.response"
COMMON_TALES_FETCH_STORY = "ovos.common_tales.fetch_story"  # + ".{this_skill_id}"
COMMON_TALES_FETCH_STORY_RESPONSE = "ovos.common_tales.fetch_story.response"

# names a user might call this collection via 'collection_hint' - matched
# fuzzily against, not required to be exact
COLLECTION_ALIASES = ["andersen", "hans christian andersen", "h c andersen",
                       "h.c. andersen", "hans andersen", "hc andersen"]
COLLECTION_HINT_THRESHOLD = 0.85
AUTHOR_NAME = "Hans Christian Andersen"
COLLECTION_NAME = "Andersen's Fairy Tales"
SOURCE_NAME = "andersenstories.com"


class AndersenTales(OVOSSkill):

    INDEX_CACHE_TTL = 60 * 60 * 24 * 7  # 7 days

    @classproperty
    def runtime_requirements(self):
        return RuntimeRequirements(
            internet_before_load=True,
            network_before_load=True,
            requires_internet=True,
            requires_network=True,
            no_internet_fallback=True,
            no_network_fallback=True,
        )

    def initialize(self):
        self.index = {}
        # in-memory cache of already-fetched story text, keyed by URL
        self._story_text_cache = {}
        self.refresh_index()
        self.add_event(COMMON_TALES_SEARCH, self.handle_search)
        self.add_event(f"{COMMON_TALES_FETCH_STORY}.{self.skill_id}", self.handle_fetch_story)

    def _index_cache_filename(self):
        lang = self.lang.split("-")[0]
        return f"index_{lang}.json"

    def _read_index_cache(self):
        cache_file = self._index_cache_filename()
        if not self.file_system.exists(cache_file):
            return None
        try:
            with self.file_system.open(cache_file, "r") as f:
                return json.load(f)
        except (OSError, ValueError) as e:
            self.log.warning(f"could not read story index cache: {e}")
            return None

    def _write_index_cache(self):
        cache_file = self._index_cache_filename()
        try:
            with self.file_system.open(cache_file, "w") as f:
                json.dump({"timestamp": time.time(), "index": self.index}, f)
        except OSError as e:
            self.log.warning(f"could not write story index cache: {e}")

    def refresh_index(self, force=False):
        cached = self._read_index_cache()
        if not force and cached and (time.time() - cached.get("timestamp", 0)) < self.INDEX_CACHE_TTL:
            self.index = cached.get("index", {})
            return
        try:
            self.update_index()
            self._write_index_cache()
        except StoryFetchError as e:
            self.log.error(f"Could not refresh story index: {e}")
            if cached:
                self.log.warning("Falling back to previously cached (possibly stale) story index")
                self.index = cached.get("index", {})

    def get_soup(self, url):
        try:
            r = requests.get(url, timeout=10)
            r.raise_for_status()
            r.encoding = r.apparent_encoding
            return BeautifulSoup(r.text, "html.parser")
        except requests.RequestException as e:
            raise StoryFetchError(f"failed to fetch {url}: {e}") from e

    def get_story(self, url):
        if url in self._story_text_cache:
            return self._story_text_cache[url]
        soup = self.get_soup(url)
        elements = soup.find_all("div", {'itemprop': ['text']})
        if not elements:
            raise StoryFetchError(f"story text not found at {url}")
        text = elements[0].text.strip()
        self._story_text_cache[url] = text
        return text

    def get_title(self, url):
        soup = self.get_soup(url)
        elements = soup.find_all("h2", {'itemprop': ['name']})
        if not elements:
            raise StoryFetchError(f"title not found at {url}")
        return elements[0].text.strip()

    def get_index(self, url):
        soup = self.get_soup(url)
        lists = soup.find_all("ul", {'class': ['list_link']})
        if not lists:
            raise StoryFetchError(f"story index not found at {url}")
        index = {}
        for link in lists[0].find_all("a"):
            index[link.text] = link.get("href")
        return index

    def update_index(self):
        # andersenstories.com only offers these 7 languages - confirmed
        # against the site itself (see andlo/ovos-skill-fairytales#31)
        url_andersen = {'da': 'https://www.andersenstories.com/da/andersen_fortaellinger/',
                        'en': 'https://www.andersenstories.com/en/andersen_fairy-tales/',
                        'de': 'https://www.andersenstories.com/de/andersen_maerchen/',
                        'es': 'https://www.andersenstories.com/es/andersen_cuentos/',
                        'fr': 'https://www.andersenstories.com/fr/andersen_contes/',
                        'it': 'https://www.andersenstories.com/it/andersen_fiabe/',
                        'nl': 'https://www.andersenstories.com/nl/andersen_sprookjes/'}
        lang = self.lang.split("-")[0]
        if lang not in url_andersen:
            lang = "en"
        self.index = self.get_index(url_andersen[lang] + "list")

    def _matches_collection_hint(self, hint):
        if not hint:
            return True
        _, score = match_one(hint.lower(), COLLECTION_ALIASES)
        return score >= COLLECTION_HINT_THRESHOLD

    def handle_search(self, message):
        if not self.index:
            return
        collection_hint = message.data.get("collection_hint")
        if not self._matches_collection_hint(collection_hint):
            return  # this search isn't aimed at us - stay silent

        phrase = message.data.get("phrase")
        if phrase:
            title, confidence = match_one(phrase, list(self.index.keys()))
        elif collection_hint:
            # 'a story from Andersen' with no specific tale named -
            # only a sensible response if the hint was actually for us
            title = random.choice(list(self.index.keys()))
            confidence = 1.0
        else:
            return  # no phrase and no hint - nothing to go on

        self.bus.emit(message.reply(COMMON_TALES_SEARCH_RESPONSE, {
            "skill_id": self.skill_id,
            "story_id": title,
            "title": title,
            "author": AUTHOR_NAME,
            "collection": COLLECTION_NAME,
            "source": SOURCE_NAME,
            "confidence": confidence,
        }))

    def handle_fetch_story(self, message):
        story_id = message.data.get("story_id")
        url = self.index.get(story_id)
        if not url:
            self.bus.emit(message.reply(COMMON_TALES_FETCH_STORY_RESPONSE, {"paragraphs": []}))
            return
        try:
            text = self.get_story(url)
        except StoryFetchError as e:
            self.log.error(f"Could not fetch story '{story_id}': {e}")
            self.bus.emit(message.reply(COMMON_TALES_FETCH_STORY_RESPONSE, {"paragraphs": []}))
            return
        paragraphs = [p for p in text.split('\n\n') if p.strip()]
        self.bus.emit(message.reply(COMMON_TALES_FETCH_STORY_RESPONSE, {"paragraphs": paragraphs}))
