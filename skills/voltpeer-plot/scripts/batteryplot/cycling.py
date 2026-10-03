"""Cycle quantity accounting with an explicitly declared reference record."""
from __future__ import annotations
from collections import defaultdict
import math
from .data import DataContractError, number


def full_cell_quantities(rows):
    """Validate capacity/CE/retention using the same sample and recorded cycles.

The function never selects a reference automatically, clips CE, or equates
CE compounding to capacity retention. Supplied charge values stay untouched.
"""
    groups = defaultdict(list)
    for index, row in enumerate(rows, 1):
        groups[str(row["series"])].append((index, row))
    result, references = [], {}
    for sample, group in groups.items():
        reference_fields = ("reference_cycle", "reference_capacity", "retention_basis")
        if any(any(not str(row.get(f, "")).strip() for f in reference_fields) for _, row in group):
            raise DataContractError(f"{sample}: full-cell cycling needs explicit reference_cycle, reference_capacity and retention_basis; no first-cycle default")
        if any(len({str(row[f]) for _, row in group}) != 1 for f in reference_fields):
            raise DataContractError(f"{sample}: retention reference changes within one series")
        first_index, first = group[0]
        ref = number(first["reference_cycle"], "reference_cycle", first_index)
        qref = number(first["reference_capacity"], "reference_capacity", first_index)
        if ref < 0 or not ref.is_integer() or qref <= 0:
            raise DataContractError(f"{sample}: reference cycle must be an integer and reference capacity positive")
        reference_rows = [(i, r) for i, r in group if number(r["cycle"], "cycle", i) == ref]
        if len(reference_rows) != 1:
            raise DataContractError(f"{sample}: provide the declared reference-cycle record; no inferred external baseline")
        ri, reference = reference_rows[0]
        if not math.isclose(qref, number(reference["discharge_capacity"], "discharge_capacity", ri), rel_tol=1e-6, abs_tol=1e-8):
            raise DataContractError(f"{sample}: reference_capacity does not match the declared source cycle")
        if str(first.get("ce_definition", "")).strip().casefold() not in {
            "discharge capacity / charge capacity", "q_discharge / q_charge", "qdis/qcharge"
        }:
            raise DataContractError(f"{sample}: full-cell CE definition must explicitly be discharge capacity / charge capacity")
        for index, row in group:
            for field in ("rate", "temperature_c", "voltage_window_v", "capacity_unit", "capacity_basis"):
                if str(row.get(field, "")).strip() != str(reference.get(field, "")).strip():
                    raise DataContractError(f"{sample}: retention uses different {field} from its reference; split conditions")
            qdis = number(row["discharge_capacity"], "discharge_capacity", index)
            supplied = str(row.get("ce_pct", "")).strip()
            charge = str(row.get("charge_capacity", "")).strip()
            if not supplied and not charge:
                raise DataContractError(f"{sample}: full-cell cycling needs measured CE or same-cycle charge_capacity; capacity alone cannot supply CE")
            qcharge = number(charge, "charge_capacity", index) if charge else None
            if qcharge is not None and qcharge <= 0:
                raise DataContractError("Full-cell charge capacity must be positive")
            ce = number(supplied, "ce_pct", index) if supplied else 100*qdis/qcharge
            if qcharge is not None and not math.isclose(ce, 100*qdis/qcharge, rel_tol=1e-5, abs_tol=1e-5):
                raise DataContractError(f"{sample}: supplied CE disagrees with the same-cycle charge ledger")
            if not 0 <= ce <= 200:
                raise DataContractError(f"{sample}: CE needs source review; values are never clipped")
            result.append({**row, "ce_pct": ce, "retention_pct": 100*qdis/qref})
        references[sample] = {"reference_cycle": int(ref), "reference_capacity": qref,
                              "capacity_unit": first["capacity_unit"], "capacity_basis": first["capacity_basis"],
                              "retention_basis": first["retention_basis"], "rate": first["rate"]}
    return result, references
