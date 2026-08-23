"""Unit tests for the golden 3-second hook."""

from __future__ import annotations

from video_script.hook import build_hook
from video_script.models import ProductBrief
from video_script.platforms import get_platform
from video_script.styles import get_style
from video_script.textutil import looks_incomplete


def test_build_hook_contains_product_and_fits_window(brief: ProductBrief) -> None:
    hook = build_hook(brief, get_platform("douyin"), get_style("grass"))
    assert brief.name in hook.spoken or brief.lead_point in hook.spoken or "先别" in hook.spoken
    assert 2.0 <= hook.duration_sec <= 3.0
    assert hook.visual
    assert hook.technique_label
    assert hook.on_screen_text


def test_build_hook_avoids_dangling_phrase(wechat_brief: ProductBrief) -> None:
    for style_id in ("grass", "howto", "story"):
        hook = build_hook(wechat_brief, get_platform("wechat"), get_style(style_id))
        assert hook.spoken
        assert not looks_incomplete(hook.spoken)


def test_build_hook_differs_by_style(brief: ProductBrief) -> None:
    platform = get_platform("douyin")
    a = build_hook(brief, platform, get_style("grass"))
    b = build_hook(brief, platform, get_style("story"))
    assert a.spoken != b.spoken
    assert a.technique != b.technique or a.visual != b.visual
