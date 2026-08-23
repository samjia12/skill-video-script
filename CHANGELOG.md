# Changelog

All notable changes to this project are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-08-23

### Added

- Agent Skill (`SKILL.md`) that generates **3 style variants** of a short-video script for Douyin, WeChat Channels, and Bilibili.
- Each variant includes a storyboard, timed voiceover, golden 3-second hook, BGM suggestion, and subtitle guidance.
- Offline template/strategy engine (Python 3.9+, standard library only at runtime).
- Optional OpenAI-compatible LLM rewrite (`--backend llm`) with retries, 401/403 handling, and HTTP 429 rate-limit errors.
- CLI: `scripts/generate_script.py` (JSON file, flags, or stdin).
- Markdown and JSON renderers, atomic file output, and permission-aware IO.
- Unit tests for every core function plus eight boundary classes (empty, oversized, illegal format, network, rate limit, concurrency, special characters, access denied).
- Bilingual README, MIT license, and three runnable examples.

### Security

- Input sanitization strips NUL, bidi overrides, and zero-width characters.
- Markdown rendering escapes user-supplied names so they cannot break the document.
- LLM mode never runs unless an API key is present; credentials are read from the environment, not from the brief JSON.
