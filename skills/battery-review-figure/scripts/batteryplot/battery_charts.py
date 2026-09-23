"""Battery test plots with explicit cell boundary and measurement contracts."""

from __future__ import annotations

from collections import defaultdict

from .data import DataContractError, comparison_guard, number, verified_rows
from .style import COLORS, LINESTYLES, MARKERS, condition_banner, make_figure


COMMON = ("chemistry", "cell_configuration", "temperature_c")
CYCLING = COMMON + ("capacity_basis", "capacity_unit", "rate", "voltage_window_v")
CE = COMMON + ("ce_definition", "rate")
SYMMETRIC = COMMON + ("current_density_ma_cm2", "areal_capacity_mah_cm2")
CURVE = COMMON + ("capacity_basis", "capacity_unit", "rate", "voltage_window_v")
EIS = COMMON + ("cell_state", "frequency_range_hz")


def _context(rows: list[dict], required: tuple[str, ...], optional: tuple[str, ...],
             mode: str, condition_note: str | None) -> bool:
    """Compare declared conditions; optional fields cannot silently change within a panel."""
    comparable = comparison_guard(rows, required, mode=mode, condition_note=condition_note)
    differences = {}
    for field in optional:
        values = [str(row.get(field, "")).strip() for row in rows]
        if not any(values):
            continue
        if any(not value or value.upper() in {"NR", "NV"} for value in values):
            raise DataContractError(f"{field} is only partly known; resolve it or split the figure")
        if len(set(values)) > 1:
            differences[field] = sorted(set(values))
    if differences and mode == "direct":
        raise DataContractError(f"Direct comparison blocked: declared conditions differ: {differences}")
    if differences and not condition_note:
        raise DataContractError("Contextual comparison of unlike conditions requires condition_note")
    return comparable and not differences


def _series(rows: list[dict]) -> dict[str, list[tuple[int, dict]]]:
    groups: dict[str, list[tuple[int, dict]]] = defaultdict(list)
    for index, row in enumerate(rows, 1):
        groups[str(row["series"])].append((index, row))
    if len(groups) > len(COLORS):
        raise DataContractError(f"At most {len(COLORS)} series fit this final-size preset; split panels")
    return dict(groups)


def _meta(fig, chart: str, rows: list[dict], comparable: bool, *, note: str = "") -> None:
    fig.batteryplot_meta = {
        "chart": chart,
        "source_ids": sorted({str(row["source_id"]).strip() for row in rows}),
        "comparison": "direct" if comparable else "contextual",
        "row_count": len(rows),
        "calculation_note": note,
    }


def _ordered_xy(group: list[tuple[int, dict]], xfield: str, yfield: str, series: str,
                *, unique_x: bool = True) -> tuple[list[float], list[float]]:
    points = [(number(row[xfield], xfield, index), number(row[yfield], yfield, index))
              for index, row in group]
    if any(points[i][0] > points[i + 1][0] for i in range(len(points) - 1)):
        raise DataContractError(f"{xfield} goes backwards in series {series!r}; check source order before plotting")
    if unique_x and len({x for x, _ in points}) != len(points):
        raise DataContractError(f"Repeated {xfield} in series {series!r}; resolve replicates or steps first")
    return [x for x, _ in points], [y for _, y in points]


def cycling_capacity(
    rows: list[dict], *, cell_configuration: str, mode: str = "direct",
    condition_note: str | None = None, width_mm: float = 89, height_mm: float = 65,
):
    """Plot measured discharge capacity against cycle for a declared cell type."""
    if cell_configuration not in {"full", "half"}:
        raise DataContractError("cell_configuration must be 'full' or 'half'")
    verified_rows(rows, ("series", "cycle", "discharge_capacity"))
    expected = {"full": "full cell", "half": "half cell"}[cell_configuration]
    if any(str(row.get("cell_configuration", "")).strip().lower() != expected for row in rows):
        raise DataContractError(f"All rows must declare cell_configuration={expected!r}")
    comparable = _context(rows, CYCLING,
                          ("loading_mg_cm2", "electrolyte_ul_mg", "np_ratio", "cell_format",
                           "formation_protocol", "pressure_mpa"), mode, condition_note)
    units = {str(row["capacity_unit"]).strip() for row in rows}
    if len(units) != 1:
        raise DataContractError("Capacity units differ")
    fig, ax = make_figure(width_mm, height_mm)
    for i, (name, group) in enumerate(_series(rows).items()):
        xs, ys = _ordered_xy(group, "cycle", "discharge_capacity", name)
        if min(xs) < 0 or min(ys) < 0:
            raise DataContractError("Cycle and discharge capacity must be non-negative")
        ax.plot(xs, ys, color=COLORS[i], linestyle=LINESTYLES[i],
                marker=MARKERS[i], markersize=2.7,
                markevery=max(1, len(xs) // 30), label=name)
    ax.set(xlabel="Cycle number", ylabel=f"Discharge capacity ({next(iter(units))})")
    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)
    ax.legend(frameon=False)
    if not comparable:
        condition_banner(fig, condition_note or "")
    _meta(fig, f"{cell_configuration}_cell_cycling", rows, comparable)
    return fig, ax


def coulombic_efficiency(
    rows: list[dict], *, mode: str = "direct", condition_note: str | None = None,
    width_mm: float = 89, height_mm: float = 65,
):
    """Plot CE as supplied or calculate an explicitly defined numerator/denominator ratio."""
    verified_rows(rows, ("series", "cycle"))
    comparable = _context(rows, CE,
                          ("current_density_ma_cm2", "areal_capacity_mah_cm2", "cutoff_rule",
                           "ce_protocol", "loading_mg_cm2", "electrolyte_ul_mg", "voltage_window_v"),
                          mode, condition_note)
    supplied = [str(row.get("ce_pct", "")).strip() != "" for row in rows]
    if any(supplied) and not all(supplied):
        raise DataContractError("Do not mix supplied and recalculated CE within one panel")
    prepared = []
    for index, row in enumerate(rows, 1):
        if supplied[0]:
            value = number(row["ce_pct"], "ce_pct", index)
        else:
            if not all(str(row.get(key, "")).strip() for key in ("ce_numerator", "ce_denominator")):
                raise DataContractError("Calculating CE needs ce_numerator and ce_denominator on every row")
            denominator = number(row["ce_denominator"], "ce_denominator", index)
            numerator = number(row["ce_numerator"], "ce_numerator", index)
            if denominator <= 0 or numerator < 0:
                raise DataContractError("CE denominator must be positive and numerator non-negative")
            value = 100 * numerator / denominator
        if not 0 <= value <= 200:
            raise DataContractError(f"Row {index}: CE {value:g}% needs source review; no value is clipped")
        prepared.append({**row, "ce_pct": value})
    fig, ax = make_figure(width_mm, height_mm)
    for i, (name, group) in enumerate(_series(prepared).items()):
        xs, ys = _ordered_xy(group, "cycle", "ce_pct", name)
        if min(xs) < 0:
            raise DataContractError("Cycle number must be non-negative")
        ax.plot(xs, ys, color=COLORS[i], linestyle=LINESTYLES[i],
                marker=MARKERS[i], markersize=2.7,
                markevery=max(1, len(xs) // 30), label=name)
    ax.set(xlabel="Cycle number", ylabel="Coulombic efficiency (%)")
    ax.set_xlim(left=0)
    # A zoom is allowed only when the visible axis clearly displays it.
    if min(row["ce_pct"] for row in prepared) >= 90 and max(row["ce_pct"] for row in prepared) <= 105:
        ax.set_ylim(90, 105)
    else:
        ax.set_ylim(bottom=0)
    ax.legend(frameon=False)
    if not comparable:
        condition_banner(fig, condition_note or "")
    _meta(fig, "coulombic_efficiency", rows, comparable,
          note="supplied CE" if supplied[0] else "CE = 100 × ce_numerator / ce_denominator")
    return fig, ax


def symmetric_voltage(
    rows: list[dict], *, mode: str = "direct", condition_note: str | None = None,
    width_mm: float = 89, height_mm: float = 65,
):
    """Plot signed two-electrode voltage versus elapsed time, without smoothing."""
    verified_rows(rows, ("series", "time_h", "voltage_mv"))
    if any("symmetric" not in str(row.get("cell_configuration", "")).lower() for row in rows):
        raise DataContractError("Symmetric voltage rows need a declared symmetric cell")
    comparable = _context(rows, SYMMETRIC,
                          ("pressure_mpa", "electrolyte_ul_mg", "separator", "failure_rule",
                           "cell_format"), mode, condition_note)
    fig, ax = make_figure(width_mm, height_mm)
    for i, (name, group) in enumerate(_series(rows).items()):
        xs, ys = _ordered_xy(group, "time_h", "voltage_mv", name, unique_x=False)
        if min(xs) < 0:
            raise DataContractError("Elapsed time must be non-negative")
        ax.plot(xs, ys, color=COLORS[i], linestyle=LINESTYLES[i], linewidth=1, label=name)
    ax.axhline(0, color="#8A969C", linewidth=0.65)
    ax.set(xlabel="Elapsed time (h)", ylabel="Cell voltage (mV)")
    ax.set_xlim(left=0)
    ax.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, 1.20), ncol=2)
    if not comparable:
        condition_banner(fig, condition_note or "")
    _meta(fig, "symmetric_cell_voltage", rows, comparable)
    return fig, ax


def voltage_capacity(
    rows: list[dict], *, mode: str = "direct", condition_note: str | None = None,
    width_mm: float = 89, height_mm: float = 65,
):
    """Plot charge/discharge voltage profiles; preserve direction and cycle labels."""
    verified_rows(rows, ("series", "cycle", "direction", "capacity", "voltage_v"))
    comparable = _context(rows, CURVE,
                          ("loading_mg_cm2", "electrolyte_ul_mg", "np_ratio", "cell_format"),
                          mode, condition_note)
    if len({str(row["capacity_unit"]).strip() for row in rows}) != 1:
        raise DataContractError("Capacity units differ")
    if any(row["direction"] not in {"charge", "discharge"} for row in rows):
        raise DataContractError("direction must be charge or discharge")
    traces: dict[tuple[str, str, str], list[tuple[int, dict]]] = defaultdict(list)
    for index, row in enumerate(rows, 1):
        traces[(str(row["series"]), str(row["cycle"]), str(row["direction"]))].append((index, row))
    if len(traces) > 10:
        raise DataContractError("More than 10 traces will be unreadable at this size; split panels")
    names = list(dict.fromkeys(key[0] for key in traces))
    if len(names) > len(COLORS):
        raise DataContractError("Too many series for the palette")
    fig, ax = make_figure(width_mm, height_mm)
    for (name, cycle, direction), group in traces.items():
        xs, ys = _ordered_xy(group, "capacity", "voltage_v", f"{name} cycle {cycle} {direction}", unique_x=False)
        if min(xs) < 0:
            raise DataContractError("Capacity must be non-negative")
        i = names.index(name)
        ax.plot(xs, ys, color=COLORS[i],
                linestyle="-" if direction == "discharge" else "--",
                linewidth=1.35, label=f"{name} · cycle {cycle} · {direction}")
    ax.set(xlabel=f"Capacity ({rows[0]['capacity_unit']})", ylabel="Voltage (V)")
    ax.set_xlim(left=0)
    ax.legend(frameon=False, fontsize=5.5)
    if not comparable:
        condition_banner(fig, condition_note or "")
    _meta(fig, "voltage_capacity", rows, comparable)
    return fig, ax


def nyquist(
    rows: list[dict], *, mode: str = "direct", condition_note: str | None = None,
    width_mm: float = 89, height_mm: float = 65,
):
    """Plot Nyquist data with an explicitly positive -Im(Z) column."""
    verified_rows(rows, ("series", "z_real_ohm", "minus_z_imag_ohm"))
    comparable = _context(rows, EIS,
                          ("perturbation_mv", "electrolyte_ul_mg", "pressure_mpa"),
                          mode, condition_note)
    fig, ax = make_figure(width_mm, height_mm)
    for i, (name, group) in enumerate(_series(rows).items()):
        xs = [number(row["z_real_ohm"], "z_real_ohm", index) for index, row in group]
        ys = [number(row["minus_z_imag_ohm"], "minus_z_imag_ohm", index) for index, row in group]
        ax.plot(xs, ys, color=COLORS[i], marker=MARKERS[i], linestyle=LINESTYLES[i],
                markersize=2.6, label=name)
    ax.set(xlabel="Re(Z) (Ω)", ylabel="−Im(Z) (Ω)")
    ax.set_aspect("equal", adjustable="datalim")
    ax.legend(frameon=False)
    if not comparable:
        condition_banner(fig, condition_note or "")
    _meta(fig, "nyquist", rows, comparable)
    return fig, ax
