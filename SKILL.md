---
name: skill-video-script
description: >
  Generate 3 distinct short-video scripts (storyboard, voiceover, golden 3-second
  hook, BGM, subtitles) for Douyin, WeChat Channels, and Bilibili from a product
  brief. Use when the user asks for 短视频脚本, 分镜, 口播稿, 黄金3秒, 抖音脚本,
  视频号脚本, B站脚本, Douyin/TikTok/Bilibili video copy, or runs /skill-video-script.
---

# Short-video script skill

Turn a product brief into **exactly 3 style variants** (种草安利 / 干货教程 / 剧情反转). Each variant includes a storyboard, voiceover, golden 3-second opening, BGM suggestion, and subtitle guidance.

Do not invent a free-form script first. Run the generator, then present its output.

## When to use

- User wants a short-video script for 抖音, 视频号, or B站.
- User mentions 分镜表, 口播, 黄金 3 秒, BGM, 字幕, 完播, 停滑.
- Slash command: `/skill-video-script`.

## Collect the brief

Required:

- Product **name**
- Target **platform**: `douyin` / `wechat` / `bilibili` (aliases 抖音, 视频号, B站 are accepted)
- At least one **selling point**

Optional: audience, category, price, brand, description, duration seconds.

If a required field is missing, ask once. Do not guess platform.

## Generate

From the skill root (works without installing the package):

```bash
python scripts/generate_script.py \
  --name "清润防晒霜" \
  --platform douyin \
  --points "清爽不黏腻,SPF50+,学生党价格" \
  --audience "通勤学生和上班族" \
  --category "美妆防晒" \
  --price "79元" \
  --format md
```

JSON file:

```bash
python scripts/generate_script.py examples/douyin_skincare.json -o output/script.md
```

Default engine is the offline template strategy. Only pass `--backend llm` when the user explicitly wants an LLM rewrite **and** `VIDEO_SCRIPT_API_KEY` is set. On LLM failure, report the error; do not silently ship an empty script.

## Present the result

Print all 3 versions. For each version keep this order:

1. Title + style label
2. Golden 3-second opening (spoken / visual / technique)
3. Storyboard table
4. Voiceover
5. BGM
6. Subtitles
7. CTA + hashtags

Do not drop timings. Do not merge the 3 styles into one. If the CLI prints warnings (truncated fields, duration clamp), surface them at the top.

## Guardrails

- Platforms are Douyin, WeChat Channels, Bilibili only.
- Copy is Chinese because those products are Chinese-language feeds.
- Never recommend unlicensed commercial music tracks; use library search keywords from the generator.
- Refuse requests to fabricate fake medical / financial claims beyond the user's selling points.
