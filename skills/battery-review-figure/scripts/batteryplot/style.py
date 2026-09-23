"""A restrained, original palette and final-size Matplotlib styling."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt

from .data import DataContractError

MM_PER_INCH = 25.4
THEME = json.loads((Path(__file__).resolve().parents[2] / "assets" / "figure_theme.json").read_text(encoding="utf-8"))
PRESETS = THEME["presets"]
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
