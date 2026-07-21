# <img src='story-512.png' card_color='#40DBB0' width='50' height='50' style='vertical-align:bottom'/> Andersen Tales (provider)

A *provider* skill for [ovos-skill-common-tales](https://github.com/andlo/ovos-skill-common-tales),
delivering Hans Christian Andersen's fairy tales.

_"Life itself is the most wonderful fairy tale of all."_
— Hans Christian Andersen

[![Tests](https://github.com/andlo/ovos-skill-andersen-tales/actions/workflows/test.yml/badge.svg)](https://github.com/andlo/ovos-skill-andersen-tales/actions/workflows/test.yml)
[![PyPI version](https://img.shields.io/pypi/v/ovos-skill-andersen-tales.svg)](https://pypi.org/project/ovos-skill-andersen-tales/)

> **This skill has no standalone voice interface.** It registers no
> intents and never speaks. It only answers
> [ovos.common_tales.* bus messages](https://github.com/andlo/ovos-skill-common-tales#the-ovoscommon_tales-bus-protocol),
> so you also need **ovos-skill-common-tales** installed for it to be
> useful at all.

## Install
```bash
pip install ovos-skill-andersen-tales ovos-skill-common-tales
```

## Languages

Sourced live from [andersenstories.com](https://www.andersenstories.com/),
which offers exactly 7 languages: EN, DA, DE, ES, FR, IT, NL. Falls back to
English for any other device language.

## Collection hints

Responds to `collection_hint` values like "andersen", "hans christian
andersen", "h c andersen", "h.c. andersen", matched fuzzily (see
`COLLECTION_ALIASES` in `__init__.py`).

## Credits

Content sourced from andersenstories.com. Scraping/caching logic ported
from [ovos-skill-fairytales](https://github.com/andlo/ovos-skill-fairytales).

## Category
**Entertainment**

## Tags
#stories #fairytales #andersen #provider
