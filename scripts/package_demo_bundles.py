"""Package paired synthetic example CSVs for the beginner guide."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "examples" / "showcase"
DEST = ROOT / "docs" / "assets" / "showcase"

BUNDLES = {
    "full-cell": ("full_cell", {"data.csv": "cycling.csv", "voltage_profiles.csv": "voltage_profiles.csv"},
                  "These files are synthetic demonstration data, not experimental results.\nGive both CSV files to BatteryReviewForge. Check columns, units and cell conditions before plotting.\n"),
    "li-cu-ce": ("li_cu_ce", {"data.csv": "ce.csv", "profiles.csv": "voltage_profiles.csv"},
                 "These files are synthetic demonstration data, not experimental results.\nThis is cycle-by-cycle Li||Cu CE, not an Aurbach protocol. Give both CSV files to BatteryReviewForge.\n"),
}


def main() -> None:
    for name, (source_dir, files, readme) in BUNDLES.items():
        target = DEST / f"BRF-demo-{name}.zip"
        folder = f"BRF-demo-{name}"
        with ZipFile(target, "w", compression=ZIP_DEFLATED) as archive:
            for old, new in files.items():
                archive.write(SOURCE / source_dir / old, f"{folder}/{new}")
            archive.writestr(f"{folder}/README.txt", readme)
        print(target)


if __name__ == "__main__":
    main()
