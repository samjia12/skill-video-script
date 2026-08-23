"""Subtitle styling and hashtag helpers."""

from __future__ import annotations

from .copy_bank import CTA_BY_PLATFORM
from .models import ProductBrief, SubtitleSuggestion
from .platforms import PlatformSpec
from .styles import StyleSpec
from .textutil import fill_template, hashtag_token, pick_template


def suggest_subtitle(
    brief: ProductBrief,
    platform: PlatformSpec,
    style: StyleSpec,
) -> SubtitleSuggestion:
    keywords = [brief.name, brief.lead_point]
    if brief.price:
        keywords.append(brief.price)
    tokens = tuple(dict.fromkeys(k for k in keywords if k))
    notes = " ".join(
        [
            platform.subtitle_style.rstrip("。；; ") + "。",
            f"每行不超过 {platform.subtitle_max_chars_per_line} 字。",
            "关键词用高亮色，数字与价格必须加粗。",
            f"风格「{style.label}」可在反转或要点处轻微缩放，但不要遮脸。",
        ]
    )
    return SubtitleSuggestion(
        style=platform.subtitle_style,
        font=platform.subtitle_font,
        position=platform.subtitle_position,
        primary_color=platform.primary_color,
        highlight_color=platform.highlight_color,
        max_chars_per_line=platform.subtitle_max_chars_per_line,
        keywords=tokens,
        notes=notes,
    )


def make_hashtags(brief: ProductBrief, platform: PlatformSpec) -> tuple[str, ...]:
    candidates = [brief.name, brief.category, brief.lead_point]
    if platform.id == "bilibili":
        candidates.extend(["开箱", "测评"])
    elif platform.id == "douyin":
        candidates.extend(["种草", "日常"])
    else:
        candidates.append("真实分享")
    candidates.extend([platform.label, brief.audience, "好物推荐", brief.brand])
    tags: list[str] = []
    seen: set[str] = set()
    for item in candidates:
        token = hashtag_token(item or "")
        if not token or token.casefold() in seen:
            continue
        seen.add(token.casefold())
        tags.append("#" + token)
        if len(tags) >= platform.hashtag_count:
            break
    return tuple(tags)


def build_cta(brief: ProductBrief, platform: PlatformSpec) -> str:
    pool = CTA_BY_PLATFORM[platform.id]
    seed = f"{brief.name}|{platform.id}|cta"
    return fill_template(pick_template(pool, seed), brief.slot_map())
