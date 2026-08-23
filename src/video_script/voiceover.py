"""Assemble a teleprompter-ready voiceover from storyboard shots."""

from __future__ import annotations

from .models import Shot
from .platforms import PlatformSpec
from .textutil import spoken_char_budget, trim_to_chars


def format_timecode(seconds: float) -> str:
    """Format seconds as M:SS.s for the timed script."""
    if seconds < 0:
        seconds = 0.0
    minutes = int(seconds // 60)
    rest = seconds - minutes * 60
    return f"{minutes}:{rest:04.1f}"


def build_voiceover(shots: tuple[Shot, ...] | list[Shot]) -> str:
    """Join shot lines with timecodes so the host can read against the cut."""
    if not shots:
        return ""
    lines: list[str] = []
    for shot in shots:
        start = format_timecode(shot.start_sec)
        end = format_timecode(shot.end_sec)
        text = shot.voiceover.strip()
        if not text:
            continue
        lines.append(f"[{start}-{end}] {text}")
    return "\n".join(lines)


def plain_voiceover(shots: tuple[Shot, ...] | list[Shot]) -> str:
    return "\n".join(shot.voiceover.strip() for shot in shots if shot.voiceover.strip())


def fit_voiceover(text: str, duration_sec: float, platform: PlatformSpec) -> str:
    """Hard-cap a whole-script voiceover to the platform speaking rate."""
    budget = spoken_char_budget(duration_sec, platform.chars_per_sec)
    # Timecodes are not spoken; only trim the concatenated plain text when needed.
    return trim_to_chars(text, max(budget, 1))
