"""Timeline allocation and storyboard assembly."""

from __future__ import annotations

from .copy_bank import SHOT_CAMERA, SHOT_VISUAL, SHOT_VO
from .errors import InputError
from .models import GoldenHook, ProductBrief, Shot
from .platforms import PlatformSpec
from .styles import StyleSpec
from .textutil import fill_template, pick_template, spoken_char_budget, trim_to_chars


def round2(value: float) -> float:
    return round(float(value), 2)


def allocate_timeline(
    duration: float,
    n_shots: int,
    hook_sec: float = 3.0,
) -> list[tuple[float, float]]:
    """Return contiguous [start, end] pairs covering exactly ``duration`` seconds."""
    if n_shots < 3:
        raise InputError("need at least 3 shots")
    if duration <= 0:
        raise InputError("duration must be positive")
    duration = round2(duration)
    # Keep the opening close to 3s but never starve the CTA.
    hook = min(hook_sec, round2(duration * 0.22), duration - 2.0)
    hook = round2(max(2.0, hook)) if duration >= 12 else round2(duration / n_shots)
    cta = round2(min(5.0, max(2.5, duration * 0.12)))
    if hook + cta >= duration:
        hook = round2(max(1.5, duration * 0.2))
        cta = round2(max(1.5, duration * 0.15))
    middle_total = round2(duration - hook - cta)
    mid_n = n_shots - 2
    if mid_n < 1:
        raise InputError("need at least 3 shots")
    base = round2(middle_total / mid_n)
    spans = [hook] + [base] * mid_n + [cta]
    # Rounding each span to 0.01s can drift the sum; dump the residual into the last middle shot.
    diff = round2(duration - round2(sum(spans)))
    spans[-2] = round2(spans[-2] + diff)
    times: list[tuple[float, float]] = []
    cursor = 0.0
    for span in spans:
        start = round2(cursor)
        end = round2(cursor + span)
        times.append((start, end))
        cursor = end
    times[-1] = (times[-1][0], duration)
    if times[0][0] != 0.0:
        raise InputError("internal: timeline must start at 0")
    return times


def _slots_with_hook(brief: ProductBrief, hook: GoldenHook) -> dict[str, str]:
    slots = brief.slot_map()
    slots["hook_line"] = hook.spoken
    extra = brief.description or brief.lead_point
    slots["description_or_point"] = extra
    return slots


def build_storyboard(
    brief: ProductBrief,
    platform: PlatformSpec,
    style: StyleSpec,
    timeline: list[tuple[float, float]],
    roles: tuple[str, ...],
    hook: GoldenHook,
) -> tuple[Shot, ...]:
    if len(timeline) != len(roles):
        raise InputError("timeline and roles length mismatch")
    slots = _slots_with_hook(brief, hook)
    shots: list[Shot] = []
    for index, ((start, end), role) in enumerate(zip(timeline, roles), start=1):
        duration = round2(end - start)
        if role == "hook":
            spoken = hook.spoken
            visual = hook.visual
            on_screen = hook.on_screen_text
            camera = SHOT_CAMERA["hook"]
            notes = "黄金 3 秒：必须完成停滑/停手，产品或冲突至少出现一个。"
        else:
            pool = SHOT_VO.get(role) or SHOT_VO["detail"]
            seed = f"{brief.name}|{style.id}|{role}|{index}"
            spoken = fill_template(pick_template(pool, seed), slots)
            budget = spoken_char_budget(duration, platform.chars_per_sec)
            spoken = trim_to_chars(spoken, budget)
            visual = fill_template(SHOT_VISUAL.get(role, SHOT_VISUAL["detail"]), slots)
            on_screen = trim_to_chars(
                spoken[: platform.subtitle_max_chars_per_line * 2],
                platform.subtitle_max_chars_per_line,
            )
            camera = SHOT_CAMERA.get(role, "中景")
            notes = f"角色 {role}；口播不超过 {budget} 字。"
        shots.append(
            Shot(
                index=index,
                start_sec=start,
                end_sec=end,
                role=role,
                visual=visual,
                voiceover=spoken,
                on_screen_text=on_screen,
                camera=camera,
                notes=notes,
            )
        )
    return tuple(shots)
