"""A channel-keyed price's headline must describe every channel.

Vectors are the real strings from the catalog: the qwencloud shape that was
live and wrong, and the labs/qqpush-relay shape that was live and right.
"""

from __future__ import annotations

from unitysvc_sellers.price_headline import check_channel_price_headline

# What every qwencloud/* service published: a free byok channel beside a paid
# managed one, headlined with only the paid rate. The free mention sits in the
# terminal note, which the catalog row does not render.
QWENCLOUD_BAD = {
    "type": "channel",
    "default": "managed",
    "description": (
        "$0.288/$2.3 / 1M input/output tokens | Free on the byok channel - "
        "bring your own QwenCloud key and pay QwenCloud directly."
    ),
    "channels": {
        "byok": {"description": "Free — bring your own key", "price": "0", "type": "constant"},
        "managed": {
            "description": "$0.288/$2.3 / 1M input/output tokens",
            "input": "0.288",
            "output": "2.3",
            "type": "one_million_tokens",
        },
    },
}

# labs/qqpush-relay, which renders "Free - $0.001 / message" correctly.
QQPUSH_GOOD = {
    "type": "channel",
    "default": "byok",
    "description": "Free - $0.001 / message",
    "price": "0.001",
    "channels": {
        "byok": {"description": "Free — relay to your own webhook", "price": "0", "type": "constant"},
        "plus": {"description": "$0.001 per message", "price": "0.001", "type": "constant"},
    },
}


def test_the_shape_that_was_live_and_wrong_is_rejected() -> None:
    (error,) = check_channel_price_headline(QWENCLOUD_BAD)
    assert "byok is free" in error
    assert "managed is not" in error


def test_a_free_mention_after_the_pipe_does_not_satisfy_the_rule() -> None:
    """The trap this check exists for.

    QWENCLOUD_BAD's description contains the word "Free" — in the note. Notes
    are not rendered in the catalog row, so a substring search over the whole
    description would pass the exact string the rule rejects.
    """
    assert "Free" in QWENCLOUD_BAD["description"]  # type: ignore[operator]
    assert check_channel_price_headline(QWENCLOUD_BAD)


def test_the_shape_that_is_live_and_right_passes() -> None:
    assert check_channel_price_headline(QQPUSH_GOOD) == []


def test_leading_with_free_fixes_it() -> None:
    fixed = {**QWENCLOUD_BAD, "description": "Free - " + str(QWENCLOUD_BAD["description"])}
    assert check_channel_price_headline(fixed) == []


def test_a_missing_headline_is_rejected() -> None:
    """The row falls back to the default channel and shows one rate as the whole."""
    no_desc = {**QWENCLOUD_BAD}
    del no_desc["description"]
    (error,) = check_channel_price_headline(no_desc)
    assert "no top-level 'description'" in error


def test_a_headline_copied_from_one_channel_is_rejected_even_when_all_are_paid() -> None:
    """The general rule, beyond the free/paid case."""
    price = {
        "type": "channel",
        "default": "standard",
        "description": "$1 / 1M tokens",
        "channels": {
            "standard": {"description": "$1 / 1M tokens", "price": "1", "type": "one_million_tokens"},
            "premium": {"description": "$5 / 1M tokens", "price": "5", "type": "one_million_tokens"},
        },
    }
    (error,) = check_channel_price_headline(price)
    assert "must represent the range" in error


def test_channels_that_all_cost_the_same_need_no_range() -> None:
    price = {
        "type": "channel",
        "default": "a",
        "description": "$1 / 1M tokens",
        "channels": {
            "a": {"description": "$1 / 1M tokens", "price": "1", "type": "one_million_tokens"},
            "b": {"description": "$1 / 1M tokens", "price": "1", "type": "one_million_tokens"},
        },
    }
    assert check_channel_price_headline(price) == []


def test_all_free_channels_need_no_range() -> None:
    price = {
        "type": "channel",
        "default": "a",
        "description": "Free",
        "channels": {
            "a": {"description": "Free", "price": "0", "type": "constant"},
            "b": {"description": "Free", "price": "0", "type": "constant"},
        },
    }
    assert check_channel_price_headline(price) == []


def test_non_channel_prices_are_not_this_rule_s_business() -> None:
    assert check_channel_price_headline({"type": "one_million_tokens", "input": "1", "output": "2"}) == []
    assert check_channel_price_headline({"type": "channel", "channels": {"only": {"price": "1"}}}) == []
    assert check_channel_price_headline(None) == []
    assert check_channel_price_headline("not a price") == []


def test_an_unparseable_channel_price_does_not_read_as_paid() -> None:
    """Otherwise a free+unknown pair would be reported as a free/paid mix."""
    price = {
        "type": "channel",
        "default": "a",
        "description": "Free",
        "channels": {
            "a": {"description": "Free", "price": "0", "type": "constant"},
            "b": {"description": "Free", "type": "weird"},
        },
    }
    assert check_channel_price_headline(price) == []


def test_the_field_name_is_reported_so_the_seller_can_find_it() -> None:
    (error,) = check_channel_price_headline(QWENCLOUD_BAD, field="promotion_price")
    assert error.startswith("promotion_price:")
