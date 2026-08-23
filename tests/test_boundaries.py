"""Boundary cases: empty, oversized, illegal, network, rate-limit, concurrency, unicode, ACL."""

from __future__ import annotations

import json
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

from video_script.constants import MAX_NAME_CHARS, MAX_POINT_CHARS, MAX_POINTS, MAX_TOTAL_INPUT_CHARS
from video_script.errors import (
    AccessDeniedError,
    EmptyInputError,
    InputError,
    InputTooLongError,
    NetworkError,
    RateLimitError,
)
from video_script.generator import generate
from video_script.io_util import read_text, write_output
from video_script.llm import HttpResponse, LLMClient, RateLimiter, urllib_post
from video_script.models import ProductBrief
from video_script.render import render_markdown
from video_script.textutil import sanitize_text
from video_script.validate import parse_brief


def test_boundary_empty_input() -> None:
    """1. Empty / missing required fields are rejected, never generate blanks."""
    for payload in (None, "", "   ", {}, {"name": "", "platform": "douyin", "points": ["x"]}):
        with pytest.raises(EmptyInputError):
            parse_brief(payload)
    with pytest.raises(EmptyInputError):
        parse_brief({"name": "A", "platform": "douyin", "selling_points": []})
    with pytest.raises(EmptyInputError):
        generate(ProductBrief(name="A", platform="douyin", selling_points=()))


def test_boundary_overlong_input() -> None:
    """2. Oversize name/points/payload raise; optional fields truncate with a warning."""
    with pytest.raises(InputTooLongError):
        parse_brief(
            {
                "name": "名" * (MAX_NAME_CHARS + 1),
                "platform": "douyin",
                "selling_points": ["快"],
            }
        )
    with pytest.raises(InputTooLongError):
        parse_brief(
            {
                "name": "A",
                "platform": "douyin",
                "selling_points": ["P" * (MAX_POINT_CHARS + 1)],
            }
        )
    too_many = [f"p{i}" for i in range(MAX_POINTS + 1)]
    with pytest.raises(InputTooLongError):
        parse_brief({"name": "A", "platform": "douyin", "selling_points": too_many})
    huge = {"name": "A", "platform": "douyin", "selling_points": ["快"], "description": "字" * (MAX_TOTAL_INPUT_CHARS)}
    with pytest.raises(InputTooLongError):
        parse_brief(huge)
    truncated = parse_brief(
        {
            "name": "A",
            "platform": "douyin",
            "selling_points": ["快"],
            "audience": "人" * 200,
        }
    )
    assert truncated.warnings
    assert len(truncated.audience) <= 80


def test_boundary_illegal_format() -> None:
    """3. Wrong JSON types, unknown platform, fractional duration."""
    with pytest.raises(InputError):
        parse_brief(["not", "an", "object"])
    with pytest.raises(InputError):
        parse_brief("{")
    with pytest.raises(InputError):
        parse_brief({"name": "A", "platform": "youtube", "selling_points": ["x"]})
    with pytest.raises(InputError):
        parse_brief({"name": 12, "platform": "douyin", "selling_points": ["x"]})
    with pytest.raises(InputError):
        parse_brief({"name": "A", "platform": "douyin", "selling_points": ["x"], "duration_sec": 12.5})
    with pytest.raises(InputError):
        parse_brief({"name": "A", "platform": "douyin", "selling_points": {"a": 1}})


def test_boundary_network_failure() -> None:
    """4. Unreachable LLM endpoint becomes NetworkError (no traceback leak to caller)."""
    with pytest.raises(NetworkError):
        urllib_post(
            "http://127.0.0.1:1/v1/chat/completions",
            {"Content-Type": "application/json"},
            b"{}",
            0.2,
        )

    def boom(url, headers, data, timeout):
        raise NetworkError("dns failed")

    client = LLMClient(
        api_key="k",
        post_fn=boom,
        max_retries=0,
        retry_backoff=0,
        limiter=RateLimiter(rate_per_sec=10, burst=5),
    )
    with pytest.raises(NetworkError):
        client.complete("hello")


def test_boundary_api_rate_limit() -> None:
    """5. Local token bucket and HTTP 429 both surface as RateLimitError."""
    limiter = RateLimiter(rate_per_sec=0, burst=1)
    limiter.acquire(wait=False)
    with pytest.raises(RateLimitError):
        limiter.acquire(wait=False)

    def always_429(url, headers, data, timeout):
        return HttpResponse(429, {"retry-after": "0"}, "slow")

    client = LLMClient(
        api_key="k",
        post_fn=always_429,
        max_retries=0,
        retry_backoff=0,
        limiter=RateLimiter(rate_per_sec=50, burst=10),
    )
    with pytest.raises(RateLimitError) as info:
        client.complete("x")
    assert info.value.retry_after == 0.0


def test_boundary_concurrency(brief: ProductBrief, tmp_path: Path) -> None:
    """6. Parallel generate/write calls stay isolated and complete."""

    def work(i: int):
        local = ProductBrief(
            name=f"{brief.name}{i}",
            platform=brief.platform,
            selling_points=brief.selling_points,
            audience=brief.audience,
            duration_sec=27,
        )
        result = generate(local)
        path = write_output(tmp_path / f"{i}.json", json.dumps(result.to_dict(), ensure_ascii=False))
        return result.versions[0].title, path.read_text(encoding="utf-8")

    with ThreadPoolExecutor(max_workers=8) as pool:
        rows = list(pool.map(work, range(8)))
    titles = {row[0] for row in rows}
    assert len(rows) == 8
    assert all("清润防晒霜" in row[1] for row in rows)
    assert len(titles) >= 1

    limiter = RateLimiter(rate_per_sec=80, burst=8)
    errors: list[Exception] = []

    def ping() -> None:
        try:
            limiter.acquire(wait=True, timeout=2.0)
        except Exception as exc:  # noqa: BLE001 - collect any racer
            errors.append(exc)

    threads = [threading.Thread(target=ping) for _ in range(8)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    assert errors == []


def test_boundary_special_characters(brief: ProductBrief) -> None:
    """7. Control chars, bidi, zero-width, and markdown metacharacters cannot break output."""
    dirty = "清\x00润\u202e防晒\u200b霜*_"
    assert sanitize_text(dirty) == "清润防晒霜*_"
    parsed = parse_brief(
        {
            "name": dirty,
            "platform": "douyin",
            "selling_points": ["<script>alert(1)</script>", "SPF50+"],
            "audience": "emoji🙂用户",
        }
    )
    assert "\x00" not in parsed.name
    assert "\u202e" not in parsed.name
    result = generate(parsed)
    md = render_markdown(result)
    assert "<script>" in md or "script" in md
    assert "\\*" in md
    assert "🙂" in md or "emoji" in md


def test_boundary_permission_denied(tmp_path: Path) -> None:
    """8. Unreadable/unwritable paths become AccessDeniedError, not raw OSError."""
    locked_dir = tmp_path / "locked"
    locked_dir.mkdir()
    locked_dir.chmod(0)
    try:
        with pytest.raises(AccessDeniedError):
            write_output(locked_dir / "out.md", "hi")
        secret = locked_dir / "secret.json"
        with pytest.raises(AccessDeniedError):
            read_text(secret)
    finally:
        locked_dir.chmod(0o700)

    file_locked = tmp_path / "file.md"
    file_locked.write_text("old", encoding="utf-8")
    file_locked.chmod(0)
    try:
        with pytest.raises(AccessDeniedError):
            write_output(file_locked, "new")
    finally:
        file_locked.chmod(0o644)
