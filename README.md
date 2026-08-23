# skill-video-script

Generate **three distinct short-video scripts** from a product brief and a target platform (Douyin, WeChat Channels, or Bilibili). Every variant includes a storyboard, a timed voiceover, a golden 3-second opening, BGM guidance, and subtitle notes.

This repository is both:

- an **Agent Skill** (`SKILL.md`) that coding agents can load, and
- a **standalone Python CLI / library** that runs offline with the standard library.

[中文文档](README.zh-CN.md) ·
[营销介绍博文](docs/blog/intro-for-marketers.zh-CN.md) ·
[Intro for marketers](docs/blog/intro-for-marketers.md) ·
[Release notes v0.1.0](docs/releases/v0.1.0.md)

## Features

- **3 styles, always:** 种草安利 (grass / recommendation), 干货教程 (how-to), 剧情反转 (story twist).
- **Platform playbooks** for Douyin, WeChat Channels, and Bilibili (duration, pacing, hashtags, CTA, subtitle safe area).
- **Golden 3-second hook** with spoken line, visual, on-screen type, and technique label.
- **Storyboard table** with contiguous timings, camera, and per-shot voiceover.
- **BGM suggestions** as licensed-library search keywords — no pirated track names.
- **Subtitle spec:** font, position, highlight color, per-line character cap.
- **Offline by default.** Optional LLM rewrite via an OpenAI-compatible HTTP API.
- **Defensive input handling:** empty, oversized, illegal JSON, special characters, IO permissions, rate limits, network failures.

## Requirements

- Python 3.9 or newer
- `pytest` only if you want to run the test suite (`requirements.txt`)

No API key is required for the default template engine.

## Install

```bash
git clone https://github.com/samjia12/skill-video-script.git
cd skill-video-script
python3 -m pip install -r requirements.txt
```

The library lives in `src/`. The CLI adds that path automatically, so you do not have to `pip install -e .` just to try it.

As a Grok / Claude / Codex skill: copy this folder (or add a git submodule) into your agent's skills directory so `SKILL.md` is discoverable. Trigger with `/skill-video-script` or by asking for a 抖音 / 视频号 / B站 script.

## Quick start

```bash
python3 scripts/generate_script.py \
  --name "清润防晒霜" \
  --platform douyin \
  --points "清爽不黏腻,SPF50+,学生党价格" \
  --audience "通勤学生和上班族" \
  --category "美妆防晒" \
  --price "79元"
```

JSON file:

```bash
python3 scripts/generate_script.py examples/douyin_skincare.json
python3 scripts/generate_script.py examples/wechat_coffee.json -o output/coffee.md --format md
python3 scripts/generate_script.py examples/bilibili_keyboard.json --format json
```

Library (`PYTHONPATH=src` is required unless you `pip install -e .`):

```bash
PYTHONPATH=src python3 - <<'PY'
from video_script import generate, parse_brief, render_markdown

brief = parse_brief({
    "name": "清润防晒霜",
    "platform": "抖音",
    "selling_points": ["清爽不黏腻", "SPF50+"],
})
print(render_markdown(generate(brief)))
PY
```

`scripts/generate_script.py` and the files in `examples/` already put `src/` on `sys.path`.

## Examples

The files under `examples/` are runnable as-is from the repo root.

### 1. Douyin · sunscreen (grass / how-to / twist)

**Input** (`examples/douyin_skincare.json`):

```json
{
  "name": "清润防晒霜",
  "platform": "douyin",
  "category": "美妆防晒",
  "selling_points": ["清爽不黏腻", "SPF50+", "学生党价格"],
  "audience": "通勤学生和上班族",
  "price": "79元",
  "brand": "晴川",
  "description": "出门前30秒涂完，通勤也不花脸。",
  "duration_sec": 27
}
```

```bash
python3 examples/01_douyin_skincare.py
# or: python3 scripts/generate_script.py examples/douyin_skincare.json
```

**Output (excerpt, version 1 · 种草安利):**

```
# 清润防晒霜 · 抖音 短视频脚本

## 版本 1 · 种草安利（`grass`）
- **标题：** 通勤学生和上班族请收藏：清润防晒霜真的有清爽不黏腻
- **时长：** 27s
- **话题：** #清润防晒霜 #美妆防晒 #清爽不黏腻 #种草 #日常 #抖音

### 黄金 3 秒开头
- **技法：** 结果前置（`result_first`）
- **时长：** 3.0s
- **口播：** 停！清爽不黏腻。
- **画面：** 桌面俯拍，手把清润防晒霜推到画面中心，同时切环境音变干净。
- **屏上大字：** 先别划走

### 分镜表
| # | 时间 | 角色 | 画面 | 口播 | ...
| 1 | 0.0–3.0s | hook | ... | 停！清爽不黏腻。 | ...
| 7 | 23.8–27.0s | cta | ... | 还有想看对比实测的 | ...

### 口播稿
[0:00.0-0:03.0] 停！清爽不黏腻。
...
[0:23.8-0:27.0] 还有想看对比实测的

### BGM 建议
- 曲库搜索词：夏日清爽 / 种草 / 轻快日常 / 阳光
- 闪避：口播段落 BGM 压到 -18~-22 LUFS 相对对白

### 字幕建议
- 字体：抖音美好体 / 思源黑体 Bold
- 每行上限：11 字
- 高亮：#FFE500
```

The same run also emits version 2 (how-to, 3-step usage) and version 3 (story twist / almost-returned-it).

### 2. WeChat Channels · portable coffee maker

**Input** (`examples/wechat_coffee.json`): a 299 RMB capsule machine for renters, 36 seconds.

```bash
python3 examples/02_wechat_coffee.py
```

**Output (excerpt):**

```
# 便携胶囊咖啡机 · 视频号 短视频脚本
- **平台：** 视频号（`wechat`）

## 版本 1 · 种草安利
- **标题：** 299元档的30秒出杯，我选便携胶囊咖啡机
- **话题：** #便携胶囊咖啡机 #小家电 #30秒出杯 #真实分享
- **黄金 3 秒口播：** 30秒出杯，是真的。
- 8 shots, 36.0s, CTA is follow + private message rather than a shop cart
```

JSON format is used by this example so you can pipe it into other tools.

### 3. Bilibili · custom keyboard kit

**Input** (`examples/bilibili_keyboard.json`): a 499 RMB hot-swap kit aimed at first-time builders, 60 seconds.

```bash
python3 examples/03_bilibili_keyboard.py
```

**Output (excerpt):**

```
# 星核机械键盘套件 · B站 短视频脚本
- **平台：** B站（`bilibili`）
- **话题：** #星核机械键盘套件 #外设 #热插拔 #开箱 #测评

## 版本 1 · 种草安利
- **黄金 3 秒口播：** 结论：值。
- 9 shots / 60s, denser voiceover, 三连 CTA, subtitle area keeps a danmaku channel at the top
```

Run all bundled inputs:

```bash
bash examples/run_all.sh
```

## Configuration

| Variable | Default | Meaning |
| --- | --- | --- |
| `VIDEO_SCRIPT_API_KEY` | (empty) | Required only for `--backend llm` |
| `VIDEO_SCRIPT_API_BASE` | `https://api.openai.com/v1` | OpenAI-compatible base URL |
| `VIDEO_SCRIPT_MODEL` | `gpt-4o-mini` | Chat Completions model id |
| `VIDEO_SCRIPT_TIMEOUT` | `20` | HTTP timeout in seconds |

CLI flags:

| Flag | Description |
| --- | --- |
| `--name` / `--platform` / `--points` | Brief without a JSON file |
| `--audience` `--category` `--price` `--brand` `--description` `--duration` `--language` | Optional brief fields (`--language` is stored; VO stays Chinese) |
| `--backend template\|llm` | Default `template` (offline) |
| `--format md\|json\|both` | Default `md` |
| `-o` / `--output` | Write a file (parents created) |
| `--stdout` | Also print when `-o` is set |
| `input` or `-` | JSON path or stdin |

Platform aliases: `抖音` / `douyin` / `tiktok`, `视频号` / `wechat` / `channels`, `B站` / `bilibili` / `哔哩哔哩`.

Hard limits (see `src/video_script/constants.py`): name ≤ 80 chars, ≤ 12 selling points, duration 8–180 s, total payload ≤ 8000 chars.

## FAQ

**Do I need an LLM API key?**
No. The default engine is a deterministic template/strategy generator. `--backend llm` is an optional rewrite and fails closed if the key is missing.

**Why is the copy in Chinese?**
Douyin, WeChat Channels, and Bilibili are Chinese-language feeds. Section titles in the Markdown output stay in Chinese so creators can paste them into an editor.

**Can I add TikTok / YouTube Shorts / Instagram Reels?**
Not in 0.1.0. Those products have different music licensing and CTA surfaces. The `tiktok` alias currently maps to the Douyin playbook. Open an issue or extend `platforms.py` + `copy_bank.py`.

**Will this recommend a copyrighted song?**
No. BGM output is mood, BPM, genre, and **library search keywords**.

**The hook line looks truncated.**
The engine prefers a **complete short sentence** that fits the ~3-second speaking budget. A long product name may show up in later shots rather than in the opening.

**Does `--language en` switch the voiceover to English?**
No. It is stored on the brief. Spoken copy stays Chinese because Douyin / Channels / Bilibili are Chinese-language feeds. English VO is on the [0.1.0 roadmap](docs/releases/v0.1.0.md).

**How do I use this as an agent skill?**
Point the agent at `SKILL.md`. The skill tells the agent to collect a brief, run `scripts/generate_script.py`, and present all three versions in a fixed order.

**Exit codes?**
`0` success, `2` bad input, `3` network, `4` missing credentials / not writable.

## Contributing

1. Fork and create a branch.
2. Keep runtime on the Python standard library unless a dependency is discussed in the issue.
3. Add or update a unit test next to the behavior you change (`tests/`).
4. Run `python3 -m pytest tests`.
5. Do not commit API keys. Do not add pirated music titles to `copy_bank.py`.
6. Open a PR with the [pull request template](.github/PULL_REQUEST_TEMPLATE.md): summary, test output, and any new example JSON. Bugs / features / how-to questions use the [issue templates](.github/ISSUE_TEMPLATE/).

Design notes for the original three implementation options live in [`DESIGN.md`](DESIGN.md).

## License

[MIT](LICENSE) © 2026 skill-video-script contributors
