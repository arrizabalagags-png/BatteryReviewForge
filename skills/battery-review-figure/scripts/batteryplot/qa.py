"""Check actual data artists before export; independent scatter stays scatter."""
from __future__ import annotations


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
            # Errorbar caps describe uncertainty, not a sampled continuous curve.
            if line.get_linestyle() in ("None", "", " "):
                continue
            if line.get_linestyle() != "-" or line.get_marker() not in (None, "None", "", " "):
                raise ValueError(f"Data panel {index} continuous curves must be solid without point markers")
            curves.append({"label": line.get_label(), "linestyle": line.get_linestyle(),
                           "marker": line.get_marker(), "points": len(line.get_xdata())})
        checks.append({"panel_index": index, "spines": spines, "continuous_curves": curves})
    return checks
