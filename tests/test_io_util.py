"""Unit tests for file IO."""

from __future__ import annotations

from pathlib import Path

import pytest

from video_script.errors import AccessDeniedError, EmptyInputError, InputError
from video_script.io_util import load_brief_from_path, read_text, write_output


def test_write_and_read_roundtrip(tmp_path: Path) -> None:
    path = tmp_path / "nested" / "out.md"
    write_output(path, "你好")
    assert read_text(path) == "你好"


def test_write_rejects_directory(tmp_path: Path) -> None:
    with pytest.raises(InputError):
        write_output(tmp_path, "x")


def test_read_missing_file(tmp_path: Path) -> None:
    with pytest.raises(InputError):
        read_text(tmp_path / "nope.json")


def test_load_brief_from_path(tmp_path: Path) -> None:
    path = tmp_path / "brief.json"
    path.write_text(
        '{"name":"A","platform":"douyin","selling_points":["快"]}', encoding="utf-8"
    )
    brief = load_brief_from_path(path)
    assert brief.name == "A"
    empty = tmp_path / "empty.json"
    empty.write_text("   ", encoding="utf-8")
    with pytest.raises(EmptyInputError):
        load_brief_from_path(empty)
    bad = tmp_path / "bad.json"
    bad.write_text("{", encoding="utf-8")
    with pytest.raises(InputError):
        load_brief_from_path(bad)


def test_write_unwritable_directory(tmp_path: Path) -> None:
    locked = tmp_path / "locked"
    locked.mkdir()
    locked.chmod(0)
    try:
        with pytest.raises(AccessDeniedError):
            write_output(locked / "out.md", "hi")
    finally:
        locked.chmod(0o700)
