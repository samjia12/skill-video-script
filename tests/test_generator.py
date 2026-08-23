"""Unit tests for the generator orchestrator."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from video_script.errors import ConfigError, InputError
from video_script.generator import build_version, generate
from video_script.models import ProductBrief, ScriptVersion
from video_script.platforms import get_platform
from video_script.styles import get_style


def test_generate_three_distinct_versions(brief: ProductBrief) -> None:
    result = generate(brief, now=datetime(2026, 8, 23, tzinfo=timezone.utc))
    assert len(result.versions) == 3
    assert [v.style_id for v in result.versions] == ["grass", "howto", "story"]
    assert result.engine == "template"
    assert result.platform_label == "抖音"
    names_in_vo = all(brief.name in v.voiceover for v in result.versions)
    assert names_in_vo
    for version in result.versions:
        _assert_version_shape(version, brief.name)


def _assert_version_shape(version: ScriptVersion, name: str) -> None:
    assert version.hook.spoken
    assert version.storyboard
    assert version.storyboard[0].role == "hook"
    assert version.storyboard[-1].role == "cta"
    assert abs(version.hook.duration_sec - 3.0) <= 1.0
    assert version.bgm.search_keywords
    assert version.subtitle.max_chars_per_line >= 8
    assert version.voiceover
    assert name in version.voiceover or name in version.title


def test_generate_is_deterministic(brief: ProductBrief) -> None:
    a = generate(brief, now=datetime(2026, 1, 1, tzinfo=timezone.utc))
    b = generate(brief, now=datetime(2026, 1, 1, tzinfo=timezone.utc))
    assert a.versions == b.versions


def test_generate_clamps_duration_with_warning(brief: ProductBrief) -> None:
    short = ProductBrief(
        name=brief.name,
        platform="douyin",
        selling_points=brief.selling_points,
        duration_sec=10,
    )
    result = generate(short)
    assert result.versions[0].duration_sec == float(get_platform("douyin").min_duration)
    assert result.warnings


def test_generate_rejects_bad_backend(brief: ProductBrief) -> None:
    with pytest.raises(InputError):
        generate(brief, backend="magic")
    with pytest.raises(ConfigError):
        generate(brief, backend="llm")


def test_generate_llm_enhancer(brief: ProductBrief) -> None:
    def enhancer(_brief: ProductBrief, versions: list[ScriptVersion]) -> list[ScriptVersion]:
        first = versions[0]
        patched = ScriptVersion(
            style_id=first.style_id,
            style_label=first.style_label,
            title="LLM标题",
            cover_text=first.cover_text,
            duration_sec=first.duration_sec,
            hook=first.hook,
            storyboard=first.storyboard,
            voiceover=first.voiceover,
            bgm=first.bgm,
            subtitle=first.subtitle,
            hashtags=first.hashtags,
            cta=first.cta,
        )
        return [patched, versions[1], versions[2]]

    result = generate(brief, backend="llm", enhancer=enhancer)
    assert result.engine == "llm"
    assert result.versions[0].title == "LLM标题"

    def bad(_b: ProductBrief, versions: list[ScriptVersion]) -> list[ScriptVersion]:
        return versions[:1]

    with pytest.raises(InputError):
        generate(brief, backend="llm", enhancer=bad)


def test_build_version_direct(brief: ProductBrief) -> None:
    version = build_version(brief, get_platform("wechat"), get_style("story"), 36)
    assert version.style_id == "story"
    assert version.duration_sec == 36
