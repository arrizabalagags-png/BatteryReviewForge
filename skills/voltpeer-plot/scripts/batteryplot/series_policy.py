"""Project display choices, resolved from the quantity and sampling axis.

Cycle records are discrete observations. This is the author's selected style,
not a claim that every journal mandates scatter. Arrays are never rewritten.
"""
from __future__ import annotations

import re
import numpy as np


EMPTY = (None, "None", "", " ")


def cycle_quantity(ax):
    x = ax.get_xlabel().casefold()
    y = ax.get_ylabel().casefold()
    if "cycle" not in x and "循环" not in x:
        # twinx owns a separate empty xlabel even though it uses the same
        # cycle coordinates. Resolve the real shared-axis contract first.
        siblings=ax.get_shared_x_axes().get_siblings(ax)
        x=" ".join(sibling.get_xlabel().casefold() for sibling in siblings)
    if "cycle" not in x and "循环" not in x:
        return None
    if "retention" in y or "保持率" in y:
        return "retention"
    if "capacity" in y or "容量" in y:
        return "capacity"
    if "coulombic" in y or re.search(r"\bce\b", y) or "efficiency" in y or "效率" in y:
        return "efficiency"
    if "charge" in y or "电荷" in y:
        return "charge_ledger"
    if "retained inventory" in y:
        return "inventory_model"
    return None


def reference_or_cap(ax,artist):
    """Explicit guide/cap identity, never the length of an observation array."""
    if (artist.get_gid() or '').startswith('voltpeer-reference:'):
        return True
    if artist.get_transform() is not ax.transData:
        return True  # axhline/axvline use blended data/axes coordinates.
    if artist.get_linestyle() in EMPTY and artist.get_marker() in ('_','|') and artist.get_label()=='_nolegend_':
        return True  # errorbar cap; the mean observation uses another artist.
    return False


def apply_series_policy(ax):
    """Apply marker-only cycle styling while keeping every original array."""
    quantity = cycle_quantity(ax)
    if quantity is None:
        return
    for artist in ax.lines:
        # One/two real observations remain visible. Explicit transforms/gids
        # and cap artists identify references; array length cannot do that.
        if len(artist.get_xdata()) == 0:
            continue
        if reference_or_cap(ax,artist):
            if artist.get_transform() is not ax.transData or (artist.get_gid() or '').startswith('voltpeer-reference:'):
                artist.set_linestyle('-')
                artist.set_marker('None')
            continue
        x, y = np.array(artist.get_xdata(), copy=True), np.array(artist.get_ydata(), copy=True)
        artist.set_linestyle("None")
        artist.set_marker("o")
        artist.set_markersize(2.7)
        artist.set_markeredgewidth(.55)
        artist.set_markerfacecolor("none" if quantity == "efficiency" else artist.get_color())
        axis_index=list(ax.figure.axes).index(ax)
        line_index=list(ax.lines).index(artist)
        artist.set_gid(f"voltpeer-cycle:axis{axis_index}:line{line_index}:" + quantity)
        if not np.array_equal(x, artist.get_xdata()) or not np.array_equal(y, artist.get_ydata()):
            raise ValueError("Cycle display styling changed source values")
    legend = ax.get_legend()
    if legend is not None:
        handles = getattr(legend, "legend_handles", getattr(legend, "legendHandles", []))
        labels=[text.get_text() for text in legend.get_texts()]
        sources={line.get_label():line for line in ax.lines}
        for handle,label in zip(handles,labels):
            if hasattr(handle, "set_marker"):
                source=sources.get(label)
                if source is not None:
                    handle.set_linestyle(source.get_linestyle())
                    handle.set_marker(source.get_marker())
                    handle.set_markersize(3)
                    handle.set_markerfacecolor(source.get_markerfacecolor())


def check_series_policy(ax, artist):
    """Verify the actual artist, including observations with only two cycles."""
    quantity = cycle_quantity(ax)
    if reference_or_cap(ax,artist):
        if artist.get_transform() is not ax.transData or (artist.get_gid() or '').startswith('voltpeer-reference:'):
            if artist.get_linestyle()!='-' or artist.get_marker() not in EMPTY:
                raise ValueError('Reference guides must be solid and unmarked')
            return 'reference_solid'
        return 'uncertainty_caps'
    if quantity is not None and len(artist.get_xdata()) >= 1:
        if artist.get_linestyle() not in EMPTY or artist.get_marker() in EMPTY:
            raise ValueError(f"{quantity} cycle records must be marker-only; no connecting lines")
        return "cycle_scatter"
    if artist.get_linestyle() in EMPTY:
        return "independent_or_uncertainty_marks"
    if artist.get_linestyle() != "-" or artist.get_marker() not in EMPTY:
        raise ValueError("Continuous traces must be solid and unmarked")
    return "continuous_solid"
