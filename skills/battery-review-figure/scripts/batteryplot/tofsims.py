"""Draw ToF-SIMS ion maps and depth traces from author-labelled tables.

Signal intensity is never converted to composition, concentration or physical
depth here. A different instrument export needs an explicit column mapping.
"""

from __future__ import annotations

from collections import defaultdict

import numpy as np
import matplotlib.pyplot as plt

from .data import DataContractError, number, verified_rows
from .style import colors_for, make_figure


REQUIRED = ("sample_id", "fragment", "signal", "signal_unit", "normalization",
            "ion_polarity", "measurement_state")


def _selection(rows: list[dict], sample_id: str, fragment: str | None = None) -> list[dict]:
    verified_rows(rows, REQUIRED)
    selected = [row for row in rows if str(row["sample_id"]) == sample_id and
                (fragment is None or str(row["fragment"]) == fragment)]
    if not selected:
        raise DataContractError("No rows match the selected sample_id/fragment")
    for field in ("source_id", "signal_unit", "normalization", "ion_polarity", "measurement_state"):
        if len({str(row[field]).strip() for row in selected}) != 1:
            raise DataContractError(f"Selected ToF-SIMS rows disagree on {field}; split the figure")
    for index, row in enumerate(selected, 1):
        if number(row["signal"], "signal", index) < 0:
            raise DataContractError("ToF-SIMS signal must be non-negative")
    return selected


def tofsims_map(rows: list[dict], *, sample_id: str, fragment: str,
                width_mm: float = 89, height_mm: float = 78, style: str = "forge"):
    """Show a complete regular x/y ion image with source-calibrated µm coordinates."""
    selected = _selection(rows, sample_id, fragment)
    verified_rows(selected, ("x_um", "y_um"))
    xs = sorted({number(row["x_um"], "x_um", i) for i, row in enumerate(selected, 1)})
    ys = sorted({number(row["y_um"], "y_um", i) for i, row in enumerate(selected, 1)})
    if len(xs) < 2 or len(ys) < 2:
        raise DataContractError("An ion map needs at least two calibrated x and y positions")
    if len(xs) * len(ys) != len(selected):
        raise DataContractError("Incomplete or duplicate x/y ion grid; provide one value per pixel")
    dx, dy = np.diff(xs), np.diff(ys)
    if not (np.allclose(dx, dx[0], rtol=1e-4, atol=1e-8) and
            np.allclose(dy, dy[0], rtol=1e-4, atol=1e-8)):
        raise DataContractError("Ion map coordinates are not a regular calibrated grid")
    matrix = np.full((len(ys), len(xs)), np.nan)
    xidx, yidx = {v:i for i,v in enumerate(xs)}, {v:i for i,v in enumerate(ys)}
    for i,row in enumerate(selected, 1):
        x,y = number(row["x_um"], "x_um", i), number(row["y_um"], "y_um", i)
        if np.isfinite(matrix[yidx[y],xidx[x]]):
            raise DataContractError("Duplicate x/y ion pixel")
        matrix[yidx[y],xidx[x]] = number(row["signal"], "signal", i)
    if not np.isfinite(matrix).all() or matrix.max() == 0:
        raise DataContractError("Ion map has missing pixels or no positive signal")
    fig, ax = make_figure(width_mm, height_mm, style=style)
    cmap = plt.get_cmap("magma")
    image = ax.imshow(matrix, origin="lower", interpolation="nearest", cmap=cmap,
                      extent=[xs[0]-dx[0]/2, xs[-1]+dx[0]/2,
                              ys[0]-dy[0]/2, ys[-1]+dy[0]/2], vmin=0, vmax=matrix.max())
    ax.set(xlabel="x (µm)", ylabel="y (µm)")
    cbar = fig.colorbar(image, ax=ax, fraction=.048, pad=.03)
    cbar.set_label(f"{fragment} signal ({selected[0]['signal_unit']})")
    fig.batteryplot_meta = {
        "chart":"tofsims_map", "source_ids":[selected[0]["source_id"]], "sample_id":sample_id,
        "fragment":fragment, "normalization":selected[0]["normalization"],
        "ion_polarity":selected[0]["ion_polarity"], "measurement_state":selected[0]["measurement_state"],
        "row_count":len(selected), "comparison":"single_channel", "style":style,
        "calculation_note":"No signal normalization, smoothing or depth conversion performed by the plotter.",
    }
    return fig, ax


def tofsims_depth(rows: list[dict], *, sample_id: str,
                  width_mm: float = 180, height_mm: float = 67, style: str = "forge"):
    """Show ion signal against sputter time without inventing a depth calibration."""
    selected = _selection(rows, sample_id)
    verified_rows(selected, ("sputter_time_s",))
    groups = defaultdict(list)
    for i,row in enumerate(selected, 1):
        groups[str(row["fragment"])].append((number(row["sputter_time_s"],"sputter_time_s",i),
                                              number(row["signal"],"signal",i)))
    colors = colors_for(style)
    if len(groups) > len(colors):
        raise DataContractError("Too many fragments for one readable panel; split the plot")
    time_sets = []
    for name, points in groups.items():
        times = [p[0] for p in points]
        if times != sorted(times) or len(times) != len(set(times)) or min(times) < 0:
            raise DataContractError(f"{name}: sputter times must be ordered, unique and non-negative")
        time_sets.append(times)
    if len(time_sets) > 1 and any(times != time_sets[0] for times in time_sets[1:]):
        raise DataContractError("Fragment traces have different sputter-time grids; align explicitly")
    fig,ax = make_figure(width_mm,height_mm,style=style)
    for i,(name,points) in enumerate(groups.items()):
        ax.plot(*zip(*points),color=colors[i],lw=fig.batteryplot_linewidth,
                linestyle=("-","--","-.",":")[i%4],label=name)
    ax.set(xlabel="Sputter time (s)",ylabel=f"Secondary-ion signal ({selected[0]['signal_unit']})")
    ax.set_xlim(left=0); ax.set_ylim(bottom=0)
    ax.legend(frameon=False,ncol=min(3,len(groups)))
    fig.batteryplot_meta = {
        "chart":"tofsims_depth", "source_ids":[selected[0]["source_id"]], "sample_id":sample_id,
        "fragments":list(groups), "normalization":selected[0]["normalization"],
        "ion_polarity":selected[0]["ion_polarity"], "measurement_state":selected[0]["measurement_state"],
        "row_count":len(selected), "comparison":"within_sample_signals", "style":style,
        "calculation_note":"Plotted supplied signals against sputter time; no physical-depth or composition conversion.",
    }
    return fig,ax
