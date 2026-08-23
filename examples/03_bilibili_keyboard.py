#!/usr/bin/env python3
"""Example: Bilibili script for a beginner custom-keyboard kit.

    python3 examples/03_bilibili_keyboard.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from video_script import generate, render_markdown  # noqa: E402
from video_script.io_util import load_brief_from_path  # noqa: E402


def main() -> int:
    brief = load_brief_from_path(ROOT / "examples" / "bilibili_keyboard.json")
    result = generate(brief)
    print("engine:", result.engine)
    print("styles:", [v.style_label for v in result.versions])
    print()
    print(render_markdown(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
