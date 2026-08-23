"""Unit tests for BGM suggestions."""

from __future__ import annotations

from video_script.bgm import suggest_bgm
from video_script.models import ProductBrief
from video_script.platforms import get_platform
from video_script.styles import get_style


def test_suggest_bgm_uses_library_and_keywords(brief: ProductBrief) -> None:
    bgm = suggest_bgm(brief, get_platform("douyin"), get_style("grass"))
    assert "抖音" in bgm.ducking
    assert bgm.search_keywords
    assert bgm.tempo_bpm
    assert bgm.avoid


def test_suggest_bgm_differs_by_style(brief: ProductBrief) -> None:
    platform = get_platform("bilibili")
    a = suggest_bgm(brief, platform, get_style("howto"))
    b = suggest_bgm(brief, platform, get_style("story"))
    assert a.mood != b.mood
