"""
Programmatic B-Roll Composer
Layered composition pipeline: Background + Chart + Avatar Circle + Text Overlays
"""

import json
import tempfile
import uuid
import numpy as np
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from PIL import Image, ImageDraw, ImageFont
from moviepy import (
    VideoFileClip, ImageClip, CompositeVideoClip,
    concatenate_videoclips,
)
import moviepy.video.fx as vfx


# ---------------------------------------------------------------------------
# Crossfade concat  (Option 1: crossfadein + negative padding)
# ---------------------------------------------------------------------------

def crossfade_concat(scenes: list, fade_dur: float = 0.5):
    """
    Concatenate scenes with a dissolve transition between each pair.

    Each clip (except the first) gets a crossfadein effect.
    padding=-fade_dur overlaps consecutive clips so the fade actually fires
    instead of creating a black gap.  set_duration on every scene is
    mandatory — CompositeVideoClip.duration can be ambiguous without it,
    which makes the overlap math wrong.
    """
    faded = []
    for i, clip in enumerate(scenes):
        c = clip
        if i > 0:
            c = c.fx(vfx.CrossFadeIn, fade_dur)
        faded.append(c)
    return concatenate_videoclips(faded, padding=-fade_dur, method="compose")


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class Insight:
    key_insight: str
    supporting_stat: str
    visual_cue: str          # bar_chart_comparison | line_trend | bullet_points | full_avatar
    audio_tone: str
    chart_data: dict = field(default_factory=dict)
    duration: float = 10.0


@dataclass
class SceneAssets:
    background_img: str
    chart_img: Optional[str] = None
    avatar_video: Optional[str] = None
    bullet_img: Optional[str] = None


# ---------------------------------------------------------------------------
# Chart generator (Matplotlib → PNG with transparency)
# ---------------------------------------------------------------------------

CHART_STYLE = {
    "bg": "#0D0D0D",
    "bar_before": "#2E4057",
    "bar_after": "#E63946",
    "text": "#F1F1EF",
    "grid": "#2A2A2A",
    "accent": "#E63946",
    "pie_colors": ["#E63946", "#2E4057", "#457B9D", "#A8DADC", "#F4A261", "#2A9D8F"],
}

# ---------------------------------------------------------------------------
# Chart generators (Matplotlib → PNG with transparency)
# ---------------------------------------------------------------------------

def make_bar_chart(data: dict, out_path: str, title: str = "", 
                   show_legend: bool = True, value_suffix: str = "%",
                   subtitle: str = "") -> str:
    """Render a side-by-side comparison bar chart. Returns output path."""
    labels = data.get("labels", [])
    before = data.get("before", [])
    after = data.get("after", [])

    fig, ax = plt.subplots(figsize=(8, 4.5), facecolor="none")
    ax.set_facecolor("none")

    x = np.arange(len(labels))
    w = 0.35
    bars_b = ax.bar(x - w / 2, before, w, color=CHART_STYLE["bar_before"],
                    label="Before", zorder=3, edgecolor="none")
    bars_a = ax.bar(x + w / 2, after, w, color=CHART_STYLE["bar_after"],
                    label="After", zorder=3, edgecolor="none")

    ax.set_xticks(x)
    ax.set_xticklabels(labels, color=CHART_STYLE["text"], fontsize=11)
    ax.tick_params(axis="y", colors=CHART_STYLE["text"])
    ax.spines[:].set_visible(False)
    ax.yaxis.grid(True, color=CHART_STYLE["grid"], linewidth=0.6, zorder=0)
    ax.set_axisbelow(True)

    for bar in [*bars_b, *bars_a]:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, h + 0.5, f"{h:.0f}{value_suffix}",
                ha="center", va="bottom", color=CHART_STYLE["text"], fontsize=9,
                fontweight="bold")

    if show_legend:
        legend = ax.legend(frameon=False, labelcolor=CHART_STYLE["text"],
                           fontsize=10, loc="upper left")
    
    # Add title and optional subtitle
    if title:
        ax.set_title(title, color=CHART_STYLE["text"], fontsize=13,
                     fontweight="bold", pad=12)
    if subtitle:
        fig.text(0.5, 0.02, subtitle, ha='center', color=CHART_STYLE["text"], 
                 fontsize=10, style='italic')

    fig.tight_layout(pad=0.5, rect=(0, 0.03 if subtitle else 0, 1, 1))
    fig.savefig(out_path, dpi=150, transparent=True, bbox_inches="tight")
    plt.close(fig)
    return out_path


def make_horizontal_bar(data: dict, out_path: str, title: str = "",
                        value_suffix: str = "%", bar_color: str = None) -> str:
    """Render a horizontal bar chart (good for rankings/lists)."""
    labels = data.get("labels", [])
    values = data.get("values", data.get("y", []))
    
    if not values:
        return ""
    
    bar_color = bar_color or CHART_STYLE["bar_after"]

    fig, ax = plt.subplots(figsize=(8, 4.5), facecolor="none")
    ax.set_facecolor("none")

    y_pos = np.arange(len(labels))
    bars = ax.barh(y_pos, values, color=bar_color, zorder=3, edgecolor="none", height=0.6)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, color=CHART_STYLE["text"], fontsize=11)
    ax.tick_params(axis="x", colors=CHART_STYLE["text"])
    ax.spines[:].set_visible(False)
    ax.xaxis.grid(True, color=CHART_STYLE["grid"], linewidth=0.6, zorder=0)
    ax.set_axisbelow(True)
    ax.invert_yaxis()

    for i, bar in enumerate(bars):
        width = bar.get_width()
        ax.text(width + 0.5, bar.get_y() + bar.get_height()/2, f"{width:.0f}{value_suffix}",
                ha="left", va="center", color=CHART_STYLE["text"], fontsize=10,
                fontweight="bold")

    if title:
        ax.set_title(title, color=CHART_STYLE["text"], fontsize=13,
                     fontweight="bold", pad=12)

    fig.tight_layout(pad=0.5)
    fig.savefig(out_path, dpi=150, transparent=True, bbox_inches="tight")
    plt.close(fig)
    return out_path


def make_line_trend(data: dict, out_path: str, title: str = "",
                    show_area: bool = True, show_markers: bool = True) -> str:
    """Render a trend line chart."""
    x_vals = data.get("x", [])
    y_vals = data.get("y", [])

    fig, ax = plt.subplots(figsize=(8, 4.5), facecolor="none")
    ax.set_facecolor("none")
    
    line_style = data.get("line_style", "-")
    line_width = data.get("line_width", 2.5)
    
    ax.plot(x_vals, y_vals, color=CHART_STYLE["accent"],
            linewidth=line_width, linestyle=line_style,
            marker="o" if show_markers else None, markersize=7, zorder=3)
    
    if show_area:
        ax.fill_between(x_vals, y_vals, alpha=0.12, color=CHART_STYLE["accent"])
    
    ax.spines[:].set_visible(False)
    ax.tick_params(colors=CHART_STYLE["text"])
    ax.yaxis.grid(True, color=CHART_STYLE["grid"], linewidth=0.6, zorder=0)
    
    if title:
        ax.set_title(title, color=CHART_STYLE["text"], fontsize=13,
                     fontweight="bold", pad=12)

    fig.tight_layout(pad=0.5)
    fig.savefig(out_path, dpi=150, transparent=True, bbox_inches="tight")
    plt.close(fig)
    return out_path


def make_pie_chart(data: dict, out_path: str, title: str = "",
                   show_labels: bool = True, show_percent: bool = True,
                   donut: bool = False) -> str:
    """Render a pie chart."""
    labels = data.get("labels", [])
    values = data.get("values", data.get("y", []))
    
    if not values:
        return ""
    
    colors = CHART_STYLE["pie_colors"][:len(values)]
    
    fig, ax = plt.subplots(figsize=(6, 4.5), facecolor="none")
    ax.set_facecolor("none")
    
    if donut:
        wedges, texts, autotexts = ax.pie(
            values, labels=labels if show_labels else None,
            colors=colors, autopct=lambda p: f'{p:.1f}%' if show_percent else '',
            startangle=90, pctdistance=0.75,
            wedgeprops=dict(width=0.5, edgecolor="none")
        )
    else:
        wedges, texts, autotexts = ax.pie(
            values, labels=labels if show_labels else None,
            colors=colors, autopct=lambda p: f'{p:.1f}%' if show_percent else '',
            startangle=90, pctdistance=0.8
        )
    
    for text in texts:
        text.set_color(CHART_STYLE["text"])
        text.set_fontsize(10)
    
    for autotext in autotexts:
        autotext.set_color(CHART_STYLE["text"])
        autotext.set_fontsize(9)
        autotext.set_fontweight("bold")
    
    if title:
        ax.set_title(title, color=CHART_STYLE["text"], fontsize=13,
                     fontweight="bold", pad=12)

    fig.tight_layout(pad=0.5)
    fig.savefig(out_path, dpi=150, transparent=True, bbox_inches="tight")
    plt.close(fig)
    return out_path


def make_stacked_bar(data: dict, out_path: str, title: str = "",
                     stack_labels: list = None) -> str:
    """Render a stacked bar chart."""
    labels = data.get("labels", [])
    stacks = data.get("stacks", [])  # List of lists, each inner list is a stack
    
    if not stacks or len(stacks) < 2:
        return ""
    
    stack_labels = stack_labels or [f"Series {i+1}" for i in range(len(stacks))]
    
    fig, ax = plt.subplots(figsize=(8, 4.5), facecolor="none")
    ax.set_facecolor("none")
    
    x = np.arange(len(labels))
    bottom = np.zeros(len(labels))
    colors = CHART_STYLE["pie_colors"][:len(stacks)]
    
    for i, stack in enumerate(stacks):
        bars = ax.bar(x, stack, 0.6, bottom=bottom, color=colors[i],
                      label=stack_labels[i], zorder=3, edgecolor="none")
        
        for j, bar in enumerate(bars):
            height = bar.get_height()
            if height > 5:  # Only show label if segment is big enough
                ax.text(bar.get_x() + bar.get_width()/2, 
                        bottom[j] + height/2,
                        f"{height:.0f}", ha="center", va="center",
                        color=CHART_STYLE["text"], fontsize=8, fontweight="bold")
        
        bottom = bottom + np.array(stack)
    
    ax.set_xticks(x)
    ax.set_xticklabels(labels, color=CHART_STYLE["text"], fontsize=11)
    ax.tick_params(axis="y", colors=CHART_STYLE["text"])
    ax.spines[:].set_visible(False)
    ax.legend(frameon=False, labelcolor=CHART_STYLE["text"], fontsize=9, loc="upper left")
    
    if title:
        ax.set_title(title, color=CHART_STYLE["text"], fontsize=13,
                     fontweight="bold", pad=12)

    fig.tight_layout(pad=0.5)
    fig.savefig(out_path, dpi=150, transparent=True, bbox_inches="tight")
    plt.close(fig)
    return out_path


# ---------------------------------------------------------------------------
# Text / Bullet overlay (Pillow → PNG)
# ---------------------------------------------------------------------------

def make_bullet_overlay(lines: list[str], out_path: str,
                        width: int = 900, font_size: int = 32) -> str:
    """Render bullet points on a semi-transparent dark pill. Returns path."""
    padding = 32
    line_h = font_size + 16
    img_h = padding * 2 + len(lines) * line_h + 12
    img = Image.new("RGBA", (width, img_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    draw.rounded_rectangle([0, 0, width - 1, img_h - 1],
                            radius=18, fill=(10, 10, 10, 185))

    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                                  font_size)
    except OSError:
        font = ImageFont.load_default()

    y = padding
    for line in lines:
        draw.text((padding + 18, y), f"• {line}", font=font, fill=(241, 241, 239, 255))
        y += line_h

    img.save(out_path, format="PNG")
    return out_path


def make_insight_card(insight: str, stat: str, out_path: str,
                      width: int = 960, height: int = 200) -> str:
    """Render a bold insight card (headline + supporting stat). Returns path."""
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle([0, 0, width - 1, height - 1],
                            radius=14, fill=(10, 10, 10, 200))

    draw.rectangle([28, 24, 36, height - 24], fill=(230, 57, 70, 255))

    try:
        font_lg = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 34)
        font_sm = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
    except OSError:
        font_lg = font_sm = ImageFont.load_default()

    draw.text((58, 36), insight, font=font_lg, fill=(241, 241, 239, 255))
    draw.text((58, 90), stat, font=font_sm, fill=(180, 180, 178, 230))

    img.save(out_path, format="PNG")
    return out_path


# ---------------------------------------------------------------------------
# Circular avatar mask
# ---------------------------------------------------------------------------

def apply_circle_mask(clip: VideoFileClip, diameter: int) -> VideoFileClip:
    """Resize clip and apply a circular alpha mask."""
    clip = clip.resize(height=diameter)
    w, h = clip.size

    Y, X = np.ogrid[:h, :w]
    cx, cy = w / 2, h / 2
    mask_arr = ((X - cx) ** 2 + (Y - cy) ** 2 <= (min(w, h) / 2) ** 2).astype(float)

    mask_clip = ImageClip(mask_arr, ismask=True).set_duration(clip.duration)
    return clip.set_mask(mask_clip)


# ---------------------------------------------------------------------------
# Ken Burns zoom effect
# ---------------------------------------------------------------------------

def ken_burns(clip: ImageClip, zoom_ratio: float = 0.08) -> ImageClip:
    """Apply a slow zoom-in over the clip duration."""
    def zoom_frame(get_frame, t):
        frame = get_frame(t)
        frac = 1 + zoom_ratio * (t / clip.duration)
        h, w = frame.shape[:2]
        new_h, new_w = int(h / frac), int(w / frac)
        y1 = (h - new_h) // 2
        x1 = (w - new_w) // 2
        cropped = frame[y1:y1 + new_h, x1:x1 + new_w]
        return np.array(Image.fromarray(cropped).resize((w, h), Image.LANCZOS))

    return clip.fl(zoom_frame, apply_to=["mask"])


# ---------------------------------------------------------------------------
# Scene builders  (one per visual_cue type)
# ---------------------------------------------------------------------------

def build_data_scene(assets: SceneAssets, insight: Insight, temp_dir: Path) -> CompositeVideoClip:
    """
    Layout: Background (Ken Burns) + Chart (fade-in) + Avatar circle (corner) + Insight card
    """
    d = insight.duration
    layers = []

    bg = (ImageClip(assets.background_img)
          .set_duration(d)
          .resize(height=1080))
    bg = ken_burns(bg)
    bg = bg.fx(vfx.lum_contrast, 0, -40)
    layers.append(bg)

    if assets.chart_img:
        chart = (ImageClip(assets.chart_img)
                 .set_duration(d - 1.5)
                 .set_start(0.5)
                 .resize(width=700)
                 .set_position(("center", 180))
                 .fx(vfx.fadein, 0.6)
                 .fx(vfx.fadeout, 0.4))
        layers.append(chart)

    card_path = str(temp_dir / f"insight_card_{uuid.uuid4().hex}.png")
    make_insight_card(insight.key_insight, insight.supporting_stat, card_path)
    card = (ImageClip(card_path)
            .set_duration(d - 1)
            .set_start(0.5)
            .set_position(("center", 820))
            .fx(vfx.fadein, 0.5))
    layers.append(card)

    if assets.avatar_video:
        avatar_raw = VideoFileClip(assets.avatar_video).subclip(0, d)
        avatar = apply_circle_mask(avatar_raw, diameter=240)
        avatar = avatar.set_position((bg.w - 280, bg.h - 280))
        layers.append(avatar)

    return CompositeVideoClip(layers, size=bg.size).set_duration(d)


def build_bullet_scene(assets: SceneAssets, insight: Insight,
                       bullets: list[str], temp_dir: Path) -> CompositeVideoClip:
    """
    Layout: AI image (Ken Burns) + Bullet overlay + Avatar circle
    """
    d = insight.duration
    layers = []

    bg = (ImageClip(assets.background_img)
          .set_duration(d)
          .resize(height=1080))
    bg = ken_burns(bg, zoom_ratio=0.05)
    bg = bg.fx(vfx.lum_contrast, 0, -50)
    layers.append(bg)

    bullet_path = str(temp_dir / f"bullets_{uuid.uuid4().hex}.png")
    make_bullet_overlay(bullets, bullet_path, width=860)
    bullets_clip = (ImageClip(bullet_path)
                    .set_duration(d - 1)
                    .set_start(0.5)
                    .set_position(("center", "center"))
                    .fx(vfx.fadein, 0.7))
    layers.append(bullets_clip)

    if assets.avatar_video:
        avatar_raw = VideoFileClip(assets.avatar_video).subclip(0, d)
        avatar = apply_circle_mask(avatar_raw, diameter=200)
        avatar = avatar.set_position((bg.w - 240, bg.h - 240))
        layers.append(avatar)

    return CompositeVideoClip(layers, size=bg.size).set_duration(d)


def build_full_avatar_scene(assets: SceneAssets, insight: Insight) -> VideoFileClip:
    """Full-screen avatar — the expensive 'Hook' scene. No overlay."""
    d = insight.duration
    avatar = VideoFileClip(assets.avatar_video).subclip(0, d)
    return avatar.resize(height=1080).set_duration(d)


# ---------------------------------------------------------------------------
# Scene dispatcher — maps visual_cue → builder
# ---------------------------------------------------------------------------

def dispatch_scene(insight: Insight, assets: SceneAssets,
                   bullet_lines: Optional[list[str]] = None,
                   temp_dir: Optional[str | Path] = None):
    """Dispatch scene based on visual_cue type."""
    cue = insight.visual_cue
    scene_temp_dir = Path(temp_dir) if temp_dir else Path(
        tempfile.mkdtemp(prefix=f"broll_{cue}_")
    )
    scene_temp_dir.mkdir(parents=True, exist_ok=True)

    if cue == "full_avatar":
        return build_full_avatar_scene(assets, insight)

    elif cue in ("bar_chart_comparison", "line_trend"):
        chart_path = str(scene_temp_dir / f"chart_{uuid.uuid4().hex}.png")
        if cue == "bar_chart_comparison":
            make_bar_chart(insight.chart_data, chart_path,
                           title=insight.key_insight)
        else:
            make_line_trend(insight.chart_data, chart_path,
                           title=insight.key_insight)
        assets.chart_img = chart_path
        return build_data_scene(assets, insight, scene_temp_dir)

    elif cue == "bullet_points":
        lines = bullet_lines or [insight.key_insight, insight.supporting_stat]
        return build_bullet_scene(assets, insight, lines, scene_temp_dir)

    else:
        return build_data_scene(assets, insight, scene_temp_dir)


# ---------------------------------------------------------------------------
# Master compositor — assembles all scenes into one video
# ---------------------------------------------------------------------------

def compose_video(scenes: list, output_path: str = "output.mp4",
                  fps: int = 24, fade_dur: float = 0.5) -> str:
    """Concatenate scenes with crossfade transitions and write final video file."""
    final = crossfade_concat(scenes, fade_dur=fade_dur)
    final.write_videofile(
        output_path,
        fps=fps,
        codec="libx264",
        audio_codec="aac",
        threads=4,
        preset="fast",
        logger=None,
    )
    return output_path


# ---------------------------------------------------------------------------
# JSON bridge — LLM insight → assets + scene
# ---------------------------------------------------------------------------

def pipeline_from_json(insight_json: str,
                       background_img: str,
                       avatar_video: Optional[str] = None) -> str:
    """
    Full pipeline:
      1. Parse LLM insight JSON
      2. Generate chart / overlay assets
      3. Build scene
      4. Write video
    Returns path to output video.
    """
    data = json.loads(insight_json)
    insight = Insight(**{k: data[k] for k in Insight.__dataclass_fields__ if k in data})
    assets = SceneAssets(background_img=background_img, avatar_video=avatar_video)
    scene_temp_dir = Path(tempfile.mkdtemp(prefix=f"scene_{insight.visual_cue}_"))
    scene = dispatch_scene(insight, assets,
                           bullet_lines=data.get("bullet_lines"),
                           temp_dir=scene_temp_dir)
    out = f"/tmp/scene_{insight.visual_cue}.mp4"
    compose_video([scene], output_path=out)
    return out


# ---------------------------------------------------------------------------
# Demo / smoke-test (no real media files needed for chart generation)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    sample_bar_data = {
        "labels": ["Content Velocity", "CTR", "Engagement", "Cost/Lead"],
        "before": [30, 22, 18, 60],
        "after": [72, 34, 41, 38],
    }
    chart_out = make_bar_chart(
        sample_bar_data,
        "/tmp/demo_chart.png",
        title="AI Tools Impact: Before vs After (2025)",
    )
    print(f"Chart saved → {chart_out}")

    bullets = [
        "AI reduced content cycles by 40% in 2025",
        "HubSpot: 12% lift in CTR with AI-assisted copy",
        "Video production cost down 3x with hybrid pipeline",
    ]
    bullet_out = make_bullet_overlay(bullets, "/tmp/demo_bullets.png")
    print(f"Bullets saved → {bullet_out}")

    card_out = make_insight_card(
        "AI tools reduced content cycles by 40%",
        "HubSpot 2026 report — 12% lift in CTR",
        "/tmp/demo_card.png",
    )
    print(f"Insight card saved → {card_out}")

    sample_json = json.dumps({
        "key_insight": "AI reduced production time by 40%",
        "supporting_stat": "HubSpot 2026: 12% CTR lift",
        "visual_cue": "bar_chart_comparison",
        "audio_tone": "authoritative_and_surprising",
        "duration": 8.0,
        "chart_data": sample_bar_data,
    })
    print("\nSample Insight JSON:\n", sample_json)
    print("\nAll asset generation tests passed.")
    print("To run full video composition, supply real background_img and avatar_video paths.")
