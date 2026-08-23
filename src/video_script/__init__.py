"""Generate 3-style short-video scripts for Douyin, WeChat Channels, and Bilibili."""

from __future__ import annotations

from .constants import VERSION
from .errors import (
    AccessDeniedError,
    ConfigError,
    EmptyInputError,
    InputError,
    InputTooLongError,
    NetworkError,
    RateLimitError,
    VideoScriptError,
)
from .generator import generate
from .models import GenerationResult, ProductBrief, ScriptVersion
from .render import render_json, render_markdown
from .validate import parse_brief

__version__ = VERSION
__all__ = [
    "AccessDeniedError",
    "ConfigError",
    "EmptyInputError",
    "GenerationResult",
    "InputError",
    "InputTooLongError",
    "NetworkError",
    "ProductBrief",
    "RateLimitError",
    "ScriptVersion",
    "VideoScriptError",
    "generate",
    "parse_brief",
    "render_json",
    "render_markdown",
]
