"""Battery-specific chart primitives. No paper data or statistics are bundled."""

from __future__ import annotations

from collections import defaultdict

import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch

from .data import (
    DataContractError,
    comparison_guard,
    number,
    require_fields,
    source_ids,
    verified_rows,
)
from .style import COLORS, LINESTYLES, MARKERS, colors_for, condition_banner, make_figure, theme_for


CYCLE_CONTEXT = (
    "chemistry", "cell_configuration", "retention_basis", "rate",
    "temperature_c", "loading_mg_cm2", "electrolyte_ul_mg",
)
RATE_CONTEXT = (
    "chemistry", "cell_configuration", "capacity_basis", "temperature_c",
    "loading_mg_cm2", "electrolyte_ul_mg",
)
BAR_CONTEXT = (
    "chemistry", "cell_configuration", "metric_basis", "rate",
    "temperature_c", "loading_mg_cm2", "electrolyte_ul_mg",
)


def _groups(rows: list[dict], key: str = "series") -> dict[str, list[tuple[int, dict]]]:
    grouped: dict[str, list[tuple[int, dict]]] = defaultdict(list)
    for index, row in enumerate(rows, 1):
        grouped[str(row[key])].append((index, row))
    if len(grouped) > len(COLORS):
        raise DataContractError(f"At most {len(COLORS)} series fit this final-size preset; split the figure")
    return dict(grouped)


def _meta(fig, chart: str, rows: list[dict], comparison: str) -> None:
    fig.batteryplot_meta = {
        "chart": chart,
        "source_ids": source_ids(rows),
        "comparison": comparison,
        "row_count": len(rows),
        "style": fig.batteryplot_style,
    }


def cycle_retention(
    rows: list[dict], *, mode: str = "direct", condition_note: str | None = None,
    width_mm: float = 89, height_mm: float = 65,
    style: str = "forge",
):
    """Plot reported retention against cycle index; no smoothing or extrapolation."""
    verified_rows(rows, ("series", "cycle", "retention_pct"))
    comparable = comparison_guard(rows, CYCLE_CONTEXT, mode=mode, condition_note=condition_note)
    fig, ax = make_figure(width_mm, height_mm, style=style)
    colors = colors_for(style)
    for series_index, (name, group) in enumerate(_groups(rows).items()):
        points = sorted((number(row["cycle"], "cycle", i), number(row["retention_pct"], "retention_pct", i)) for i, row in group)
        if any(x < 0 or y < 0 for x, y in points):
            raise DataContractError("Cycle and retention values must be non-negative")
        if len({x for x, _ in points}) != len(points):
            raise DataContractError(f"Repeated cycle index in series {name!r}; resolve replicates first")
        ax.plot([p[0] for p in points], [p[1] for p in points],
                color=colors[series_index], linestyle=LINESTYLES[series_index],
                linewidth=fig.batteryplot_linewidth,
                marker=MARKERS[series_index], markersize=3, label=name)
    ax.set(xlabel="Cycle number", ylabel="Capacity retention (%)")
    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)
    ax.legend(frameon=False, loc="best")
    if not comparable:
        condition_banner(fig, condition_note or "")
    _meta(fig, "cycle_retention", rows, "direct" if comparable else "contextual")
    return fig, ax


def rate_capability(
    rows: list[dict], *, mode: str = "direct", condition_note: str | None = None,
    width_mm: float = 89, height_mm: float = 65,
    style: str = "forge",
):
    """Plot capacity in the recorded test-step order, including recovery steps."""
    verified_rows(rows, ("series", "step", "rate_label", "capacity", "capacity_unit"))
    comparable = comparison_guard(rows, RATE_CONTEXT, mode=mode, condition_note=condition_note)
    if len({row["capacity_unit"] for row in rows}) != 1:
        raise DataContractError("Capacity units differ; convert with a documented method first")
    groups = _groups(rows)
    reference_steps = None
    fig, ax = make_figure(width_mm, height_mm, style=style)
    colors = colors_for(style)
    for series_index, (name, group) in enumerate(groups.items()):
        points = sorted((number(row["step"], "step", i), row["rate_label"], number(row["capacity"], "capacity", i)) for i, row in group)
        if any(step < 0 or value < 0 for step, _, value in points):
            raise DataContractError("Step and capacity must be non-negative")
        steps = [(step, label) for step, label, _ in points]
        if len({step for step, _ in steps}) != len(steps):
            raise DataContractError(f"Repeated step in series {name!r}; resolve replicates first")
        if reference_steps is None:
            reference_steps = steps
        elif reference_steps != steps:
            raise DataContractError("Rate step sequences differ; split panels or document a mapping")
        ax.plot([p[0] for p in points], [p[2] for p in points],
                color=colors[series_index], linestyle=LINESTYLES[series_index],
                linewidth=fig.batteryplot_linewidth,
                marker=MARKERS[series_index], markersize=3, label=name)
    assert reference_steps is not None
    ax.set_xticks([s for s, _ in reference_steps], [label for _, label in reference_steps])
    ax.set(xlabel="Applied rate (test order)", ylabel=f"Specific capacity ({rows[0]['capacity_unit']})")
    ax.set_ylim(bottom=0)
    ax.legend(frameon=False, loc="best")
    if not comparable:
        condition_banner(fig, condition_note or "")
    _meta(fig, "rate_capability", rows, "direct" if comparable else "contextual")
    return fig, ax


def comparison_bars(
    rows: list[dict], *, metric_label: str, uncertainty_label: str | None = None,
    width_mm: float = 89, height_mm: float = 65,
    style: str = "forge",
):
    """Make a direct comparison only when all declared test conditions match."""
    verified_rows(rows, ("label", "value", "metric_unit"))
    comparison_guard(rows, BAR_CONTEXT)
    if len({row["metric_unit"] for row in rows}) != 1:
        raise DataContractError("Metric units differ")
    if len({row["label"] for row in rows}) != len(rows):
        raise DataContractError("Repeated bar label; aggregate replicates explicitly")
    has_uncertainty = [bool(str(row.get("uncertainty", "")).strip()) for row in rows]
    if any(has_uncertainty) and not all(has_uncertainty):
        raise DataContractError("Uncertainty is missing for some bars; resolve before comparing")
    if any(has_uncertainty) and not uncertainty_label:
        raise DataContractError("Define uncertainty_label (for example SD, SE or 95% CI)")
    values = [number(row["value"], "value", i) for i, row in enumerate(rows, 1)]
    if any(value < 0 for value in values):
        raise DataContractError("Negative values need a signed-axis chart")
    errors = [number(row["uncertainty"], "uncertainty", i) if str(row.get("uncertainty", "")).strip() else 0.0 for i, row in enumerate(rows, 1)]
    if any(error < 0 for error in errors):
        raise DataContractError("Uncertainty magnitudes must be non-negative")
    if len(rows) > 5:
        raise DataContractError("Split more than five bars into panels at this size")
    fig, ax = make_figure(width_mm, height_mm, style=style)
    colors = colors_for(style)
    theme = theme_for(style)
    positions = range(len(rows))
    bars = ax.bar(positions, values, yerr=errors if any(errors) else None,
           color=colors[:len(rows)], edgecolor=theme["ink"], linewidth=0.6,
           error_kw={"elinewidth": 0.7, "capsize": 2})
    for bar, hatch in zip(bars, ("", "/", ".", "x", "-")):
        bar.set_hatch(hatch)
    ax.set_xticks(list(positions), [str(row["label"]) for row in rows], rotation=20, ha="right")
    ax.set(ylabel=f"{metric_label} ({rows[0]['metric_unit']})")
    ax.set_ylim(bottom=0)
    if uncertainty_label:
        ax.text(0.98, 0.98, f"Error bars: {uncertainty_label}", transform=ax.transAxes,
                ha="right", va="top", fontsize=6)
    _meta(fig, "comparison_bars", rows, "direct")
    return fig, ax


def conditions_matrix(
    rows: list[dict], fields: tuple[str, ...], *, label_field: str = "label",
    width_mm: float = 130, height_mm: float | None = None,
    style: str = "forge",
):
    """Show which conditions are reported, checked-unreported (NR), or unverified (NV).

    The matrix shows reporting status, never the numerical values themselves.
    """
    if not fields or len(set(fields)) != len(fields):
        raise DataContractError("Provide distinct condition fields")
    require_fields(rows, ("source_id", label_field) + fields)
    if len({str(row[label_field]) for row in rows}) != len(rows):
        raise DataContractError("Matrix row labels must be unique")
    codes = []
    for row in rows:
        codes.append([0 if str(row[field]).strip().upper() == "NV" else
                      1 if str(row[field]).strip().upper() == "NR" else 2 for field in fields])
    height = height_mm or max(45.0, 13.0 + 7.0 * len(rows))
    fig, ax = make_figure(width_mm, height, style=style)
    theme = theme_for(style)
    cmap = ListedColormap((theme["pastels"]["rust"], "#B8C0C4",
                           theme["roles"]["new_or_intervention"]))
    ax.imshow(codes, vmin=-0.5, vmax=2.5, cmap=cmap, aspect="auto", interpolation="nearest")
    ax.set_xticks(range(len(fields)), [field.replace("_", " ") for field in fields], rotation=35, ha="right")
    ax.set_yticks(range(len(rows)), [str(row[label_field]) for row in rows])
    for i, code_row in enumerate(codes):
        for j, code in enumerate(code_row):
            ax.text(j, i, ("NV", "NR", "R")[code], ha="center", va="center",
                    color="white" if code == 2 else theme["ink"], fontsize=6)
    ax.set_xticks([x - 0.5 for x in range(1, len(fields))], minor=True)
    ax.set_yticks([y - 0.5 for y in range(1, len(rows))], minor=True)
    ax.grid(which="minor", color="white", linewidth=1)
    ax.tick_params(which="minor", bottom=False, left=False)
    ax.legend(handles=[Patch(facecolor=theme["roles"]["new_or_intervention"], label="Reported"),
                       Patch(facecolor="#B8C0C4", label="NR: checked, not reported"),
                       Patch(facecolor=theme["pastels"]["rust"], label="NV: not verified")],
              loc="upper center", bbox_to_anchor=(0.5, -0.38), ncol=3, frameon=False)
    _meta(fig, "conditions_matrix", rows, "not_applicable")
    return fig, ax
