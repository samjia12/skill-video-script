"""BGM suggestions tied to platform music libraries, never pirated track names."""

from __future__ import annotations

from .copy_bank import BGM_BY_STYLE, BGM_KEYWORDS
from .models import BgmSuggestion, ProductBrief
from .platforms import PlatformSpec
from .styles import StyleSpec


def suggest_bgm(brief: ProductBrief, platform: PlatformSpec, style: StyleSpec) -> BgmSuggestion:
    meta = BGM_BY_STYLE[style.id]
    keywords = BGM_KEYWORDS.get((platform.id, style.id), ("日常", "轻快"))
    extra = []
    if brief.category:
        extra.append(brief.category)
    if brief.audience:
        extra.append(brief.audience)
    search = tuple(list(keywords) + extra[:2])
    ducking = (
        "口播段落 BGM 压到 -18~-22 LUFS 相对对白；"
        "黄金 3 秒可抬 2dB 做停滑，CTA 前 0.4 秒做短淡出。"
    )
    return BgmSuggestion(
        mood=meta["mood"],
        tempo_bpm=meta["tempo_bpm"],
        genre=meta["genre"],
        energy=meta["energy"],
        search_keywords=search,
        ducking=ducking + f" 曲库优先使用{platform.music_library}。",
        avoid=meta["avoid"],
    )
