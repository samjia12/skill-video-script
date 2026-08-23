"""Unit tests for subtitles, hashtags, and CTA."""

from __future__ import annotations

from video_script.models import ProductBrief
from video_script.platforms import get_platform
from video_script.styles import get_style
from video_script.subtitle import build_cta, make_hashtags, suggest_subtitle


def test_suggest_subtitle_platform_rules(brief: ProductBrief) -> None:
    sub = suggest_subtitle(brief, get_platform("douyin"), get_style("grass"))
    assert sub.max_chars_per_line == 11
    assert brief.name in sub.keywords
    assert sub.highlight_color.startswith("#")


def test_make_hashtags_and_cta(brief: ProductBrief, bili_brief: ProductBrief) -> None:
    tags = make_hashtags(brief, get_platform("douyin"))
    assert tags
    assert all(tag.startswith("#") for tag in tags)
    assert any(brief.name.replace(" ", "") in tag or "种草" in tag for tag in tags)
    bili_tags = make_hashtags(bili_brief, get_platform("bilibili"))
    assert any("测评" in tag or "开箱" in tag for tag in bili_tags)
    cta = build_cta(brief, get_platform("douyin"))
    assert cta
