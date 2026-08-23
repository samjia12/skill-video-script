"""Parse and reject illegal product briefs before generation."""

from __future__ import annotations

import json
import re
from typing import Any

from .constants import (
    DEFAULT_LANGUAGE,
    MAX_AUDIENCE_CHARS,
    MAX_BRAND_CHARS,
    MAX_CATEGORY_CHARS,
    MAX_DESCRIPTION_CHARS,
    MAX_DURATION_SEC,
    MAX_NAME_CHARS,
    MAX_POINT_CHARS,
    MAX_POINTS,
    MAX_PRICE_CHARS,
    MAX_TOTAL_INPUT_CHARS,
    MIN_DURATION_SEC,
    MIN_POINTS,
    SUPPORTED_LANGUAGES,
)
from .errors import EmptyInputError, InputError, InputTooLongError
from .models import ProductBrief
from .platforms import normalize_platform
from .textutil import sanitize_text, total_payload_chars

_POINT_SPLIT_RE = re.compile(r"[,，;；\n|]+")


def parse_selling_points(raw: object) -> list[str]:
    """Accept a list, a comma/Chinese-comma/newline string, or a JSON array string."""
    if raw is None:
        raise EmptyInputError("selling_points is required")
    if isinstance(raw, (list, tuple)):
        items = [str(item) for item in raw]
    elif isinstance(raw, str):
        stripped = raw.strip()
        if not stripped:
            raise EmptyInputError("selling_points is required")
        if stripped[:1] in "{[":
            try:
                decoded = json.loads(stripped)
            except json.JSONDecodeError as exc:
                raise InputError(f"selling_points is not valid JSON: {exc.msg}") from exc
            if not isinstance(decoded, list):
                raise InputError("selling_points JSON must be an array of strings")
            items = [str(item) for item in decoded]
        else:
            items = [part for part in _POINT_SPLIT_RE.split(stripped) if part.strip()]
    else:
        raise InputError("selling_points must be a string or a list of strings")
    return items


def _optional_text(raw: object, field: str, max_chars: int) -> tuple[str, tuple[str, ...]]:
    if raw is None:
        return "", ()
    if not isinstance(raw, str):
        raise InputError(f"{field} must be a string")
    text = sanitize_text(raw)
    if len(text) <= max_chars:
        return text, ()
    return text[:max_chars].rstrip(), (f"{field} truncated to {max_chars} characters",)


def _parse_duration(raw: object) -> int | None:
    if raw is None or raw == "":
        return None
    if isinstance(raw, bool):
        raise InputError("duration_sec must be an integer")
    if isinstance(raw, int):
        value = raw
    elif isinstance(raw, float):
        if not raw.is_integer():
            raise InputError("duration_sec must be a whole number of seconds")
        value = int(raw)
    elif isinstance(raw, str):
        stripped = sanitize_text(raw)
        if not stripped:
            return None
        if not re.fullmatch(r"[0-9]+", stripped):
            raise InputError("duration_sec must be an integer")
        value = int(stripped)
    else:
        raise InputError("duration_sec must be an integer")
    if value < MIN_DURATION_SEC or value > MAX_DURATION_SEC:
        raise InputError(
            f"duration_sec must be between {MIN_DURATION_SEC} and {MAX_DURATION_SEC}"
        )
    return value


def _parse_language(raw: object) -> str:
    if raw is None or raw == "":
        return DEFAULT_LANGUAGE
    if not isinstance(raw, str):
        raise InputError("language must be a string")
    lang = sanitize_text(raw).casefold()
    aliases = {"zh-cn": "zh", "zh_cn": "zh", "cn": "zh", "chinese": "zh", "en-us": "en", "english": "en"}
    lang = aliases.get(lang, lang)
    if lang not in SUPPORTED_LANGUAGES:
        raise InputError(f"language must be one of: {', '.join(SUPPORTED_LANGUAGES)}")
    return lang


def _first_present(payload: dict[str, Any], keys: tuple[str, ...]) -> object:
    for key in keys:
        if key in payload and payload[key] is not None:
            return payload[key]
    return None


def parse_brief(payload: object) -> ProductBrief:
    """Validate a mapping (or JSON string) into a ProductBrief."""
    if payload is None:
        raise EmptyInputError("input is required")
    if isinstance(payload, str):
        stripped = payload.strip()
        if not stripped:
            raise EmptyInputError("input is required")
        try:
            payload = json.loads(stripped)
        except json.JSONDecodeError as exc:
            raise InputError(f"input is not valid JSON: {exc.msg}") from exc
    if not isinstance(payload, dict):
        raise InputError("input must be a JSON object / dict")
    if not payload:
        raise EmptyInputError("input is required")
    if total_payload_chars(payload) > MAX_TOTAL_INPUT_CHARS:
        raise InputTooLongError(
            f"input exceeds {MAX_TOTAL_INPUT_CHARS} characters"
        )

    warnings: list[str] = []
    name_raw = _first_present(payload, ("name", "product_name", "product"))
    if name_raw is None:
        raise EmptyInputError("product name is required")
    if not isinstance(name_raw, str):
        raise InputError("product name must be a string")
    name = sanitize_text(name_raw)
    if not name:
        raise EmptyInputError("product name is required")
    if len(name) > MAX_NAME_CHARS:
        raise InputTooLongError(
            f"product name must be at most {MAX_NAME_CHARS} characters"
        )

    platform = normalize_platform(_first_present(payload, ("platform", "target_platform", "channel")))

    raw_points = parse_selling_points(
        _first_present(payload, ("selling_points", "points", "sellingPoints"))
    )
    points: list[str] = []
    seen: set[str] = set()
    for item in raw_points:
        point = sanitize_text(item)
        if not point:
            continue
        if len(point) > MAX_POINT_CHARS:
            raise InputTooLongError(
                f"each selling point must be at most {MAX_POINT_CHARS} characters"
            )
        key = point.casefold()
        if key in seen:
            continue
        seen.add(key)
        points.append(point)
    if len(points) < MIN_POINTS:
        raise EmptyInputError("at least one selling point is required")
    if len(points) > MAX_POINTS:
        raise InputTooLongError(f"at most {MAX_POINTS} selling points are allowed")

    audience, extra = _optional_text(
        _first_present(payload, ("audience", "target_audience")), "audience", MAX_AUDIENCE_CHARS
    )
    warnings.extend(extra)
    category, extra = _optional_text(
        _first_present(payload, ("category",)), "category", MAX_CATEGORY_CHARS
    )
    warnings.extend(extra)
    price, extra = _optional_text(_first_present(payload, ("price",)), "price", MAX_PRICE_CHARS)
    warnings.extend(extra)
    brand, extra = _optional_text(_first_present(payload, ("brand",)), "brand", MAX_BRAND_CHARS)
    warnings.extend(extra)
    description, extra = _optional_text(
        _first_present(payload, ("description", "extra", "notes")),
        "description",
        MAX_DESCRIPTION_CHARS,
    )
    warnings.extend(extra)

    duration = _parse_duration(_first_present(payload, ("duration_sec", "duration")))
    language = _parse_language(_first_present(payload, ("language", "lang")))

    return ProductBrief(
        name=name,
        platform=platform,
        selling_points=tuple(points),
        audience=audience,
        category=category,
        price=price,
        brand=brand,
        description=description,
        duration_sec=duration,
        language=language,
        warnings=tuple(warnings),
    )
