"""The headline of a channel-keyed price must describe every channel.

A channel-keyed ``list_price`` carries a per-channel price plus a top-level
``description``. That top-level string is the **only** thing the catalog row
renders — the frontend's ``PriceTag`` reads ``price.description`` and falls back
to the *default channel's* description when it is absent. So when the channels
differ in price, a headline that names one of them tells the reader something
false about the service.

This was live: every ``qwencloud/*`` service paired a free ``byok`` channel with
a paid ``managed`` one, and the headline read ``$0.288/$2.3 / 1M input/output
tokens``. A reader scanning the catalog saw a priced service with no hint that
it could be used for nothing.

**Why the check splits on ``|`` first.** That same headline *did* contain the
word "free" — in the terminal note, ``| Free on the byok channel - …``. Notes
are not rendered in the row header. A substring search over the whole
description would therefore have passed the exact string this rule exists to
reject, which is the trap worth encoding rather than rediscovering.
"""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any

__all__ = ["check_channel_price_headline"]

# The marketplace description grammar (unitysvc/unitysvc#1886) is
# ``<amount> [/ <unit>] [~badge]* [| <note>]``. Only the part before the note
# reaches the catalog row's amount+unit line.
_NOTE_SEP = "|"


def _headline(description: Any) -> str:
    """The part of a description the catalog row actually shows."""
    if not isinstance(description, str):
        return ""
    return description.split(_NOTE_SEP, 1)[0].strip()


def _is_zero(value: Any) -> bool:
    try:
        return Decimal(str(value)) == 0
    except (InvalidOperation, TypeError, ValueError):
        return False


def _is_free(channel: Any) -> bool | None:
    """True/False when a channel's price is knowable, None when it is not.

    ``None`` keeps an unparseable channel from being silently counted as paid,
    which would let a genuinely-mixed price through the free/paid check.
    """
    if not isinstance(channel, dict):
        return None
    if "price" in channel or "amount" in channel:
        return _is_zero(channel.get("price", channel.get("amount")))
    if "input" in channel and "output" in channel:
        return _is_zero(channel["input"]) and _is_zero(channel["output"])
    return None


def check_channel_price_headline(price: Any, *, field: str = "list_price") -> list[str]:
    """Errors for a channel-keyed price whose headline hides a channel.

    Returns an empty list for anything that is not a multi-channel price, or
    whose channels all cost the same — a single shared rate is fully described
    by naming it once.
    """
    if not isinstance(price, dict) or price.get("type") != "channel":
        return []
    channels = price.get("channels")
    if not isinstance(channels, dict) or len(channels) < 2:
        return []

    headline = _headline(price.get("description"))
    freeness = {name: _is_free(ch) for name, ch in channels.items()}
    free = sorted(n for n, f in freeness.items() if f is True)
    paid = sorted(n for n, f in freeness.items() if f is False)

    # Distinct per-channel headlines, as the reader would see them in the
    # channels section. Two channels quoting the same rate are not "differing".
    per_channel = {
        name: _headline(ch.get("description")) if isinstance(ch, dict) else "" for name, ch in channels.items()
    }
    distinct = {h for h in per_channel.values() if h}

    mixed = bool(free and paid)
    if not mixed and len(distinct) < 2:
        return []

    errors: list[str] = []
    if not headline:
        errors.append(
            f"{field}: channels {', '.join(sorted(channels))} differ in price but the "
            f"price has no top-level 'description'. The catalog row falls back to the "
            f"'{price.get('default')}' channel and shows that one rate as if it were "
            f"the whole service."
        )
        return errors

    if mixed and "free" not in headline.lower() and not _is_zero(price.get("price")):
        errors.append(
            f"{field}: {', '.join(free)} is free and {', '.join(paid)} is not, but the "
            f"headline {headline!r} names only a paid rate. Lead with the range, e.g. "
            f"'Free - {headline}'. (A 'free' mention AFTER '|' does not count — notes "
            f"are not rendered in the catalog row.)"
        )
        return errors

    # The general case: the headline reproduces one channel verbatim while
    # another quotes something different.
    named = sorted(n for n, h in per_channel.items() if h and h == headline)
    if named and len(distinct) > 1:
        others = sorted(set(channels) - set(named))
        errors.append(
            f"{field}: headline {headline!r} is exactly the '{named[0]}' channel's price, "
            f"but {', '.join(others)} differ. The headline must represent the range across "
            f"channels, not one of them."
        )
    return errors
