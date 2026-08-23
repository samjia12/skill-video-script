"""Platform playbooks: Douyin, WeChat Channels, Bilibili."""

from __future__ import annotations

from dataclasses import dataclass

from .constants import MAX_DURATION_SEC, MIN_DURATION_SEC
from .errors import EmptyInputError, InputError
from .textutil import sanitize_text


@dataclass(frozen=True)
class PlatformSpec:
    id: str
    label: str
    aliases: tuple[str, ...]
    min_duration: int
    max_duration: int
    default_duration: int
    aspect_ratio: str
    hook_sec: float
    chars_per_sec: float
    shot_count: int
    hashtag_count: int
    subtitle_max_chars_per_line: int
    subtitle_font: str
    subtitle_style: str
    subtitle_position: str
    primary_color: str
    highlight_color: str
    pacing: str
    music_library: str
    cta_hint: str
    notes: str


DOUYIN = PlatformSpec(
    id="douyin",
    label="抖音",
    aliases=(
        "douyin",
        "抖音",
        "dy",
        "tiktok",
        "tik tok",
        "抖音短视频",
    ),
    min_duration=15,
    max_duration=45,
    default_duration=27,
    aspect_ratio="9:16",
    hook_sec=3.0,
    chars_per_sec=4.8,
    shot_count=7,
    hashtag_count=6,
    subtitle_max_chars_per_line=11,
    subtitle_font="抖音美好体 / 思源黑体 Bold",
    subtitle_style="大字高对比，关键词色块高亮，禁止花字堆叠遮脸",
    subtitle_position="画面下 1/3 安全区，左右各留 8%",
    primary_color="#FFFFFF",
    highlight_color="#FFE500",
    pacing="fast",
    music_library="抖音音乐库（优先原创/商用授权）",
    cta_hint="评论区置顶 + 购物车/小黄车，口播要求点赞收藏",
    notes="前 3 秒必须完成停滑；节奏偏快切；信息点不超过 3 个。",
)

WECHAT = PlatformSpec(
    id="wechat",
    label="视频号",
    aliases=(
        "wechat",
        "weixin",
        "channels",
        "wx",
        "视频号",
        "微信视频号",
        "shipinhao",
        "wechatchannels",
        "wechat-channels",
    ),
    min_duration=20,
    max_duration=60,
    default_duration=36,
    aspect_ratio="9:16",
    hook_sec=3.0,
    chars_per_sec=4.0,
    shot_count=8,
    hashtag_count=4,
    subtitle_max_chars_per_line=13,
    subtitle_font="苹方 / 微软雅黑 Medium",
    subtitle_style="克制清晰，少特效，信任感优先于刺激感",
    subtitle_position="底部居中，避开头像条与进度条",
    primary_color="#FFFFFF",
    highlight_color="#FA5151",
    pacing="medium",
    music_library="视频号音乐 / 公众号原创",
    cta_hint="引导关注与私信咨询，少硬广话术，强调真实使用",
    notes="更像朋友推荐；避免过度喊麦；证据与口碑比反转更重要。",
)

BILIBILI = PlatformSpec(
    id="bilibili",
    label="B站",
    aliases=(
        "bilibili",
        "bili",
        "b站",
        "B站",
        "哔哩哔哩",
        "bilibili.com",
        "小破站",
    ),
    min_duration=30,
    max_duration=MAX_DURATION_SEC,
    default_duration=60,
    aspect_ratio="16:9 或 9:16",
    hook_sec=3.0,
    chars_per_sec=3.6,
    shot_count=9,
    hashtag_count=5,
    subtitle_max_chars_per_line=16,
    subtitle_font="思源黑体 / B站圆体",
    subtitle_style="可中英关键词对照；字幕避开弹幕密集的上方区域",
    subtitle_position="中下部，预留顶部弹幕通道",
    primary_color="#FFFFFF",
    highlight_color="#00A1D6",
    pacing="info-dense",
    music_library="Bilibili 创作中心授权曲库",
    cta_hint="三连（点赞投币收藏）+ 评论区置顶目录，可引导系列稿",
    notes="信息密度更高；允许章节感；梗要用准，不要硬凹。",
)

PLATFORMS: dict[str, PlatformSpec] = {
    DOUYIN.id: DOUYIN,
    WECHAT.id: WECHAT,
    BILIBILI.id: BILIBILI,
}


def _build_alias_table() -> dict[str, str]:
    table: dict[str, str] = {}
    for spec in PLATFORMS.values():
        table[spec.id] = spec.id
        table[_alias_key(spec.id)] = spec.id
        for alias in spec.aliases:
            table[_alias_key(alias)] = spec.id
    return table


def _alias_key(value: str) -> str:
    return sanitize_text(value).casefold().replace(" ", "").replace("_", "").replace("-", "")


# Built once: normalize_platform is on the CLI hot path.
_ALIAS_TABLE = _build_alias_table()


def normalize_platform(raw: object) -> str:
    """Map user-facing names (抖音 / 视频号 / B站 / english ids) to a canonical id."""
    if raw is None:
        raise EmptyInputError("platform is required")
    if not isinstance(raw, str):
        raise InputError("platform must be a string")
    cleaned = sanitize_text(raw)
    if not cleaned:
        raise EmptyInputError("platform is required")
    key = _alias_key(cleaned)
    if key not in _ALIAS_TABLE:
        supported = ", ".join(sorted(PLATFORMS))
        raise InputError(f"unsupported platform {raw!r}; expected one of: {supported}")
    return _ALIAS_TABLE[key]


def get_platform(platform_id: str) -> PlatformSpec:
    if platform_id not in PLATFORMS:
        raise InputError(f"unknown platform id {platform_id!r}")
    return PLATFORMS[platform_id]


def clamp_duration(requested: int | None, spec: PlatformSpec) -> tuple[int, tuple[str, ...]]:
    """Fill defaults and clamp to the platform sweet spot. Hard-reject illegal numbers upstream."""
    warnings: list[str] = []
    if requested is None:
        return spec.default_duration, tuple(warnings)
    duration = int(requested)
    if duration < spec.min_duration:
        warnings.append(
            f"duration {duration}s is below {spec.label} sweet spot "
            f"{spec.min_duration}-{spec.max_duration}s; clamped to {spec.min_duration}s"
        )
        duration = spec.min_duration
    elif duration > spec.max_duration:
        warnings.append(
            f"duration {duration}s is above {spec.label} sweet spot "
            f"{spec.min_duration}-{spec.max_duration}s; clamped to {spec.max_duration}s"
        )
        duration = spec.max_duration
    if duration < MIN_DURATION_SEC:
        duration = MIN_DURATION_SEC
    if duration > MAX_DURATION_SEC:
        duration = MAX_DURATION_SEC
    return duration, tuple(warnings)
