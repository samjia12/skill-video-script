"""Typed records that flow through validation, generation, and rendering."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class ProductBrief:
    """Normalized product input after validation."""

    name: str
    platform: str
    selling_points: tuple[str, ...]
    audience: str = ""
    category: str = ""
    price: str = ""
    brand: str = ""
    description: str = ""
    duration_sec: int | None = None
    language: str = "zh"
    warnings: tuple[str, ...] = field(default_factory=tuple)

    @property
    def brand_or_name(self) -> str:
        return self.brand or self.name

    @property
    def lead_point(self) -> str:
        return self.selling_points[0] if self.selling_points else self.name

    def slot_map(self) -> dict[str, str]:
        """Values interpolated into copy templates."""
        points = "、".join(self.selling_points[:3])
        return {
            "name": self.name,
            "point": self.lead_point,
            "points": points,
            "audience": self.audience or "普通人",
            "price": self.price or "这个价位",
            "brand": self.brand_or_name,
            "category": self.category or "好物",
        }


@dataclass(frozen=True)
class GoldenHook:
    """The first ~3 seconds: spoken line, visual, and technique."""

    spoken: str
    visual: str
    technique: str
    technique_label: str
    duration_sec: float
    on_screen_text: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Shot:
    """One storyboard row with timing, picture, and voiceover."""

    index: int
    start_sec: float
    end_sec: float
    role: str
    visual: str
    voiceover: str
    on_screen_text: str
    camera: str
    notes: str

    @property
    def duration_sec(self) -> float:
        return round(self.end_sec - self.start_sec, 2)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["duration_sec"] = self.duration_sec
        return payload


@dataclass(frozen=True)
class BgmSuggestion:
    mood: str
    tempo_bpm: str
    genre: str
    energy: str
    search_keywords: tuple[str, ...]
    ducking: str
    avoid: str

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["search_keywords"] = list(self.search_keywords)
        return payload


@dataclass(frozen=True)
class SubtitleSuggestion:
    style: str
    font: str
    position: str
    primary_color: str
    highlight_color: str
    max_chars_per_line: int
    keywords: tuple[str, ...]
    notes: str

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["keywords"] = list(self.keywords)
        return payload


@dataclass(frozen=True)
class ScriptVersion:
    """One complete style variant of the short-video script."""

    style_id: str
    style_label: str
    title: str
    cover_text: str
    duration_sec: float
    hook: GoldenHook
    storyboard: tuple[Shot, ...]
    voiceover: str
    bgm: BgmSuggestion
    subtitle: SubtitleSuggestion
    hashtags: tuple[str, ...]
    cta: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "style_id": self.style_id,
            "style_label": self.style_label,
            "title": self.title,
            "cover_text": self.cover_text,
            "duration_sec": self.duration_sec,
            "hook": self.hook.to_dict(),
            "storyboard": [shot.to_dict() for shot in self.storyboard],
            "voiceover": self.voiceover,
            "bgm": self.bgm.to_dict(),
            "subtitle": self.subtitle.to_dict(),
            "hashtags": list(self.hashtags),
            "cta": self.cta,
        }


@dataclass(frozen=True)
class GenerationResult:
    """Three script versions plus the brief they were generated from."""

    product: ProductBrief
    platform: str
    platform_label: str
    engine: str
    versions: tuple[ScriptVersion, ...]
    warnings: tuple[str, ...] = field(default_factory=tuple)
    generated_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "product": {
                "name": self.product.name,
                "platform": self.platform,
                "selling_points": list(self.product.selling_points),
                "audience": self.product.audience,
                "category": self.product.category,
                "price": self.product.price,
                "brand": self.product.brand,
                "description": self.product.description,
                "duration_sec": self.product.duration_sec,
                "language": self.product.language,
            },
            "platform": self.platform,
            "platform_label": self.platform_label,
            "engine": self.engine,
            "generated_at": self.generated_at,
            "warnings": list(self.warnings),
            "versions": [version.to_dict() for version in self.versions],
        }
