"""Unit tests for voiceover assembly."""

from __future__ import annotations

from video_script.models import Shot
from video_script.platforms import get_platform
from video_script.voiceover import build_voiceover, fit_voiceover, format_timecode, plain_voiceover


def _shot(i: int, start: float, end: float, text: str) -> Shot:
    return Shot(
        index=i,
        start_sec=start,
        end_sec=end,
        role="hook" if i == 1 else "cta",
        visual="v",
        voiceover=text,
        on_screen_text="s",
        camera="c",
        notes="n",
    )


def test_format_timecode() -> None:
    assert format_timecode(0) == "0:00.0"
    assert format_timecode(3) == "0:03.0"
    assert format_timecode(75.5).startswith("1:")
    assert format_timecode(-1) == "0:00.0"


def test_build_and_plain_voiceover() -> None:
    shots = (_shot(1, 0, 3, "开头"), _shot(2, 3, 6, "结尾"))
    timed = build_voiceover(shots)
    assert "[0:00.0-0:03.0] 开头" in timed
    assert "结尾" in timed
    assert plain_voiceover(shots) == "开头\n结尾"
    assert build_voiceover(()) == ""


def test_fit_voiceover_caps_length() -> None:
    platform = get_platform("douyin")
    long_text = "口播内容。" * 80
    fitted = fit_voiceover(long_text, 10, platform)
    assert len(fitted) <= int(10 * platform.chars_per_sec) + 1
