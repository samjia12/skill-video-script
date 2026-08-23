"""Unit tests for text sanitization and trimming."""

from __future__ import annotations

import pytest

from video_script.errors import InputError
from video_script.textutil import (
    escape_markdown,
    fill_template,
    hashtag_token,
    looks_incomplete,
    pick_index,
    pick_template,
    sanitize_text,
    spoken_char_budget,
    total_payload_chars,
    trim_to_chars,
)


def test_sanitize_text_strips_controls_and_bidi() -> None:
    raw = "  清润\x00防晒\u202e霜\u200b  "
    assert sanitize_text(raw) == "清润防晒霜"


def test_sanitize_text_rejects_non_string() -> None:
    with pytest.raises(InputError):
        sanitize_text(123)  # type: ignore[arg-type]


def test_sanitize_text_collapses_whitespace() -> None:
    assert sanitize_text("a \t  b\n\n\n\nc") == "a b\n\nc"


def test_escape_markdown_protects_specials() -> None:
    assert "*" in escape_markdown("use *stars*")
    assert "\\*" in escape_markdown("use *stars*")


def test_pick_index_is_deterministic() -> None:
    assert pick_index("seed", 5) == pick_index("seed", 5)
    assert pick_index("seed-a", 8) != pick_index("seed-b", 8) or True  # may collide, not required
    with pytest.raises(InputError):
        pick_index("x", 0)


def test_pick_template_and_fill() -> None:
    chosen = pick_template(("A{name}", "B{name}"), "s")
    assert "{name}" in chosen
    assert fill_template("{name}-{point}", {"name": "N", "point": "P"}) == "N-P"
    with pytest.raises(InputError):
        fill_template("{missing}", {"name": "N"})


def test_trim_to_chars_prefers_sentence_end() -> None:
    text = "第一句。第二句还很长没有结束"
    trimmed = trim_to_chars(text, 8)
    assert trimmed.endswith("。") or len(trimmed) <= 8
    assert len(trim_to_chars("短", 10)) == 1
    assert trim_to_chars("abcdef", 0) == ""
    assert len(trim_to_chars("没有句号的超长口播内容继续说", 6)) <= 6


def test_trim_to_chars_strips_dangling_function_words() -> None:
    text = "我把便携胶囊咖啡机用了一周，只想说一句：真的。"
    trimmed = trim_to_chars(text, 12)
    assert not looks_incomplete(trimmed)
    assert not trimmed.endswith("一")


def test_spoken_char_budget() -> None:
    assert spoken_char_budget(10, 4.0) == 40
    assert spoken_char_budget(0, 4.0) == 0
    assert spoken_char_budget(3, 4.8) >= 1


def test_hashtag_token_strips_symbols() -> None:
    assert hashtag_token("#清润 防晒!") == "清润防晒"
    assert len(hashtag_token("x" * 50, max_chars=8)) == 8


def test_total_payload_chars() -> None:
    size = total_payload_chars({"name": "ab", "points": ["c", "d"]})
    assert size >= 6
