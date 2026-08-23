#!/usr/bin/env python3
"""Build the marketing sample report charts from bundled example briefs.

Run from the repo root:

    PYTHONPATH=src python3 scripts/generate_report.py
"""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from video_script.generator import generate  # noqa: E402
from video_script.io_util import load_brief_from_path  # noqa: E402

OUT = ROOT / "examples" / "report-sample"
EXAMPLES = [
    ROOT / "examples" / "douyin_skincare.json",
    ROOT / "examples" / "wechat_coffee.json",
    ROOT / "examples" / "bilibili_keyboard.json",
]

# Warm paper + gold / ink — matches the demo page.
PALETTE = {
    "ink": "#1a1d26",
    "gold": "#c9a227",
    "blue": "#0369a1",
    "rose": "#be123c",
    "paper": "#f6f3ec",
    "grid": "#e4dfd4",
}
STYLE_COLORS = [PALETTE["gold"], PALETTE["blue"], PALETTE["rose"]]


def setup_fonts() -> None:
    plt.rcParams["font.sans-serif"] = [
        "Songti SC",
        "Hiragino Sans GB",
        "PingFang HK",
        "STHeiti",
        "Arial Unicode MS",
        "sans-serif",
    ]
    plt.rcParams["axes.unicode_minus"] = False
    plt.rcParams["figure.facecolor"] = PALETTE["paper"]
    plt.rcParams["axes.facecolor"] = "#fffdf8"
    plt.rcParams["axes.edgecolor"] = PALETTE["grid"]
    plt.rcParams["text.color"] = PALETTE["ink"]
    plt.rcParams["axes.labelcolor"] = PALETTE["ink"]
    plt.rcParams["xtick.color"] = PALETTE["ink"]
    plt.rcParams["ytick.color"] = PALETTE["ink"]
    plt.rcParams["axes.titleweight"] = "semibold"


def load_results():
    rows = []
    for path in EXAMPLES:
        brief = load_brief_from_path(path)
        result = generate(brief)
        rows.append((path.stem, brief, result))
    return rows


def fig_duration_bar(rows, dest: Path) -> None:
    labels = [r.platform_label for _, _, r in rows]
    values = [r.versions[0].duration_sec for _, _, r in rows]
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    bars = ax.bar(labels, values, color=[PALETTE["gold"], PALETTE["blue"], PALETTE["rose"]], width=0.55)
    ax.set_ylabel("秒")
    ax.set_title("三平台成片时长（按示例 brief 生成）")
    ax.set_ylim(0, max(values) * 1.25)
    ax.yaxis.grid(True, color=PALETTE["grid"])
    ax.set_axisbelow(True)
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, val + 1.5, f"{int(val)}s", ha="center", fontsize=10)
    fig.tight_layout()
    fig.savefig(dest, dpi=140)
    plt.close(fig)


def fig_timeline_line(rows, dest: Path) -> None:
    """Cumulative seconds for the first style of each platform example."""
    fig, ax = plt.subplots(figsize=(7.6, 4.4))
    for (_, _, result), color in zip(rows, STYLE_COLORS):
        version = result.versions[0]
        xs = [0]
        ys = [0.0]
        for shot in version.storyboard:
            xs.append(shot.index)
            ys.append(shot.end_sec)
        ax.plot(
            xs,
            ys,
            marker="o",
            color=color,
            label=f"{result.platform_label} · {int(version.duration_sec)}s",
            linewidth=2,
        )
    ax.set_xlabel("分镜序号")
    ax.set_ylabel("累计秒")
    ax.set_title("三平台种草版：分镜累进（越陡越密）")
    ax.legend(frameon=False)
    ax.yaxis.grid(True, color=PALETTE["grid"])
    ax.set_axisbelow(True)
    fig.tight_layout()
    fig.savefig(dest, dpi=140)
    plt.close(fig)


def fig_role_pie(rows, dest: Path) -> None:
    buckets = {"黄金3秒": 0, "卖点展开": 0, "剧情段落": 0, "结尾CTA": 0}
    story = {"setup", "conflict", "twist", "solution", "result"}
    for _, _, result in rows:
        for version in result.versions:
            for shot in version.storyboard:
                if shot.role == "hook":
                    buckets["黄金3秒"] += 1
                elif shot.role == "cta":
                    buckets["结尾CTA"] += 1
                elif shot.role in story:
                    buckets["剧情段落"] += 1
                else:
                    buckets["卖点展开"] += 1
    counts = Counter(buckets)
    labels, sizes = zip(*counts.most_common())
    colors = plt.cm.YlOrBr(np.linspace(0.25, 0.85, len(labels)))
    fig, ax = plt.subplots(figsize=(6.8, 6.2))
    wedges, texts, autotexts = ax.pie(
        sizes,
        labels=labels,
        autopct="%1.0f%%",
        colors=colors,
        startangle=90,
        pctdistance=0.72,
    )
    for text in texts:
        text.set_fontsize(9)
    ax.set_title("九份脚本的分镜角色分布")
    fig.tight_layout()
    fig.savefig(dest, dpi=140)
    plt.close(fig)


def fig_style_radar(dest: Path) -> None:
    labels = ["黄金3秒", "信息密度", "信任感", "娱乐性", "行动号召"]
    series = {
        "种草安利": [9, 5, 6, 8, 7],
        "干货教程": [6, 9, 8, 4, 6],
        "剧情反转": [8, 5, 5, 9, 7],
    }
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    angles += angles[:1]
    fig, ax = plt.subplots(figsize=(6.6, 6.4), subplot_kw={"polar": True})
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_thetagrids(np.degrees(angles[:-1]), labels)
    ax.set_ylim(0, 10)
    ax.set_yticks([2, 4, 6, 8, 10])
    ax.yaxis.grid(True, color=PALETTE["grid"])
    for (name, vals), color in zip(series.items(), STYLE_COLORS):
        data = vals + vals[:1]
        ax.plot(angles, data, color=color, linewidth=2, label=name)
        ax.fill(angles, data, color=color, alpha=0.12)
    ax.legend(loc="upper right", bbox_to_anchor=(1.28, 1.12), frameon=False)
    ax.set_title("三风格能力雷达（模板策略，非模型打分）", pad=16)
    fig.tight_layout()
    fig.savefig(dest, dpi=140)
    plt.close(fig)


def fig_heatmap(rows, dest: Path) -> None:
    platforms = [r.platform_label for _, _, r in rows]
    styles = [v.style_label for v in rows[0][2].versions]
    matrix = []
    for _, _, result in rows:
        matrix.append([len(v.voiceover) for v in result.versions])
    data = np.array(matrix)
    fig, ax = plt.subplots(figsize=(7.2, 4.4))
    im = ax.imshow(data, cmap="YlOrBr")
    ax.set_xticks(range(len(styles)), styles)
    ax.set_yticks(range(len(platforms)), platforms)
    ax.set_title("口播稿字符数热力（平台 × 风格）")
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            ax.text(j, i, str(int(data[i, j])), ha="center", va="center", color=PALETTE["ink"])
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04, label="字符")
    fig.tight_layout()
    fig.savefig(dest, dpi=140)
    plt.close(fig)


def main() -> int:
    setup_fonts()
    OUT.mkdir(parents=True, exist_ok=True)
    rows = load_results()
    fig_duration_bar(rows, OUT / "01-duration-bar.png")
    fig_timeline_line(rows, OUT / "02-timeline-line.png")
    fig_role_pie(rows, OUT / "03-role-pie.png")
    fig_style_radar(OUT / "04-style-radar.png")
    fig_heatmap(rows, OUT / "05-vo-heatmap.png")
    print("wrote", OUT)
    for path in sorted(OUT.glob("*.png")):
        print(" ", path.name, path.stat().st_size)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
