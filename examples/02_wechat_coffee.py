#!/usr/bin/env python3
"""Example: WeChat Channels script for a portable capsule coffee maker.

    python3 examples/02_wechat_coffee.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from video_script import generate, render_json  # noqa: E402
from video_script.io_util import load_brief_from_path  # noqa: E402


def main() -> int:
    brief = load_brief_from_path(ROOT / "examples" / "wechat_coffee.json")
    result = generate(brief)
    print(render_json(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
