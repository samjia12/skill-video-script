"""Render a generation result as Markdown or JSON."""

from __future__ import annotations

import json

from .models import GenerationResult, ScriptVersion
from .textutil import escape_markdown


def render_json(result: GenerationResult, *, indent: int = 2) -> str:
    return json.dumps(result.to_dict(), ensure_ascii=False, indent=indent) + "\n"


def _shot_table(version: ScriptVersion) -> str:
    header = (
        "| # | 时间 | 角色 | 画面 | 口播 | 字幕 | 机位 |\n"
        "| --- | --- | --- | --- | --- | --- | --- |"
    )
    rows = [header]
    for shot in version.storyboard:
        rows.append(
            "| {i} | {t} | {r} | {v} | {vo} | {s} | {c} |".format(
                i=shot.index,
                t=f"{shot.start_sec:.1f}–{shot.end_sec:.1f}s",
                r=escape_markdown(shot.role),
                v=escape_markdown(shot.visual).replace("\n", " "),
                vo=escape_markdown(shot.voiceover).replace("\n", " "),
                s=escape_markdown(shot.on_screen_text).replace("\n", " "),
                c=escape_markdown(shot.camera),
            )
        )
    return "\n".join(rows)


def _render_version(index: int, version: ScriptVersion) -> str:
    tags = " ".join(version.hashtags)
    bgm = version.bgm
    sub = version.subtitle
    hook = version.hook
    parts = [
        f"## 版本 {index} · {version.style_label}（`{version.style_id}`）",
        "",
        f"- **标题：** {escape_markdown(version.title)}",
        f"- **封面字：** {escape_markdown(version.cover_text)}",
        f"- **时长：** {version.duration_sec:.0f}s",
        f"- **话题：** {escape_markdown(tags)}",
        "",
        "### 黄金 3 秒开头",
        "",
        f"- **技法：** {hook.technique_label}（`{hook.technique}`）",
        f"- **时长：** {hook.duration_sec:.1f}s",
        f"- **口播：** {escape_markdown(hook.spoken)}",
        f"- **画面：** {escape_markdown(hook.visual)}",
        f"- **屏上大字：** {escape_markdown(hook.on_screen_text)}",
        "",
        "### 分镜表",
        "",
        _shot_table(version),
        "",
        "### 口播稿",
        "",
        "```",
        version.voiceover,
        "```",
        "",
        "### BGM 建议",
        "",
        f"- **情绪：** {bgm.mood}",
        f"- **速度：** {bgm.tempo_bpm} BPM",
        f"- **类型：** {bgm.genre}（能量 {bgm.energy}）",
        f"- **曲库搜索词：** {' / '.join(bgm.search_keywords)}",
        f"- **闪避：** {bgm.ducking}",
        f"- **避免：** {bgm.avoid}",
        "",
        "### 字幕建议",
        "",
        f"- **字体：** {sub.font}",
        f"- **位置：** {sub.position}",
        f"- **主色 / 高亮：** {sub.primary_color} / {sub.highlight_color}",
        f"- **每行上限：** {sub.max_chars_per_line} 字",
        f"- **必须高亮的词：** {'、'.join(sub.keywords)}",
        f"- **注意事项：** {sub.notes}",
        "",
        "### 结尾 CTA",
        "",
        escape_markdown(version.cta),
        "",
    ]
    return "\n".join(parts)


def render_markdown(result: GenerationResult) -> str:
    product = result.product
    warning_block = ""
    if result.warnings:
        items = "\n".join(f"- {escape_markdown(item)}" for item in result.warnings)
        warning_block = f"\n> **Warnings**\n>\n{items}\n"
    header = [
        f"# {escape_markdown(product.name)} · {result.platform_label} 短视频脚本",
        "",
        f"- **平台：** {result.platform_label}（`{result.platform}`）",
        f"- **卖点：** {escape_markdown('、'.join(product.selling_points))}",
        f"- **人群：** {escape_markdown(product.audience or '（未指定）')}",
        f"- **引擎：** {result.engine}",
        f"- **生成时间：** {escape_markdown(result.generated_at or '')}",
        warning_block,
        "共 3 个风格版本：种草安利、干货教程、剧情反转。",
        "",
    ]
    body = [_render_version(i, version) for i, version in enumerate(result.versions, start=1)]
    return "\n".join(header + body).strip() + "\n"
