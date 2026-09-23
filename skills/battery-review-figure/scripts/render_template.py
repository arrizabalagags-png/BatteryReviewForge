"""Recolor original editable SVG templates with a selected figure style."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from batteryplot.style import DEFAULT_STYLE, PRESETS, THEME, get_preset

ORIGINALS = Path(__file__).resolve().parents[1] / "assets" / "original"
COLOR = re.compile(r"#[0-9a-fA-F]{6}\b")


def darken(value: str, factor: float = 0.78) -> str:
    channels = [round(int(value[index:index + 2], 16) * factor) for index in (1, 3, 5)]
    return "#" + "".join(f"{channel:02X}" for channel in channels)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--list", action="store_true", help="List supported original templates")
    parser.add_argument("--template", choices=sorted(p.stem for p in ORIGINALS.glob("*.svg")))
    parser.add_argument("--style", choices=sorted(PRESETS))
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    if args.list:
        for name in sorted(p.stem for p in ORIGINALS.glob("*.svg")):
            print(name)
        return
    if not args.template or not args.style or not args.out:
        parser.error("Choose --template, --style and --out; do not silently guess a manuscript style")
    preset = get_preset(args.style)
    source = ORIGINALS / f"{args.template}.svg"
    source_colors = {**THEME["roles"], **THEME["pastels"],
                     "ink": THEME["ink"], "muted_ink": THEME["muted_ink"], "grid": THEME["grid"]}
    destination_colors = {**preset["roles"], **preset["pastels"],
                          "ink": THEME["ink"], "muted_ink": THEME["muted_ink"], "grid": THEME["grid"]}
    substitutions = {source_colors[key].lower(): destination_colors[key]
                     for key in source_colors}
    substitutions.update({
        "#174a69": darken(preset["roles"]["reference_or_baseline"]),
        "#286b60": darken(preset["roles"]["new_or_intervention"]),
        "#6b557d": darken(preset["roles"]["mechanism_or_model"]),
        "#adc6ee": preset["pastels"]["blue"],
    })
    original = source.read_text(encoding="utf-8")
    recolored = COLOR.sub(lambda match: substitutions.get(match.group().lower(), match.group()), original)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(recolored, encoding="utf-8")
    print(f"{args.template}: {DEFAULT_STYLE} → {args.style}: {args.out}")


if __name__ == "__main__":
    main()
