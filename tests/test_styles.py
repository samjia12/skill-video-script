"""Unit tests for style role lists."""

from __future__ import annotations

import pytest

from video_script.errors import InputError
from video_script.styles import get_style, list_styles, shot_roles


def test_list_styles_is_three() -> None:
    styles = list_styles()
    assert len(styles) == 3
    assert [s.id for s in styles] == ["grass", "howto", "story"]
    assert get_style("howto").label == "干货教程"
    with pytest.raises(InputError):
        get_style("comedy")


def test_shot_roles_bookends() -> None:
    style = get_style("grass")
    roles = shot_roles(style, 9)
    assert roles[0] == "hook"
    assert roles[-1] == "cta"
    assert len(roles) == 9
    short = shot_roles(style, 3)
    assert short == ("hook", "pain", "cta") or (short[0] == "hook" and short[-1] == "cta")
    with pytest.raises(InputError):
        shot_roles(style, 2)
