"""Golden 3-second opening builder."""

from __future__ import annotations

from .copy_bank import HOOK_SCREEN, HOOK_SPOKEN, HOOK_VISUAL, TECHNIQUE_LABELS
from .constants import HOOK_TARGET_SEC
from .errors import InputError
from .models import GoldenHook, ProductBrief
from .platforms import PlatformSpec
from .styles import StyleSpec
from .textutil import fill_template, looks_incomplete, pick_template, trim_to_chars


def _spoken_for_budget(templates: tuple[str, ...], slots: dict[str, str], seed: str, budget: int) -> str:
    """Pick a line that actually fits the 3-second speaking budget.

    Prefer a complete template over a trimmed fragment of a longer one.
    """
    filled = [fill_template(template, slots) for template in templates]
    fitting = [line for line in filled if len(line) <= budget]
    if fitting:
        seeded = fill_template(pick_template(templates, seed), slots)
        if seeded in fitting:
            return seeded
        return fitting[0]
    filled.sort(key=len)
    for candidate in filled:
        trimmed = trim_to_chars(candidate, budget)
        if trimmed and not looks_incomplete(trimmed):
            return trimmed
    return trim_to_chars(filled[0], budget) or filled[0][:budget]


def build_hook(brief: ProductBrief, platform: PlatformSpec, style: StyleSpec) -> GoldenHook:
    """Create a platform-aware opening that fits the 3-second window."""
    key = (platform.id, style.id)
    spoken_pool = HOOK_SPOKEN.get(key)
    if not spoken_pool:
        raise InputError(f"no hook templates for {platform.id}/{style.id}")
    slots = brief.slot_map()
    seed = f"{brief.name}|{platform.id}|{style.id}|hook"
    visual = fill_template(pick_template(HOOK_VISUAL[style.id], seed + "|v"), slots)
    on_screen = fill_template(pick_template(HOOK_SCREEN[style.id], seed + "|s"), slots)
    duration = min(HOOK_TARGET_SEC, platform.hook_sec)
    # Hooks are delivered faster than the rest of the VO; allow a denser line.
    budget = max(12, int(duration * platform.chars_per_sec * 1.35))
    spoken = _spoken_for_budget(spoken_pool, slots, seed, budget)
    technique = style.hook_bias
    return GoldenHook(
        spoken=spoken,
        visual=visual,
        technique=technique,
        technique_label=TECHNIQUE_LABELS.get(technique, technique),
        duration_sec=round(duration, 2),
        on_screen_text=trim_to_chars(on_screen, platform.subtitle_max_chars_per_line),
    )
