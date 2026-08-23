"""Unit tests for the optional LLM client, JSON parser, and rate limiter."""

from __future__ import annotations

import json

import pytest

from video_script.errors import AccessDeniedError, ConfigError, NetworkError, RateLimitError
from video_script.llm import (
    HttpResponse,
    LLMClient,
    RateLimiter,
    apply_llm_enhancement,
    build_llm_prompt,
    parse_llm_json,
    parse_retry_after,
)
from video_script.generator import generate
from video_script.models import ProductBrief


def test_rate_limiter_allows_burst_then_blocks() -> None:
    limiter = RateLimiter(rate_per_sec=0.0, burst=1)
    limiter.acquire(wait=False)
    with pytest.raises(RateLimitError):
        limiter.acquire(wait=False)
    with pytest.raises(ConfigError):
        RateLimiter(rate_per_sec=1, burst=0)


def test_parse_llm_json_fenced_and_raw() -> None:
    assert parse_llm_json('{"a": 1}') == {"a": 1}
    fenced = "```json\n{\"b\": 2}\n```"
    assert parse_llm_json(fenced) == {"b": 2}
    mixed = "here you go {\"c\": 3} thanks"
    assert parse_llm_json(mixed) == {"c": 3}
    with pytest.raises(NetworkError):
        parse_llm_json("not json at all")
    with pytest.raises(NetworkError):
        parse_llm_json("   ")


def test_parse_retry_after() -> None:
    assert parse_retry_after({"retry-after": "1.5"}) == 1.5
    assert parse_retry_after({"Retry-After": "nope"}) is None
    assert parse_retry_after({}) is None


def test_llm_client_requires_key() -> None:
    client = LLMClient(api_key="")
    with pytest.raises(ConfigError):
        client.complete("hi")


def test_llm_client_http_statuses(brief: ProductBrief) -> None:
    calls = {"n": 0}

    def post_429(url, headers, data, timeout):
        calls["n"] += 1
        return HttpResponse(429, {"retry-after": "0"}, "slow down")

    client = LLMClient(
        api_key="k",
        post_fn=post_429,
        max_retries=0,
        retry_backoff=0,
        limiter=RateLimiter(rate_per_sec=10, burst=10),
    )
    with pytest.raises(RateLimitError) as exc:
        client.complete("p")
    assert exc.value.retry_after == 0.0

    def post_403(url, headers, data, timeout):
        return HttpResponse(403, {}, "nope")

    denied = LLMClient(api_key="k", post_fn=post_403, limiter=RateLimiter(10, 10), max_retries=0)
    with pytest.raises(AccessDeniedError):
        denied.complete("p")

    def post_500(url, headers, data, timeout):
        return HttpResponse(500, {}, "boom")

    server = LLMClient(
        api_key="k", post_fn=post_500, limiter=RateLimiter(10, 10), max_retries=0, retry_backoff=0
    )
    with pytest.raises(NetworkError):
        server.complete("p")

    def post_ok(url, headers, data, timeout):
        body = json.dumps({"choices": [{"message": {"content": '{"ok": true}'}}]})
        return HttpResponse(200, {}, body)

    ok = LLMClient(api_key="k", post_fn=post_ok, limiter=RateLimiter(10, 10))
    assert "ok" in ok.complete("p")


def test_llm_client_retries_network_then_succeeds() -> None:
    state = {"n": 0}

    def flaky(url, headers, data, timeout):
        state["n"] += 1
        if state["n"] == 1:
            raise NetworkError("down")
        body = json.dumps({"choices": [{"message": {"content": "hello"}}]})
        return HttpResponse(200, {}, body)

    client = LLMClient(
        api_key="k",
        post_fn=flaky,
        max_retries=1,
        retry_backoff=0,
        limiter=RateLimiter(10, 10),
    )
    assert client.complete("p") == "hello"
    assert state["n"] == 2


def test_apply_llm_enhancement_keeps_structure(brief: ProductBrief) -> None:
    result = generate(brief)

    class Dummy:
        def complete(self, prompt: str) -> str:
            payload = {
                "versions": [
                    {
                        "title": "改写标题",
                        "hook": {"spoken": "新开头", "visual": "新画面"},
                        "voiceover": "新口播",
                        "cta": "新CTA",
                    }
                    for _ in result.versions
                ]
            }
            return json.dumps(payload)

    updated = apply_llm_enhancement(Dummy(), brief, list(result.versions))  # type: ignore[arg-type]
    assert updated[0].title == "改写标题"
    assert updated[0].hook.spoken == "新开头"
    assert updated[0].storyboard == result.versions[0].storyboard

    class Junk:
        def complete(self, prompt: str) -> str:
            return "lol"

    kept = apply_llm_enhancement(Junk(), brief, list(result.versions))  # type: ignore[arg-type]
    assert kept[0].title == result.versions[0].title


def test_build_llm_prompt_contains_versions(brief: ProductBrief) -> None:
    result = generate(brief)
    prompt = build_llm_prompt(brief, list(result.versions))
    data = json.loads(prompt)
    assert len(data["versions"]) == 3
    assert data["product"]["name"] == brief.name
