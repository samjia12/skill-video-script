"""Unit tests for platform aliases and duration clamping."""

from __future__ import annotations

import pytest

from video_script.errors import EmptyInputError, InputError
from video_script.platforms import clamp_duration, get_platform, normalize_platform


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("抖音", "douyin"),
        ("douyin", "douyin"),
        ("TikTok", "douyin"),
        ("视频号", "wechat"),
        ("WeChat Channels", "wechat"),
        ("B站", "bilibili"),
        ("哔哩哔哩", "bilibili"),
        ("bili", "bilibili"),
    ],
)
def test_normalize_platform_aliases(raw: str, expected: str) -> None:
    assert normalize_platform(raw) == expected


def test_normalize_platform_rejects_unknown_and_empty() -> None:
    with pytest.raises(InputError):
        normalize_platform("youtube")
    with pytest.raises(EmptyInputError):
        normalize_platform("  ")
    with pytest.raises(EmptyInputError):
        normalize_platform(None)
    with pytest.raises(InputError):
        normalize_platform(1)


def test_get_platform_and_clamp() -> None:
    spec = get_platform("douyin")
    assert spec.label == "抖音"
    duration, warnings = clamp_duration(None, spec)
    assert duration == spec.default_duration
    assert warnings == ()
    low, low_w = clamp_duration(8, spec)
    assert low == spec.min_duration
    assert low_w
    high, high_w = clamp_duration(120, spec)
    assert high == spec.max_duration
    assert high_w
    with pytest.raises(InputError):
        get_platform("youtube")
