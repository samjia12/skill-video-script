"""Unit tests for timeline allocation and storyboard assembly."""

from __future__ import annotations

import pytest

from video_script.errors import InputError
from video_script.hook import build_hook
from video_script.models import ProductBrief
from video_script.platforms import get_platform
from video_script.storyboard import allocate_timeline, build_storyboard, round2
from video_script.styles import get_style, shot_roles


def test_allocate_timeline_contiguous_and_covers_duration() -> None:
    times = allocate_timeline(27, 7, hook_sec=3.0)
    assert times[0][0] == 0.0
    assert times[-1][1] == 27.0
    for prev, cur in zip(times, times[1:]):
        assert round2(prev[1]) == round2(cur[0])
    assert abs((times[0][1] - times[0][0]) - 3.0) <= 0.3
    with pytest.raises(InputError):
        allocate_timeline(20, 2)
    with pytest.raises(InputError):
        allocate_timeline(0, 5)


def test_build_storyboard_roles_and_product_name(brief: ProductBrief) -> None:
    platform = get_platform(brief.platform)
    style = get_style("howto")
    roles = shot_roles(style, platform.shot_count)
    timeline = allocate_timeline(27, len(roles), hook_sec=platform.hook_sec)
    hook = build_hook(brief, platform, style)
    shots = build_storyboard(brief, platform, style, timeline, roles, hook)
    assert len(shots) == len(roles)
    assert shots[0].role == "hook"
    assert shots[-1].role == "cta"
    joined = "".join(s.voiceover for s in shots)
    assert brief.name in joined
    assert shots[0].voiceover == hook.spoken
