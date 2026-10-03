"""Check actual data artists before export; independent scatter stays scatter."""
from __future__ import annotations
from .series_policy import check_series_policy


def data_plot_checks(fig):
    checks = []
    for index, ax in enumerate(fig.axes):
        if not ax.axison or hasattr(ax, "_colorbar"):
            continue
        spines = {side: bool(ax.spines[side].get_visible()) for side in ("top", "right", "bottom", "left")}
        if not all(spines.values()):
            raise ValueError(f"Data panel {index} must show top/right/bottom/left frame spines")
        curves = []
        for line in ax.lines:
            sampling = check_series_policy(ax, line)
            curves.append({"label": line.get_label(), "linestyle": line.get_linestyle(),
                           "marker": line.get_marker(), "points": len(line.get_xdata()), "sampling": sampling})
        checks.append({"panel_index": index, "spines": spines, "continuous_curves": curves})
    return checks
