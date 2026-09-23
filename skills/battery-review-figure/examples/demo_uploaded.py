"""Create SYNTHETIC uploaded tables and render the battery-specific chart routes."""

from __future__ import annotations

import csv
import json
import math
import subprocess
import sys
from pathlib import Path


def write_case(output: Path, kind: str, rows: list[dict], common: dict) -> None:
    data = output / f"{kind}.csv"
    with data.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    mapping = output / f"{kind}.json"
    mapping.write_text(json.dumps({
        "kind": kind,
        "style": "forge",
        "claim": "SYNTHETIC DEMO ONLY — no scientific claim",
        "caption_notes": "Invented values for testing; never cite as experiment or literature.",
        "columns": {}, "common": common,
    }, indent=2) + "\n", encoding="utf-8")
    script = Path(__file__).resolve().parents[1] / "scripts" / "plot_uploaded.py"
    subprocess.run([sys.executable, str(script), "plot", "--data", str(data),
                    "--metadata", str(mapping), "--out", str(output / kind)], check=True)


def main(output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    common = {
        "source_id": "SYNTHETIC-DEMO", "evidence_state": "verified",
        "chemistry": "DEMO battery", "temperature_c": "25", "electrolyte_ul_mg": "10",
        "rate": "1 C", "loading_mg_cm2": "2", "voltage_window_v": "2.5-4.2",
    }
    write_case(output, "coulombic_efficiency",
               [{"series": series, "cycle": cycle,
                 "ce_pct": round(98.5 + offset + 1.2 * (1 - 1 / (cycle + 1)), 3)}
               for series, offset in (("Reference", 0), ("Example", 0.45))
               for cycle in range(1, 11)],
               {**common, "cell_configuration": "half cell",
                "ce_definition": "discharge capacity / charge capacity",
                "current_density_ma_cm2": "1", "areal_capacity_mah_cm2": "1",
                "cutoff_rule": "synthetic fixed cutoff", "ce_protocol": "invented cycling protocol"})
    for kind, cell in (("full_cell_cycling", "full cell"), ("half_cell_cycling", "half cell")):
        write_case(output, kind,
                   [{"series": series, "cycle": cycle,
                     "discharge_capacity": round(start - loss * cycle, 2)}
                    for series, start, loss in (("Reference", 160, 0.45), ("Example", 160, 0.23))
                    for cycle in range(0, 251, 25)],
                   {**common, "cell_configuration": cell,
                    "capacity_basis": "cathode active mass" if cell == "full cell" else "working-electrode active mass",
                    "capacity_unit": "mAh g-1", "np_ratio": "1.1" if cell == "full cell" else "not applicable",
                    "cell_format": "synthetic coin cell", "formation_protocol": "invented three cycles",
                    "pressure_mpa": "0.1"})
    write_case(output, "symmetric_cell_voltage",
               [{"series": series, "time_h": round(i * 0.5, 2),
                 "voltage_mv": (1 if i % 4 < 2 else -1) * amplitude}
                for series, amplitude in (("Reference", 42), ("Example", 25))
                for i in range(41)],
               {**common, "cell_configuration": "Li|Li symmetric cell",
                "current_density_ma_cm2": "1", "areal_capacity_mah_cm2": "1",
                "pressure_mpa": "0.1", "separator": "synthetic separator",
                "failure_rule": "invented cutoff", "cell_format": "synthetic coin cell"})
    write_case(output, "voltage_capacity",
               [{"series": "Example", "cycle": cycle, "direction": direction,
                 "capacity": capacity, "voltage_v": round(voltage, 3)}
                for cycle in (1, 50)
                for direction in ("charge", "discharge")
                for capacity, voltage in (
                    [(x, 3.0 + x * 0.007 + cycle * 0.0006) for x in range(0, 151, 15)]
                    if direction == "charge" else
                    [(x, 4.05 - x * 0.006 - cycle * 0.0005) for x in range(0, 151, 15)]
                )],
               {**common, "cell_configuration": "full cell",
                "capacity_basis": "cathode active mass", "capacity_unit": "mAh g-1"})
    write_case(output, "nyquist",
               [{"series": series, "z_real_ohm": round(center + radius * (1 - math.cos(math.pi * i / 10)), 3),
                 "minus_z_imag_ohm": round(radius * math.sin(math.pi * i / 10), 3)}
                for series, center, radius in (("Reference", 5, 36), ("Example", 5, 24))
                for i in range(11)],
               {**common, "cell_configuration": "full cell",
                "cell_state": "before cycling", "frequency_range_hz": "1e5-0.1",
                "perturbation_mv": "10", "pressure_mpa": "0.1"})


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    main(parser.parse_args().output)
