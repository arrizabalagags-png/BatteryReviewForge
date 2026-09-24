"""Validate curated JSON assets and publish a static, versioned Battery Commons catalog."""
from __future__ import annotations

import hashlib
import html
import itertools
import json
import math
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "community"
PUBLIC = ROOT / "docs" / "commons"
BASE_URL = "https://arrizabalagags-png.github.io/BatteryReviewForge/commons"
HEX = re.compile(r"^#[0-9A-Fa-f]{6}$")
SLUG = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")
VERSION = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")
STATUSES = {"community", "reviewed", "verified", "core"}
LICENSES = {"CC0-1.0", "CC-BY-4.0", "MIT"}
REQUIRED = {"id", "version", "name", "author", "description", "description_zh", "license", "created_at", "updated_at", "category", "tags", "status", "source", "permissions"}


def rgb(color: str) -> tuple[int, int, int]:
    if not HEX.fullmatch(color):
        raise ValueError(f"Invalid color: {color!r}")
    return tuple(int(color[index:index + 2], 16) for index in (1, 3, 5))


def contrast_on_white(color: str) -> float:
    def channel(n: int) -> float:
        value = n / 255
        return value / 12.92 if value <= .04045 else ((value + .055) / 1.055) ** 2.4
    r, g, b = rgb(color)
    luminance = .2126 * channel(r) + .7152 * channel(g) + .0722 * channel(b)
    return 1.05 / (luminance + .05)


def simulated(color: str, kind: str) -> str:
    # Simple screening preview, not a certification of color accessibility.
    matrices = {
        "protan": ((.567, .433, 0), (.558, .442, 0), (0, .242, .758)),
        "deutan": ((.625, .375, 0), (.7, .3, 0), (0, .3, .7)),
    }
    original = rgb(color)
    values = [round(sum(weight * value for weight, value in zip(row, original))) for row in matrices[kind]]
    return "#" + "".join(f"{max(0, min(255, value)):02X}" for value in values)


def style_preview(asset: dict) -> str:
    colors = asset["series"]
    bands = []
    for row, (label, palette) in enumerate((
        ("Original", colors), ("Protan screen", [simulated(c, "protan") for c in colors]),
        ("Deutan screen", [simulated(c, "deutan") for c in colors]),
    )):
        y = 47 + row * 70
        bands.append(f'<text x="24" y="{y}" font-size="14" fill="#26343D">{label}</text>')
        for index, color in enumerate(palette):
            x = 160 + index * 105
            bands.append(f'<rect x="{x}" y="{y - 18}" width="80" height="30" rx="4" fill="{color}"/>')
    title = html.escape(asset["name"])
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 620 275" role="img" aria-label="{title} color swatches"><rect width="620" height="275" fill="#fff"/><text x="24" y="248" font-size="12" fill="#66747C">Automated color vision previews; verify at final figure size.</text>{"".join(bands)}</svg>\n'


def layout_preview(asset: dict) -> str:
    fractions = asset["layout"]["columns_fraction"]
    usable = 560
    gap = 16
    widths = [round((usable - gap) * f) for f in fractions]
    x2 = 30 + widths[0] + gap
    letters = [html.escape(value) for value in asset["layout"]["panel_letters"]]
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 620 260" role="img" aria-label="Two-panel layout"><rect width="620" height="260" fill="#fff"/><rect x="30" y="28" width="{widths[0]}" height="195" fill="#F1F5F7" stroke="#536A78"/><rect x="{x2}" y="28" width="{widths[1]}" height="195" fill="#F1F5F7" stroke="#536A78"/><text x="46" y="57" font-size="20" font-weight="bold" fill="#26343D">{letters[0]}</text><text x="{x2+16}" y="57" font-size="20" font-weight="bold" fill="#26343D">{letters[1]}</text><text x="46" y="126" font-size="14" fill="#536A78">Cycling</text><text x="{x2+16}" y="126" font-size="14" fill="#536A78">Voltage profiles</text></svg>\n'


def validate(path: Path) -> dict:
    asset = json.loads(path.read_text(encoding="utf-8"))
    missing = REQUIRED - set(asset)
    if missing:
        raise ValueError(f"{path}: missing {sorted(missing)}")
    if not SLUG.fullmatch(asset["id"]) or not VERSION.fullmatch(asset["version"]):
        raise ValueError(f"{path}: invalid stable id or semantic version")
    if path.stem != f'{asset["id"]}@{asset["version"]}':
        raise ValueError(f"{path}: filename must pin id@version")
    if asset["category"] not in {"style", "layout"} or asset["status"] not in STATUSES:
        raise ValueError(f"{path}: invalid category or status")
    if asset["status"] != "community":
        review = asset.get("review")
        if not isinstance(review, dict) or not all(review.get(key) for key in ("reviewer", "date", "evidence")):
            raise ValueError(f"{path}: reviewed/verified/core status needs a named human review record")
    if asset["status"] in {"verified", "core"} and not asset.get("final_size_qa"):
        raise ValueError(f"{path}: verified/core status needs recorded final-size QA")
    if asset["license"] not in LICENSES or not asset["author"].strip():
        raise ValueError(f"{path}: missing approved license or author")
    permissions = asset["permissions"]
    if not isinstance(permissions, dict) or not all(permissions.get(key) is True for key in ("public_display", "registry", "automated_testing")) or not isinstance(permissions.get("model_training"), bool):
        raise ValueError(f"{path}: separate display, registry, test and training permissions are required")
    if not isinstance(asset["tags"], list) or not all(isinstance(tag, str) for tag in asset["tags"]):
        raise ValueError(f"{path}: tags must be a string list")
    if asset["category"] == "style":
        colors = asset["series"]
        if not 2 <= len(colors) <= 8 or len(colors) != len(set(colors)):
            raise ValueError(f"{path}: use 2–8 unique series colors")
        if asset["background"].upper() != "#FFFFFF":
            raise ValueError(f"{path}: phase 1 styles require white background")
        for color in colors + list(asset["roles"].values()) + list(asset["pastels"].values()):
            rgb(color)
        if any(contrast_on_white(color) < 3 for color in colors):
            raise ValueError(f"{path}: series color is too light against white")
        for kind in ("protan", "deutan"):
            transformed = [rgb(simulated(color, kind)) for color in colors]
            if any(math.dist(left, right) < 30 for left, right in itertools.combinations(transformed, 2)):
                raise ValueError(f"{path}: two series collapse in the {kind} screening simulation")
        if not 1 <= asset["recommended_series_count"] <= len(colors):
            raise ValueError(f"{path}: invalid recommended series count")
    else:
        layout = asset["layout"]
        if asset["panel_count"] != 2 or len(asset["roles"]) != 2 or len(layout["columns_fraction"]) != 2:
            raise ValueError(f"{path}: phase 1 layout preview supports exactly two panels")
        if abs(sum(layout["columns_fraction"]) - 1) > 1e-6 or not all(0 < f < 1 for f in layout["columns_fraction"]):
            raise ValueError(f"{path}: invalid column fractions")
        if not 0 < layout["gutter_mm"] < 15 or asset["minimum_width_mm"] <= 0 or asset["minimum_font_pt"] < 5:
            raise ValueError(f"{path}: invalid physical dimensions")
    return asset


def main() -> None:
    PUBLIC.mkdir(parents=True, exist_ok=True)
    entries = []
    dates = []
    for category in ("styles", "layouts"):
        (PUBLIC / category).mkdir(parents=True, exist_ok=True)
        for path in sorted((SOURCE / category).glob("*.json")):
            asset = validate(path)
            dates.append(asset["updated_at"])
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            target = PUBLIC / category / path.name
            shutil.copyfile(path, target)
            preview = (style_preview(asset) if category == "styles" else layout_preview(asset))
            preview_name = path.stem + ".svg"
            (SOURCE / category / preview_name).write_text(preview, encoding="utf-8")
            (PUBLIC / category / preview_name).write_text(preview, encoding="utf-8")
            entries.append({key: asset[key] for key in ("id", "version", "name", "author", "description", "description_zh", "license", "category", "tags", "status")}
                           | {"source_url": f"{BASE_URL}/{category}/{path.name}", "preview_url": f"commons/{category}/{preview_name}", "sha256": digest,
                              "quality": {"format_checked": True, "color_screen": "automated_only" if category == "styles" else "not_applicable", "scientific_review": "not_claimed"}})
    catalog = {"schema_version": "1.0", "updated_at": max(dates), "execution_policy": "JSON and SVG only; never execute remote code", "assets": entries}
    payload = json.dumps(catalog, ensure_ascii=False, indent=2) + "\n"
    (SOURCE / "catalog.json").write_text(payload, encoding="utf-8")
    (PUBLIC / "catalog.json").write_text(payload, encoding="utf-8")
    print(f"Published {len(entries)} Battery Commons assets")


if __name__ == "__main__":
    main()
