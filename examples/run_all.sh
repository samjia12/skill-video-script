#!/usr/bin/env bash
# Run the three bundled examples through the CLI.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
python3 scripts/generate_script.py examples/douyin_skincare.json --format md >/dev/null
python3 scripts/generate_script.py examples/wechat_coffee.json --format json >/dev/null
python3 scripts/generate_script.py examples/bilibili_keyboard.json --format md >/dev/null
echo "ok: 3 examples generated"
