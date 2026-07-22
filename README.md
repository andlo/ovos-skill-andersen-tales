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

**This provider does not translate.** On any other device language, it
doesn't just decline to answer searches - it **never loads at all**:
`initialize()` checks the device's language against `SUPPORTED_LANGUAGES`
before building any index or registering any bus events, and logs a
clear message if the language isn't supported, rather than silently
serving English (or any other) content. Set your device to one of the 7
supported languages to use this provider.

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
