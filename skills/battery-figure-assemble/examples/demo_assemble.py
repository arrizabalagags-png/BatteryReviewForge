"""Generate an explicitly synthetic three-panel composition and its sources."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw
from reportlab.pdfgen import canvas


def make_demo(root: Path) -> Path:
    sources = root / "sources"
    sources.mkdir(parents=True, exist_ok=True)
    hero = sources / "demo_schematic.pdf"
    pdf = canvas.Canvas(str(hero), pagesize=(720, 210))
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(24, 180, "SYNTHETIC DEMO: evidence chain")
    for i, (label, color) in enumerate((
        ("Cell boundary", (0.15, 0.34, 0.50)),
        ("Test condition", (0.25, 0.52, 0.47)),
        ("Measured trend", (0.69, 0.36, 0.28)),
    )):
        x = 26 + i * 230
        pdf.setFillColorRGB(*color)
        pdf.roundRect(x, 55, 190, 82, 9, stroke=0, fill=1)
        pdf.setFillColorRGB(1, 1, 1)
        pdf.setFont("Helvetica-Bold", 15)
        pdf.drawCentredString(x + 95, 95, label)
        if i < 2:
            pdf.setFillColorRGB(0.2, 0.2, 0.2)
            pdf.line(x + 194, 96, x + 226, 96)
    pdf.save()

    image = Image.new("RGB", (1200, 680), "white")
    draw = ImageDraw.Draw(image)
    draw.line((115, 80, 115, 570, 1090, 570), fill="#26343D", width=4)
    draw.line((145, 210, 380, 250, 610, 325, 835, 370, 1060, 402), fill="#205C85", width=9, joint="curve")
    for x, y in ((145, 210), (380, 250), (610, 325), (835, 370), (1060, 402)):
        draw.ellipse((x - 10, y - 10, x + 10, y + 10), fill="#205C85")
    image.save(sources / "demo_trend.png", dpi=(600, 600))

    svg = sources / "demo_matrix.svg"
    svg.write_text('''<svg xmlns="http://www.w3.org/2000/svg" width="600" height="340" viewBox="0 0 600 340">
<rect width="600" height="340" fill="white"/>
<g font-family="Arial,sans-serif" fill="#26343D" font-size="22">
<text x="24" y="38">SYNTHETIC DEMO - reporting matrix</text>
<text x="35" y="143">A</text><text x="35" y="251">B</text>
</g>
<rect x="90" y="72" width="145" height="110" fill="#4C8B85"/>
<rect x="240" y="72" width="145" height="110" fill="#B8C0C4"/>
<rect x="390" y="72" width="145" height="110" fill="#EEE6DF"/>
<rect x="90" y="188" width="145" height="110" fill="#B8C0C4"/>
<rect x="240" y="188" width="145" height="110" fill="#4C8B85"/>
<rect x="390" y="188" width="145" height="110" fill="#EEE6DF"/>
<g font-family="Arial,sans-serif" fill="#26343D" font-size="22" text-anchor="middle">
<text x="162" y="135">R</text><text x="312" y="135">NR</text><text x="462" y="135">NV</text>
<text x="162" y="250">NR</text><text x="312" y="250">R</text><text x="462" y="250">NV</text>
</g></svg>''', encoding="utf-8")

    manifest = {
        "version": 1, "figure_id": "DEMO Fig. 1",
        "claim": "SYNTHETIC DEMO — three visual roles illustrate a reproducible figure assembly.",
        "width_mm": 180, "margin_mm": 4, "gutter_mm": 3,
        "label_band_mm": 4.5, "row_heights_mm": [42, 48], "col_weights": [1, 1],
        "dpi": 300, "min_effective_dpi": 300,
        "panels": [
            {"label": "a", "path": "sources/demo_schematic.pdf", "row": 0, "col": 0,
             "colspan": 2, "role": "synthetic overview", "source_id": "SYNTHETIC-ONLY",
             "rights_status": "original", "crop_box_fraction": [0.015, 0.04, 0.985, 0.78],
             "alignment_intent": "independent", "alignment_reason": "Overview schematic has no plotted axes",
             "crop_reason": "Remove only authored PDF page whitespace; retain all lettering and blocks"},
            {"label": "b", "path": "sources/demo_trend.png", "row": 1, "col": 0,
             "role": "synthetic trend", "source_id": "SYNTHETIC-ONLY",
             "rights_status": "original", "alignment_intent": "independent",
             "alignment_reason": "Trend and adjacent reporting matrix use different coordinate systems"},
            {"label": "c", "path": "sources/demo_matrix.svg", "row": 1, "col": 1,
             "role": "synthetic reporting matrix", "source_id": "SYNTHETIC-ONLY",
             "rights_status": "original", "alignment_intent": "independent",
             "alignment_reason": "Categorical matrix is not an axes comparison with the trend"},
        ],
    }
    manifest_path = root / "demo_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest_path


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python demo_assemble.py OUTPUT_DIRECTORY")
    root = Path(sys.argv[1]).resolve()
    manifest_path = make_demo(root)
    script = Path(__file__).resolve().parents[1] / "scripts" / "compose_figure.py"
    subprocess.run([sys.executable, str(script), "inventory", "--input", str(root / "sources"),
                    "--output", str(root / "inventory")], check=True)
    subprocess.run([sys.executable, str(script), "compose", "--manifest", str(manifest_path),
                    "--out", str(root / "composite")], check=True)
