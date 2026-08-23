"""Unit tests for Markdown and JSON rendering."""

from __future__ import annotations

import json

from video_script.generator import generate
from video_script.models import ProductBrief
from video_script.render import render_json, render_markdown


def test_render_json_roundtrip_keys(brief: ProductBrief) -> None:
    result = generate(brief)
    payload = json.loads(render_json(result))
    assert payload["platform"] == "douyin"
    assert len(payload["versions"]) == 3
    assert payload["versions"][0]["hook"]["spoken"]
    assert payload["versions"][0]["storyboard"][0]["voiceover"]


def test_render_markdown_has_required_sections(brief: ProductBrief) -> None:
    result = generate(brief)
    md = render_markdown(result)
    assert "黄金 3 秒" in md
    assert "分镜表" in md
    assert "口播稿" in md
    assert "BGM" in md
    assert "字幕建议" in md
    assert "种草安利" in md
    assert "干货教程" in md
    assert "剧情反转" in md
    assert brief.name in md


def test_render_markdown_escapes_product_name() -> None:
    brief = ProductBrief(
        name="A*B_C",
        platform="douyin",
        selling_points=("快",),
    )
    md = render_markdown(generate(brief))
    assert "A\\*B\\_C" in md or "A\\*" in md
