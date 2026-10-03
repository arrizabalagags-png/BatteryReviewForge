"""Render a synthetic comparison card for every bundled figure style."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

from batteryplot.style import PRESETS
from output_safety import reserve_stem


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True, help="Output basename, without extension")
    args = parser.parse_args()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with plt.rc_context({"font.family": "sans-serif", "font.sans-serif": ["Arial", "DejaVu Sans"],
                         "svg.fonttype": "none", "pdf.fonttype": 42}):
        fig, axes = plt.subplots(2, 3, figsize=(12.5, 7.5), layout="constrained")
        x = [0, 2, 4, 6, 8, 10]
        baseline = [0.38, 0.46, 0.54, 0.57, 0.61, 0.63]
        variant = [0.39, 0.55, 0.62, 0.72, 0.80, 0.86]
        for ax, (name, preset) in zip(axes.flat, PRESETS.items()):
            series = preset["series"]
            ax.plot(x, baseline, color=series[0], linewidth=preset["line_pt"],
                    marker=None, linestyle="-", label="Reference")
            ax.plot(x, variant, color=series[1], linewidth=preset["line_pt"],
                    marker=None, linestyle="-", label="Variant")
            ax.fill_between(x, [v - 0.035 for v in variant], [v + 0.035 for v in variant],
                            color=series[1], alpha=0.13, linewidth=0)
            ax.set(xlim=(-0.3, 10.3), ylim=(0.2, 1.02), xlabel="Cycle index (synthetic)",
                   ylabel="Relative value")
            ax.set_title(f"{preset['label_en']}  ·  {name}", pad=34)
            ax.spines[["top", "right", "bottom", "left"]].set_visible(True)
            ax.tick_params(labelsize=8)
            ax.xaxis.label.set_size(8)
            ax.yaxis.label.set_size(8)
            ax.title.set_size(10)
            ax.legend(loc="lower right", frameon=False, fontsize=7)
            for i, color in enumerate(preset["swatches"]):
                ax.add_patch(Rectangle((i / len(preset["swatches"]), 1.015),
                                       1 / len(preset["swatches"]), 0.045,
                                       transform=ax.transAxes, clip_on=False,
                                       facecolor=color, edgecolor="white", linewidth=0.5))
        fig.suptitle("VoltPeer style choices · invented preview data", fontsize=14)
        with reserve_stem(args.out, ('.svg', '.png')) as (reserved, _):
            for ext in ("svg", "png"):
                fig.savefig(Path(str(reserved) + f'.{ext}'), dpi=300, facecolor="white")
            svg = Path(str(reserved) + '.svg')
            svg.write_text("\n".join(line.rstrip() for line in svg.read_text(encoding="utf-8").splitlines()) + "\n", encoding="utf-8")
        plt.close(fig)
    print(Path(str(reserved) + '.svg'))
    print(Path(str(reserved) + '.png'))


if __name__ == "__main__":
    from cli_runtime import configure_utf8
    configure_utf8()
    main()
