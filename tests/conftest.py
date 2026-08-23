"""Shared fixtures."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from video_script.models import ProductBrief  # noqa: E402


@pytest.fixture
def brief() -> ProductBrief:
    return ProductBrief(
        name="清润防晒霜",
        platform="douyin",
        selling_points=("清爽不黏腻", "SPF50+", "学生党价格"),
        audience="通勤学生和上班族",
        category="美妆防晒",
        price="79元",
        brand="晴川",
        description="通勤出门前30秒能涂完。",
        duration_sec=27,
        language="zh",
    )


@pytest.fixture
def wechat_brief(brief: ProductBrief) -> ProductBrief:
    return ProductBrief(
        name=brief.name,
        platform="wechat",
        selling_points=brief.selling_points,
        audience=brief.audience,
        category=brief.category,
        price=brief.price,
        brand=brief.brand,
        description=brief.description,
        duration_sec=36,
        language="zh",
    )


@pytest.fixture
def bili_brief(brief: ProductBrief) -> ProductBrief:
    return ProductBrief(
        name="星核机械键盘套件",
        platform="bilibili",
        selling_points=("热插拔", "卫星轴不晃", "空格不响"),
        audience="客制化入门党",
        category="外设",
        price="499元",
        brand="星核",
        description="第一次组键盘也不劝退。",
        duration_sec=60,
        language="zh",
    )
