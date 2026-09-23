"""A restrained, original palette and final-size Matplotlib styling."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt

MM_PER_INCH = 25.4
THEME = json.loads((Path(__file__).resolve().parents[2] / "assets" / "figure_theme.json").read_text(encoding="utf-8"))
COLORS = tuple(THEME["roles"][role] for role in (
    "reference_or_baseline", "new_or_intervention", "limitation_or_failure",
    "mechanism_or_model", "neutral_context",
))
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


def make_figure(width_mm: float = 89, height_mm: float = 65):
    if width_mm <= 0 or height_mm <= 0:
        raise ValueError("Figure dimensions must be positive")
    with mpl.rc_context(PLOT_STYLE):
        fig, ax = plt.subplots(
            figsize=(width_mm / MM_PER_INCH, height_mm / MM_PER_INCH),
            layout="constrained",
        )
    return fig, ax


def condition_banner(fig, note: str) -> None:
    fig.text(0.5, 0.99, f"Different test conditions · {note}", ha="center", va="top", fontsize=6,
             color=THEME["roles"]["limitation_or_failure"])
