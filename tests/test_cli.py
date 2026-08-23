"""Unit tests for the CLI entry point."""

from __future__ import annotations

import io
import json
from pathlib import Path

import pytest

from video_script.cli import main


def test_cli_from_flags_stdout() -> None:
    buf = io.StringIO()
    code = main(
        [
            "--name",
            "清润防晒霜",
            "--platform",
            "抖音",
            "--points",
            "清爽,SPF50+",
            "--format",
            "json",
        ],
        stdout=buf,
    )
    assert code == 0
    payload = json.loads(buf.getvalue())
    assert payload["platform"] == "douyin"
    assert len(payload["versions"]) == 3


def test_cli_from_file_and_output(tmp_path: Path) -> None:
    src = tmp_path / "in.json"
    src.write_text(
        json.dumps(
            {
                "name": "胶囊咖啡机",
                "platform": "wechat",
                "selling_points": ["30秒出杯", "占地小"],
                "audience": "租房党",
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    out = tmp_path / "script.md"
    code = main([str(src), "-o", str(out), "--format", "md"])
    assert code == 0
    text = out.read_text(encoding="utf-8")
    assert "胶囊咖啡机" in text
    assert "视频号" in text


def test_cli_stdin_json() -> None:
    payload = {"name": "键盘", "platform": "bilibili", "points": ["热插拔"]}
    buf = io.StringIO()
    code = main(
        ["-", "--format", "json"],
        stdin=io.StringIO(json.dumps(payload, ensure_ascii=False)),
        stdout=buf,
    )
    assert code == 0
    assert json.loads(buf.getvalue())["platform"] == "bilibili"


def test_cli_missing_input_is_exit_2() -> None:
    err_code = main([])
    assert err_code == 2


def test_cli_llm_without_key_is_denied(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("VIDEO_SCRIPT_API_KEY", raising=False)
    code = main(
        ["--name", "A", "--platform", "douyin", "--points", "快", "--backend", "llm"]
    )
    assert code == 4
