"""The three mandatory script styles shipped with the skill."""

from __future__ import annotations

from dataclasses import dataclass

from .errors import InputError


@dataclass(frozen=True)
class StyleSpec:
    id: str
    label: str
    summary: str
    hook_bias: str
    voice: str
    roles: tuple[str, ...]


GRASS = StyleSpec(
    id="grass",
    label="种草安利",
    summary="第一人称体验，感官细节，制造「我也想试试」的冲动。",
    hook_bias="result_first",
    voice="像朋友掏出压箱底私藏，语速轻快，少术语。",
    roles=("hook", "pain", "reveal", "closeup", "proof", "lifestyle", "cta"),
)

HOWTO = StyleSpec(
    id="howto",
    label="干货教程",
    summary="价值前置，步骤拆解，看完能照做。",
    hook_bias="curiosity_gap",
    voice="口播像目录：先给结论，再给 2～3 个可执行要点。",
    roles=("hook", "promise", "tip1", "tip2", "tip3", "recap", "cta"),
)

STORY = StyleSpec(
    id="story",
    label="剧情反转",
    summary="冲突开场，中段反转，产品作为解决方案出现。",
    hook_bias="pattern_interrupt",
    voice="先演戏后讲理，反转后节奏上扬。",
    roles=("hook", "setup", "conflict", "twist", "solution", "result", "cta"),
)

STYLES: tuple[StyleSpec, ...] = (GRASS, HOWTO, STORY)
STYLES_BY_ID = {style.id: style for style in STYLES}


def list_styles() -> tuple[StyleSpec, ...]:
    return STYLES


def get_style(style_id: str) -> StyleSpec:
    if style_id not in STYLES_BY_ID:
        raise InputError(f"unknown style {style_id!r}")
    return STYLES_BY_ID[style_id]


def shot_roles(style: StyleSpec, shot_count: int) -> tuple[str, ...]:
    """Stretch or trim the style's role list to match the platform shot count."""
    if shot_count < 3:
        raise InputError("shot count must be at least 3")
    base = list(style.roles)
    # Always bookend with hook / cta.
    if base[0] != "hook":
        base.insert(0, "hook")
    if base[-1] != "cta":
        base.append("cta")
    extras = ("detail", "demo", "reaction", "compare")
    idx = 0
    while len(base) < shot_count:
        insert_at = max(1, len(base) - 1)
        base.insert(insert_at, extras[idx % len(extras)])
        idx += 1
    if len(base) > shot_count:
        # Drop from the middle, never the hook or CTA.
        while len(base) > shot_count and len(base) > 3:
            del base[-2]
    base[0] = "hook"
    base[-1] = "cta"
    return tuple(base)
