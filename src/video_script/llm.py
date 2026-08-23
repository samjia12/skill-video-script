"""Optional OpenAI-compatible LLM backend with retries and rate limiting."""

from __future__ import annotations

import json
import os
import socket
import threading
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, replace
from typing import Any, Callable, Mapping

from .errors import AccessDeniedError, ConfigError, NetworkError, RateLimitError
from .models import ProductBrief, ScriptVersion

DEFAULT_BASE_URL = "https://api.openai.com/v1"
DEFAULT_MODEL = "gpt-4o-mini"
DEFAULT_TIMEOUT = 20.0
DEFAULT_RETRIES = 2


@dataclass
class HttpResponse:
    status: int
    headers: Mapping[str, str]
    body: str


PostFn = Callable[[str, dict[str, str], bytes, float], HttpResponse]


class RateLimiter:
    """Thread-safe token bucket. ``rate_per_sec`` tokens refill continuously."""

    def __init__(self, rate_per_sec: float, burst: int = 1) -> None:
        if rate_per_sec < 0:
            raise ConfigError("rate_per_sec must be >= 0")
        if burst < 1:
            raise ConfigError("burst must be >= 1")
        self.rate_per_sec = float(rate_per_sec)
        self.burst = int(burst)
        self._tokens = float(burst)
        self._updated = time.monotonic()
        self._lock = threading.Lock()

    def acquire(self, *, wait: bool = True, timeout: float = 2.0) -> None:
        deadline = time.monotonic() + max(0.0, timeout)
        while True:
            with self._lock:
                self._refill()
                if self._tokens >= 1.0:
                    self._tokens -= 1.0
                    return
                deficit = 1.0 - self._tokens
                if self.rate_per_sec <= 0:
                    raise RateLimitError("rate limit exceeded", retry_after=None)
                sleep_for = deficit / self.rate_per_sec
            if not wait:
                raise RateLimitError("rate limit exceeded", retry_after=sleep_for)
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise RateLimitError("rate limit exceeded", retry_after=sleep_for)
            time.sleep(min(sleep_for, remaining, 0.05))

    def _refill(self) -> None:
        now = time.monotonic()
        elapsed = now - self._updated
        self._updated = now
        if self.rate_per_sec > 0:
            self._tokens = min(self.burst, self._tokens + elapsed * self.rate_per_sec)


def urllib_post(url: str, headers: dict[str, str], data: bytes, timeout: float) -> HttpResponse:
    request = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            header_map = {k.lower(): v for k, v in resp.headers.items()}
            return HttpResponse(status=getattr(resp, "status", 200), headers=header_map, body=body)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        header_map = {k.lower(): v for k, v in exc.headers.items()} if exc.headers else {}
        return HttpResponse(status=exc.code, headers=header_map, body=body)
    except socket.timeout as exc:
        raise NetworkError(f"LLM request timed out after {timeout}s") from exc
    except urllib.error.URLError as exc:
        raise NetworkError(f"LLM network error: {exc.reason}") from exc
    except OSError as exc:
        raise NetworkError(f"LLM network error: {exc}") from exc


def parse_retry_after(headers: Mapping[str, str]) -> float | None:
    raw = headers.get("retry-after") or headers.get("Retry-After")
    if not raw:
        return None
    try:
        return max(0.0, float(raw))
    except (TypeError, ValueError):
        return None


def parse_llm_json(text: str) -> Any:
    """Extract a JSON value from a model response, including fenced blocks."""
    stripped = text.strip()
    if not stripped:
        raise NetworkError("LLM returned an empty body")
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        inner = "\n".join(lines[1:])
        if inner.rstrip().endswith("```"):
            inner = inner.rstrip()[:-3]
        stripped = inner.strip()
        if stripped.startswith("json"):
            stripped = stripped[4:].lstrip()
    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        start = stripped.find("{")
        end = stripped.rfind("}")
        if start >= 0 and end > start:
            try:
                return json.loads(stripped[start : end + 1])
            except json.JSONDecodeError as exc:
                raise NetworkError(f"LLM returned invalid JSON: {exc.msg}") from exc
        raise NetworkError("LLM returned invalid JSON")


class LLMClient:
    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_RETRIES,
        retry_backoff: float = 0.4,
        limiter: RateLimiter | None = None,
        post_fn: PostFn | None = None,
    ) -> None:
        self.api_key = api_key if api_key is not None else os.environ.get("VIDEO_SCRIPT_API_KEY", "")
        self.base_url = (base_url or os.environ.get("VIDEO_SCRIPT_API_BASE") or DEFAULT_BASE_URL).rstrip("/")
        self.model = model or os.environ.get("VIDEO_SCRIPT_MODEL") or DEFAULT_MODEL
        self.timeout = float(os.environ.get("VIDEO_SCRIPT_TIMEOUT", timeout))
        self.max_retries = max_retries
        self.retry_backoff = retry_backoff
        self.limiter = limiter or RateLimiter(rate_per_sec=2.0, burst=2)
        self.post_fn = post_fn or urllib_post

    def require_ready(self) -> None:
        if not self.api_key:
            raise ConfigError("VIDEO_SCRIPT_API_KEY is required for --backend llm")

    def complete(self, prompt: str) -> str:
        self.require_ready()
        self.limiter.acquire(wait=True, timeout=max(0.5, self.timeout))
        url = self.base_url + "/chat/completions"
        payload = {
            "model": self.model,
            "temperature": 0.7,
            "messages": [
                {
                    "role": "system",
                    "content": "You rewrite short-video scripts. Return JSON only.",
                },
                {"role": "user", "content": prompt},
            ],
        }
        data = json.dumps(payload).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        last_error: Exception | None = None
        for attempt in range(self.max_retries + 1):
            try:
                response = self.post_fn(url, headers, data, self.timeout)
            except NetworkError as exc:
                last_error = exc
                if attempt >= self.max_retries:
                    raise
                time.sleep(self.retry_backoff * (2 ** attempt))
                continue
            if response.status == 401 or response.status == 403:
                raise AccessDeniedError(f"LLM provider rejected credentials (HTTP {response.status})")
            if response.status == 429:
                retry_after = parse_retry_after(response.headers)
                if attempt >= self.max_retries:
                    raise RateLimitError(
                        "LLM provider rate-limited the request (HTTP 429)",
                        retry_after=retry_after,
                    )
                time.sleep(retry_after if retry_after is not None else self.retry_backoff * (2 ** attempt))
                continue
            if response.status >= 500:
                last_error = NetworkError(f"LLM provider error HTTP {response.status}")
                if attempt >= self.max_retries:
                    raise last_error
                time.sleep(self.retry_backoff * (2 ** attempt))
                continue
            if response.status >= 400:
                raise NetworkError(f"LLM request failed HTTP {response.status}: {response.body[:240]}")
            parsed = parse_llm_json(response.body)
            return _extract_message_text(parsed)
        raise last_error or NetworkError("LLM request failed")


def _extract_message_text(parsed: Any) -> str:
    if isinstance(parsed, dict):
        choices = parsed.get("choices")
        if isinstance(choices, list) and choices:
            message = choices[0].get("message") if isinstance(choices[0], dict) else None
            if isinstance(message, dict) and isinstance(message.get("content"), str):
                return message["content"]
        if isinstance(parsed.get("content"), str):
            return parsed["content"]
    if isinstance(parsed, str):
        return parsed
    return json.dumps(parsed, ensure_ascii=False)


def build_llm_prompt(brief: ProductBrief, versions: list[ScriptVersion]) -> str:
    payload = {
        "instruction": (
            "Rewrite each of the 3 script versions to feel more natural while "
            "KEEPING: 3 versions, same style_id values, a ~3s hook, storyboard "
            "timings, bgm, subtitle, hashtags, and cta. Return a JSON object "
            "{\"versions\": [...]} matching the input shape."
        ),
        "product": {
            "name": brief.name,
            "platform": brief.platform,
            "selling_points": list(brief.selling_points),
        },
        "versions": [version.to_dict() for version in versions],
    }
    return json.dumps(payload, ensure_ascii=False)


def apply_llm_enhancement(
    client: LLMClient,
    brief: ProductBrief,
    versions: list[ScriptVersion],
) -> list[ScriptVersion]:
    """Best-effort rewrite. On unusable JSON, keep the template versions."""
    prompt = build_llm_prompt(brief, versions)
    raw = client.complete(prompt)
    try:
        parsed = parse_llm_json(raw)
    except NetworkError:
        return versions
    incoming = parsed.get("versions") if isinstance(parsed, dict) else None
    if not isinstance(incoming, list) or len(incoming) != len(versions):
        return versions
    # Structural rewrite of spoken/visual fields only; timings stay authoritative.
    updated: list[ScriptVersion] = []
    for original, blob in zip(versions, incoming):
        if not isinstance(blob, dict):
            updated.append(original)
            continue
        hook_blob = blob.get("hook") if isinstance(blob.get("hook"), dict) else {}
        spoken = hook_blob.get("spoken") if isinstance(hook_blob.get("spoken"), str) else original.hook.spoken
        visual = hook_blob.get("visual") if isinstance(hook_blob.get("visual"), str) else original.hook.visual
        new_hook = replace(
            original.hook,
            spoken=spoken.strip() or original.hook.spoken,
            visual=visual.strip() or original.hook.visual,
        )
        voiceover = blob.get("voiceover") if isinstance(blob.get("voiceover"), str) else original.voiceover
        cta = blob.get("cta") if isinstance(blob.get("cta"), str) else original.cta
        title = blob.get("title") if isinstance(blob.get("title"), str) else original.title
        updated.append(
            replace(
                original,
                title=title.strip() or original.title,
                hook=new_hook,
                voiceover=voiceover.strip() or original.voiceover,
                cta=cta.strip() or original.cta,
            )
        )
    return updated


def make_enhancer(client: LLMClient):
    def _enhance(brief: ProductBrief, versions: list[ScriptVersion]) -> list[ScriptVersion]:
        return apply_llm_enhancement(client, brief, versions)

    return _enhance
