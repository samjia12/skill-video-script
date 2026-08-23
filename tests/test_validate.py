"""Unit tests for brief parsing and validation."""

from __future__ import annotations

import pytest

from video_script.errors import EmptyInputError, InputError, InputTooLongError
from video_script.validate import parse_brief, parse_selling_points


def test_parse_selling_points_list_and_csv() -> None:
    assert parse_selling_points([" a ", "b"]) == [" a ", "b"]
    assert parse_selling_points("清爽,不黏腻，SPF50+") == ["清爽", "不黏腻", "SPF50+"]
    assert parse_selling_points('["x", "y"]') == ["x", "y"]


def test_parse_selling_points_rejects_empty_and_bad_json() -> None:
    with pytest.raises(EmptyInputError):
        parse_selling_points(None)
    with pytest.raises(EmptyInputError):
        parse_selling_points("  ")
    with pytest.raises(InputError):
        parse_selling_points("[not-json")
    with pytest.raises(InputError):
        parse_selling_points('{"a": 1}')
    with pytest.raises(InputError):
        parse_selling_points(12)


def test_parse_brief_happy_path() -> None:
    brief = parse_brief(
        {
            "name": "清润防晒霜",
            "platform": "抖音",
            "selling_points": "清爽不黏腻,SPF50+",
            "audience": "学生",
            "price": "79元",
        }
    )
    assert brief.platform == "douyin"
    assert brief.name == "清润防晒霜"
    assert brief.selling_points[0] == "清爽不黏腻"
    assert brief.lead_point == "清爽不黏腻"


def test_parse_brief_from_json_string() -> None:
    brief = parse_brief(
        '{"name":"A","platform":"wechat","selling_points":["快"]}'
    )
    assert brief.platform == "wechat"


def test_parse_brief_aliases() -> None:
    brief = parse_brief(
        {
            "product_name": "胶囊咖啡机",
            "target_platform": "视频号",
            "points": ["30秒出杯", "占地小"],
        }
    )
    assert brief.name == "胶囊咖啡机"
    assert brief.platform == "wechat"


def test_parse_brief_dedupes_points() -> None:
    brief = parse_brief(
        {"name": "A", "platform": "bilibili", "selling_points": ["热插拔", "热插拔", "卫星轴"]}
    )
    assert brief.selling_points == ("热插拔", "卫星轴")


def test_parse_brief_duration_and_language() -> None:
    brief = parse_brief(
        {"name": "A", "platform": "douyin", "points": ["x"], "duration": "30", "language": "zh-cn"}
    )
    assert brief.duration_sec == 30
    assert brief.language == "zh"
    with pytest.raises(InputError):
        parse_brief({"name": "A", "platform": "douyin", "points": ["x"], "duration": "abc"})
    with pytest.raises(InputError):
        parse_brief({"name": "A", "platform": "douyin", "points": ["x"], "duration_sec": True})
    with pytest.raises(InputError):
        parse_brief({"name": "A", "platform": "douyin", "points": ["x"], "language": "fr"})
