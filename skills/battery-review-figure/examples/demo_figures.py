"""SYNTHETIC DEMO ONLY. These values are not literature or manuscript evidence."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from batteryplot import (  # noqa: E402
    comparison_bars, conditions_matrix, cycle_retention, rate_capability, save_bundle,
)


def context(**extra):
    return {
        "evidence_state": "verified", "chemistry": "DEMO chemistry",
        "cell_configuration": "DEMO coin half-cell", "temperature_c": "25",
        "loading_mg_cm2": "2.0", "electrolyte_ul_mg": "10",
        **extra,
    }


def main(output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    cycle = [
        context(source_id=f"SYNTHETIC-{series}", series=series, cycle=str(cycle_number),
                retention_pct=str(value), retention_basis="initial discharge capacity", reference_cycle="0", rate="1 C")
        for series, values in (("Material A", (100, 91, 82, 75)), ("Material B", (100, 87, 76, 65)))
        for cycle_number, value in zip((0, 100, 200, 300), values)
    ]
    rate = [
        context(source_id=f"SYNTHETIC-{series}", series=series, step=str(step),
                rate_label=label, capacity=str(value), capacity_unit="mAh g$^{-1}$",
                capacity_basis="active-material mass")
        for series, values in (("Material A", (180, 160, 125, 171)),
                               ("Material B", (165, 143, 105, 151)))
        for step, (label, value) in enumerate(zip(("0.1 C", "0.5 C", "2 C", "0.1 C"), values))
    ]
    bars = [
        context(source_id=f"SYNTHETIC-{series}", label=series, value=str(value),
                uncertainty="4", metric_unit="mAh g$^{-1}$", metric_basis="active-material mass", rate="1 C")
        for series, value in (("A", 145), ("B", 132), ("C", 119))
    ]
    matrix = [
        {"source_id": "SYNTHETIC-A", "label": "Demo A", "loading_mg_cm2": "2.0",
         "electrolyte_ul_mg": "NR", "temperature_c": "25", "pressure_mpa": "NV"},
        {"source_id": "SYNTHETIC-B", "label": "Demo B", "loading_mg_cm2": "NR",
         "electrolyte_ul_mg": "8", "temperature_c": "NV", "pressure_mpa": "1"},
    ]
    specs = (
        ("cycle_retention", cycle_retention(cycle), "synthetic in-script cycle data"),
        ("rate_capability", rate_capability(rate), "synthetic in-script rate data"),
        ("comparison_bars", comparison_bars(bars, metric_label="Specific capacity", uncertainty_label="synthetic SD"), "synthetic in-script bar data"),
        ("conditions_matrix", conditions_matrix(matrix, ("loading_mg_cm2", "electrolyte_ul_mg", "temperature_c", "pressure_mpa")), "synthetic in-script matrix data"),
    )
    for name, (fig, _), source in specs:
        save_bundle(fig, output / name, claim="SYNTHETIC DEMO — no scientific claim",
                    source_data=source, caption_notes="Synthetic values for library testing only; never cite.", close=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="Directory for synthetic demo figures")
    args = parser.parse_args()
    main(args.output)
