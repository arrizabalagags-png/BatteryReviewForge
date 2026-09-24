"""A restrained, original palette and final-size Matplotlib styling."""

from __future__ import annotations

import json
import hashlib
import re
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt

from .data import DataContractError

MM_PER_INCH = 25.4
THEME = json.loads((Path(__file__).resolve().parents[2] / "assets" / "figure_theme.json").read_text(encoding="utf-8"))
PRESETS = THEME["presets"]
COLOR = re.compile(r"^#[0-9A-Fa-f]{6}$")
DEFAULT_STYLE = "forge"
COLORS = tuple(PRESETS[DEFAULT_STYLE]["series"])
MARKERS = ("o", "s", "^", "D", "v")
LINESTYLES = ("-", "--", "-.", ":", "-")
PLOT_STYLE = {
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
    "font.size": 7,
    "text.color": THEME["ink"],
    "axes.labelcolor": THEME["ink"],
    "axes.edgecolor": THEME["ink"],
    "xtick.color": THEME["ink"],
    "ytick.color": THEME["ink"],
    "axes.labelsize": 8,
    "axes.titlesize": 8,
    "xtick.labelsize": 6,
    "ytick.labelsize": 6,
    "legend.fontsize": 6,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.linewidth": 0.8,
    "xtick.major.width": 0.7,
    "ytick.major.width": 0.7,
    "lines.linewidth": 1.5,
    "hatch.linewidth": 0.4,
    "svg.fonttype": "none",
    "pdf.fonttype": 42,
    "savefig.facecolor": "white",
}


def get_preset(style: str) -> dict:
    if style not in PRESETS:
        raise DataContractError(f"Unknown figure style {style!r}; choose one of {', '.join(PRESETS)}")
    return PRESETS[style]


def register_community_style(lock_path: str | Path) -> tuple[str, dict]:
    """Load one pinned JSON style from an explicit local lock; no network or code execution."""
    lock_file = Path(lock_path)
    lock = json.loads(lock_file.read_text(encoding="utf-8"))
    pin = lock.get("style_id", "")
    if not re.fullmatch(r"community:[a-z][a-z0-9-]*@[0-9]+\.[0-9]+\.[0-9]+", pin):
        raise DataContractError("Community style needs a pinned community:id@version lock")
    asset_file = (lock_file.parent / lock["asset_file"]).resolve()
    if asset_file.parent != lock_file.parent.resolve() or not asset_file.is_file():
        raise DataContractError("Community style JSON must sit beside its lock file")
    raw = asset_file.read_bytes()
    if hashlib.sha256(raw).hexdigest() != lock.get("sha256"):
        raise DataContractError("Community style hash changed after locking")
    asset = json.loads(raw)
    identity = f'community:{asset.get("id")}@{asset.get("version")}'
    if asset.get("category") != "style" or identity != pin or asset.get("background", "").upper() != "#FFFFFF":
        raise DataContractError("Community style identity or background is invalid")
    series = asset.get("series", [])
    if not isinstance(series, list) or not 2 <= len(series) <= 8 or not all(isinstance(c, str) and COLOR.fullmatch(c) for c in series):
        raise DataContractError("Community style needs 2–8 valid series colors")
    required_roles = set(THEME["roles"])
    required_pastels = set(THEME["pastels"])
    roles, pastels = asset.get("roles"), asset.get("pastels")
    if not isinstance(roles, dict) or not isinstance(pastels, dict) or not required_roles <= set(roles) or not required_pastels <= set(pastels):
        raise DataContractError("Community style roles or pastels are incomplete")
    if not all(isinstance(c, str) and COLOR.fullmatch(c) for c in list(roles.values()) + list(pastels.values())):
        raise DataContractError("Community style roles or pastels contain invalid colors")
    line_pt = asset.get("line_pt")
    if not isinstance(line_pt, (int, float)) or not .5 <= line_pt <= 3:
        raise DataContractError("Community style line width must be 0.5–3 pt")
    PRESETS[pin] = {"series": series, "roles": roles, "pastels": pastels, "line_pt": line_pt,
                    "label_zh": asset["name"], "label_en": asset["name"], "purpose": asset["description"]}
    return pin, {key: lock[key] for key in ("asset_id", "asset_version", "source_url", "sha256", "retrieved_at", "review_status")}


def colors_for(style: str) -> tuple[str, ...]:
    return tuple(get_preset(style)["series"])


def theme_for(style: str) -> dict:
    preset = get_preset(style)
    return {**THEME, "roles": preset["roles"], "pastels": preset["pastels"]}


def make_figure(width_mm: float = 89, height_mm: float = 65, *, style: str = DEFAULT_STYLE):
    if width_mm <= 0 or height_mm <= 0:
        raise ValueError("Figure dimensions must be positive")
    preset = get_preset(style)
    selected_theme = theme_for(style)
    plot_style = {**PLOT_STYLE,
                  "text.color": THEME["ink"],
                  "axes.labelcolor": THEME["ink"],
                  "axes.edgecolor": THEME["ink"],
                  "lines.linewidth": preset["line_pt"]}
    with mpl.rc_context(plot_style):
        fig, ax = plt.subplots(
            figsize=(width_mm / MM_PER_INCH, height_mm / MM_PER_INCH),
            layout="constrained",
        )
    fig.batteryplot_style = style
    fig.batteryplot_theme = selected_theme
    fig.batteryplot_linewidth = float(preset["line_pt"])
    return fig, ax


def condition_banner(fig, note: str) -> None:
    fig.text(0.5, 0.99, f"Comparison limits · {note}", ha="center", va="top", fontsize=6,
             color=fig.batteryplot_theme["roles"]["limitation_or_failure"])
