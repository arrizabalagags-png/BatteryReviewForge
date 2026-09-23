"""Small, strict data contracts. Scientific interpretation remains with the author."""

from __future__ import annotations

import math
from pathlib import Path


class DataContractError(ValueError):
    """The input cannot support the requested visual claim."""


def read_csv(path: str | Path) -> list[dict[str, str]]:
    """Backward-compatible CSV entrypoint using the shared upload parser."""
    if Path(path).suffix.lower() != ".csv":
        raise DataContractError("read_csv accepts .csv only; use read_table for other files")
    from .ingest import read_table
    return read_table(path)


def require_fields(rows: list[dict], fields: tuple[str, ...]) -> None:
    if not rows:
        raise DataContractError("No records supplied")
    for index, row in enumerate(rows, 1):
        for field in fields:
            if field not in row or row[field] is None or not str(row[field]).strip():
                raise DataContractError(f"Row {index}: missing {field}; use NR or NV where appropriate")


def verified_rows(rows: list[dict], fields: tuple[str, ...]) -> None:
    require_fields(rows, ("source_id", "evidence_state") + fields)
    for index, row in enumerate(rows, 1):
        if row["evidence_state"] != "verified":
            raise DataContractError(
                f"Row {index}: evidence_state={row['evidence_state']!r}; quantitative plots need verified values"
            )


def number(value: object, field: str, row: int) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise DataContractError(f"Row {row}: {field} must be numeric, got {value!r}") from exc
    if not math.isfinite(result):
        raise DataContractError(f"Row {row}: {field} must be finite")
    return result


def comparison_guard(
    rows: list[dict],
    fields: tuple[str, ...],
    *,
    mode: str = "direct",
    condition_note: str | None = None,
) -> bool:
    """Return True only for an exact-context direct comparison.

    Contextual plots may display unlike conditions only with an explicit note.
    This is a screening gate, not proof of scientific comparability.
    """
    if mode not in {"direct", "contextual"}:
        raise DataContractError("comparison mode must be 'direct' or 'contextual'")
    require_fields(rows, fields)
    for index, row in enumerate(rows, 1):
        for field in fields:
            if str(row[field]).strip().upper() in {"NR", "NV"}:
                raise DataContractError(
                    f"Row {index}: {field} is {row[field]}; plot reporting status in a conditions matrix"
                )
    differences = {
        field: sorted({str(row[field]).strip() for row in rows})
        for field in fields
        if len({str(row[field]).strip() for row in rows}) > 1
    }
    if differences and mode == "direct":
        raise DataContractError(f"Direct comparison blocked: conditions differ: {differences}")
    if differences and (not condition_note or not condition_note.strip()):
        raise DataContractError("Contextual comparison of unlike conditions requires condition_note")
    return not differences


def source_ids(rows: list[dict]) -> list[str]:
    require_fields(rows, ("source_id",))
    return sorted({str(row["source_id"]).strip() for row in rows})
