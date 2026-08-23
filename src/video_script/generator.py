"""Orchestrate three style variants from a validated brief."""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
from typing import Callable

from .bgm import suggest_bgm
from .constants import STYLE_COUNT
from .copy_bank import COVERS, TITLES
from .errors import ConfigError, EmptyInputError, InputError
from .hook import build_hook
from .models import GenerationResult, ProductBrief, ScriptVersion
from .platforms import PlatformSpec, clamp_duration, get_platform
from .storyboard import allocate_timeline, build_storyboard
from .styles import StyleSpec, list_styles, shot_roles
from .subtitle import build_cta, make_hashtags, suggest_subtitle
from .textutil import fill_template, pick_template
from .voiceover import build_voiceover


def _build_title(brief: ProductBrief, style: StyleSpec) -> str:
    seed = f"{brief.name}|{style.id}|title"
    return fill_template(pick_template(TITLES[style.id], seed), brief.slot_map())


def _build_cover(brief: ProductBrief, style: StyleSpec, platform: PlatformSpec) -> str:
    seed = f"{brief.name}|{style.id}|cover"
    text = fill_template(pick_template(COVERS[style.id], seed), brief.slot_map())
    return text[: platform.subtitle_max_chars_per_line]


def build_version(
    brief: ProductBrief,
    platform: PlatformSpec,
    style: StyleSpec,
    duration: int,
) -> ScriptVersion:
    roles = shot_roles(style, platform.shot_count)
    timeline = allocate_timeline(duration, len(roles), hook_sec=platform.hook_sec)
    hook = build_hook(brief, platform, style)
    hook_span = round(timeline[0][1] - timeline[0][0], 2)
    if abs(hook.duration_sec - hook_span) > 0.01:
        hook = replace(hook, duration_sec=hook_span)
    storyboard = build_storyboard(brief, platform, style, timeline, roles, hook)
    return ScriptVersion(
        style_id=style.id,
        style_label=style.label,
        title=_build_title(brief, style),
        cover_text=_build_cover(brief, style, platform),
        duration_sec=float(duration),
        hook=hook,
        storyboard=storyboard,
        voiceover=build_voiceover(storyboard),
        bgm=suggest_bgm(brief, platform, style),
        subtitle=suggest_subtitle(brief, platform, style),
        hashtags=make_hashtags(brief, platform),
        cta=build_cta(brief, platform),
    )


def generate(
    brief: ProductBrief,
    *,
    backend: str = "template",
    enhancer: Callable[[ProductBrief, list[ScriptVersion]], list[ScriptVersion]] | None = None,
    now: datetime | None = None,
) -> GenerationResult:
    """Generate exactly three style variants. ``backend`` is ``template`` or ``llm``."""
    if backend not in {"template", "llm"}:
        raise InputError("backend must be 'template' or 'llm'")
    if brief is None:
        raise EmptyInputError("input is required")
    if not getattr(brief, "name", "").strip():
        raise EmptyInputError("product name is required")
    if not getattr(brief, "selling_points", ()):
        raise EmptyInputError("at least one selling point is required")
    platform = get_platform(brief.platform)
    duration, duration_warnings = clamp_duration(brief.duration_sec, platform)
    styles = list_styles()
    if len(styles) != STYLE_COUNT:
        raise InputError(f"internal: expected {STYLE_COUNT} styles")
    versions = [build_version(brief, platform, style, duration) for style in styles]
    warnings = list(brief.warnings) + list(duration_warnings)
    engine = "template"
    if backend == "llm":
        if enhancer is None:
            raise ConfigError("LLM backend requested but no enhancer is configured")
        versions = list(enhancer(brief, versions))
        engine = "llm"
        if len(versions) != STYLE_COUNT:
            raise InputError("LLM enhancer must return exactly 3 versions")
    stamp = (now or datetime.now(timezone.utc)).isoformat()
    return GenerationResult(
        product=brief,
        platform=platform.id,
        platform_label=platform.label,
        engine=engine,
        versions=tuple(versions),
        warnings=tuple(warnings),
        generated_at=stamp,
    )
