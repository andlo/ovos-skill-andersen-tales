# <img src='story-512.png' card_color='#40DBB0' width='50' height='50' style='vertical-align:bottom'/> Andersen Tales (provider)

A *provider* skill for [ovos-common-reading-pipeline-plugin](https://github.com/andlo/ovos-common-reading-pipeline-plugin),
delivering Hans Christian Andersen's fairy tales.

_"Life itself is the most wonderful fairy tale of all."_
— Hans Christian Andersen

[![Tests](https://github.com/andlo/ovos-skill-andersen-tales/actions/workflows/test.yml/badge.svg)](https://github.com/andlo/ovos-skill-andersen-tales/actions/workflows/test.yml)
[![PyPI version](https://img.shields.io/pypi/v/ovos-skill-andersen-tales.svg)](https://pypi.org/project/ovos-skill-andersen-tales/)

> **This skill has no standalone voice interface.** It registers no
> intents and never speaks. It only answers
> [ovos.common_reading.* bus messages](https://github.com/andlo/ovos-common-reading-pipeline-plugin#the-ovoscommon_reading-bus-protocol),
> so you also need **ovos-common-reading-pipeline-plugin** installed and
> added to your pipeline config for it to be useful at all.

## Install
```bash
pip install ovos-skill-andersen-tales ovos-common-reading-pipeline-plugin
```

## Languages

Sourced live from [andersenstories.com](https://www.andersenstories.com/),
which offers exactly 7 languages: EN, DA, DE, ES, FR, IT, NL.

**This provider does not translate.** It loads only for the languages
the installation is configured for - the device's own `lang` plus
`secondary_langs` in `mycroft.conf` - that it supports. If none of them
is one of the 7, it **never loads at all**: `initialize()` builds no
index, registers no bus events, and logs a clear message rather than
silently serving English (or any other) content.

For each configured, supported language it builds its own story index,
and each search is answered from the index of the language it was made
in: the pipeline plugin's `lang` field, else the language of the session
the search came from, else the device's own. A single device builds one
index, as before. A HiveMind hub serving users in several languages lists
them in `secondary_langs`:

```json
{
  "lang": "en-US",
  "secondary_langs": ["da-DK", "de-DE"]
}
```

A search in a language the installation doesn't serve gets no answer at
all. A search with no title ("tell me a story") gets a random story at
0.9, and titles match regardless of case.

**Author/collection name and collection_hint aliases are also
per-language**, not hardcoded English - a Danish device announces
"H.C. Andersen" / "H.C. Andersens Eventyr" instead of the English
"Hans Christian Andersen" / "Andersen's Fairy Tales". See
`locale/<lang>/collection.voc` (aliases) and
`locale/<lang>/collection_meta.json` (author/collection name), loaded
via OVOS's own resource file resolution rather than Python constants -
see [ovos-common-reading-pipeline-plugin#26](https://github.com/andlo/ovos-common-reading-pipeline-plugin/issues/26)
for the full reasoning. This also means every supported language has
its own `locale/<lang>/skill.json`, so the Skills Store can see this
provider genuinely supports 7 languages, not just English.

## Collection hints

Responds to `collection_hint` values in the *device's own language* -
e.g. "andersen"/"hans christian andersen" on English, "andersen"/"h.c.
andersen" on Danish - matched fuzzily against that language's own alias
list (see `locale/<lang>/collection.voc`).

## Content type

Always identifies as `content_type: "story"`. A search with a
`content_type` hint for anything else (e.g. "article", "poem") gets no
response from this provider.

## Credits

Content sourced from andersenstories.com. Scraping/caching logic ported
from [ovos-skill-fairytales](https://github.com/andlo/ovos-skill-fairytales).

## Category
**Entertainment**

## Tags
#stories #fairytales #andersen #provider
