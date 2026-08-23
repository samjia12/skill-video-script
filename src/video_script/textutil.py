"""Sanitize untrusted input and keep spoken copy inside duration budgets."""

from __future__ import annotations

import re
import unicodedata
import zlib
from typing import Sequence

from .errors import InputError

_CONTROL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
_BIDI_RE = re.compile(r"[\u202a-\u202e\u2066-\u2069]")
_ZERO_WIDTH_RE = re.compile(r"[\u200b\u200c\u200d\u2060\ufeff]")
_SPACE_RE = re.compile(r"[ \t\f\r]+")
_NEWLINE_RE = re.compile(r"\n{3,}")
_SENTENCE_END_RE = re.compile(r"[。！？!?；;]")
_INCOMPLETE_ENDINGS = tuple("的了着把被让和与及在用一这那从给到")
_MD_ESCAPE_RE = re.compile(r"([\\`*_{}\[\]()#+\-.!|>~])")
_HASHTAG_UNSAFE_RE = re.compile(r"[^\w\u4e00-\u9fff]+", re.UNICODE)


def sanitize_text(value: str) -> str:
    """Strip control chars, bidi overrides, and zero-width glyphs, then NFC-normalize."""
    if not isinstance(value, str):
        raise InputError("text value must be a string")
    text = unicodedata.normalize("NFC", value)
    text = _CONTROL_RE.sub("", text)
    text = _BIDI_RE.sub("", text)
    text = _ZERO_WIDTH_RE.sub("", text)
    text = _SPACE_RE.sub(" ", text)
    text = _NEWLINE_RE.sub("\n\n", text)
    return text.strip()


def escape_markdown(text: str) -> str:
    """Escape characters that would break Markdown rendering of user-supplied names."""
    return _MD_ESCAPE_RE.sub(r"\\\1", text)


def pick_index(seed: str, size: int) -> int:
    """Deterministic index so the same brief always yields the same variant."""
    if size <= 0:
        raise InputError("internal: empty template list")
    return zlib.crc32(seed.encode("utf-8")) % size


def pick_template(templates: Sequence[str], seed: str) -> str:
    return templates[pick_index(seed, len(templates))]


def fill_template(template: str, slots: dict[str, str]) -> str:
    try:
        return template.format(**slots)
    except KeyError as exc:
        raise InputError(f"template missing slot {exc}") from exc


def looks_incomplete(text: str) -> bool:
    """True when a trimmed line likely ends mid-phrase (e.g. 「用了一」)."""
    stripped = text.strip()
    if not stripped:
        return True
    last = stripped[-1]
    if last in "。！？!?；;…":
        return False
    if stripped.endswith(("——", "...", "…")):
        return False
    return last in _INCOMPLETE_ENDINGS


def trim_to_chars(text: str, max_chars: int) -> str:
    """Trim spoken copy to a character budget, preferring sentence boundaries."""
    text = sanitize_text(text)
    if max_chars < 1:
        return ""
    if len(text) <= max_chars:
        return text
    chunk = text[:max_chars]
    ends = [match.end() for match in _SENTENCE_END_RE.finditer(chunk)]
    if ends:
        # A short complete sentence is better than a long dangling fragment.
        return chunk[: ends[-1]].strip()
    for sep in ("——", "，", "、", ",", " "):
        pos = chunk.rfind(sep)
        if pos >= max(4, int(max_chars * 0.4)):
            cut = chunk[:pos].strip()
            if cut:
                return cut
    chunk = chunk.rstrip()
    while len(chunk) > 4 and looks_incomplete(chunk):
        chunk = chunk[:-1].rstrip()
    return chunk


def spoken_char_budget(duration_sec: float, chars_per_sec: float) -> int:
    if duration_sec <= 0 or chars_per_sec <= 0:
        return 0
    return max(1, int(duration_sec * chars_per_sec))


def hashtag_token(text: str, max_chars: int = 20) -> str:
    token = _HASHTAG_UNSAFE_RE.sub("", sanitize_text(text))
    return token[:max_chars]


def total_payload_chars(raw: dict) -> int:
    """Approximate size of a JSON-like mapping for the whole-input cap."""
    pieces: list[str] = []

    def walk(node: object) -> None:
        if node is None:
            return
        if isinstance(node, str):
            pieces.append(node)
        elif isinstance(node, dict):
            for key, value in node.items():
                pieces.append(str(key))
                walk(value)
        elif isinstance(node, (list, tuple)):
            for item in node:
                walk(item)
        else:
            pieces.append(str(node))

    walk(raw)
    return sum(len(piece) for piece in pieces)
