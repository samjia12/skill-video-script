#!/usr/bin/env python3
"""Example: Douyin script for a sunscreen. Run from the repo root:

    python3 examples/01_douyin_skincare.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from video_script import generate, render_markdown  # noqa: E402
from video_script.io_util import load_brief_from_path  # noqa: E402


def main() -> int:
    brief = load_brief_from_path(ROOT / "examples" / "douyin_skincare.json")
    result = generate(brief)
    print(render_markdown(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
