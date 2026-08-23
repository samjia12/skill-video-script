"""Public exception types for the video-script pipeline."""

from __future__ import annotations


class VideoScriptError(Exception):
    """Base error for all library and CLI failures."""

    exit_code = 1


class InputError(VideoScriptError, ValueError):
    """Raised when the product brief is missing or malformed."""

    exit_code = 2


class EmptyInputError(InputError):
    """Raised when a required field is missing or blank."""


class InputTooLongError(InputError):
    """Raised when a field or the whole payload exceeds hard limits."""


class NetworkError(VideoScriptError):
    """Raised when an optional LLM HTTP call fails."""

    exit_code = 3


class RateLimitError(NetworkError):
    """Raised when the local limiter or the provider returns HTTP 429."""

    def __init__(self, message: str, retry_after: float | None = None) -> None:
        super().__init__(message)
        self.retry_after = retry_after


class AccessDeniedError(VideoScriptError, OSError):
    """Raised when credentials are missing or a path is not writable."""

    exit_code = 4


class ConfigError(AccessDeniedError):
    """Raised when LLM mode is requested without usable configuration."""
