"""Validate curated JSON assets and publish a static, versioned Battery Commons catalog."""
from __future__ import annotations

import colorsys
import hashlib
import html
import itertools
import json
import math
import re
import shutil
import tempfile
from datetime import date
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
MAX_TEXT = {"name": 80, "author": 120, "description": 400, "description_zh": 400, "source": 300}


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
    layout = asset.get("layout", {})
    # Preserve the published v1.0.0 preview byte-for-byte. New layouts use an
    # explicit weighted grid and are drawn from validated, numeric geometry.
    if "columns_fraction" in layout:
        fractions = layout["columns_fraction"]
        usable = 560
        gap = 16
        widths = [round((usable - gap) * f) for f in fractions]
        x2 = 30 + widths[0] + gap
        letters = [html.escape(value) for value in layout["panel_letters"]]
        return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 620 260" role="img" aria-label="Two-panel layout"><rect width="620" height="260" fill="#fff"/><rect x="30" y="28" width="{widths[0]}" height="195" fill="#F1F5F7" stroke="#536A78"/><rect x="{x2}" y="28" width="{widths[1]}" height="195" fill="#F1F5F7" stroke="#536A78"/><text x="46" y="57" font-size="20" font-weight="bold" fill="#26343D">{letters[0]}</text><text x="{x2+16}" y="57" font-size="20" font-weight="bold" fill="#26343D">{letters[1]}</text><text x="46" y="126" font-size="14" fill="#536A78">Cycling</text><text x="{x2+16}" y="126" font-size="14" fill="#536A78">Voltage profiles</text></svg>\n'

    canvas, grid = asset["canvas"], asset["grid"]
    view_w, view_h = 620, 360
    margin = 20
    gap = 8
    total_w = view_w - margin * 2 - gap * (grid["cols"] - 1)
    total_h = view_h - margin * 2 - gap * (grid["rows"] - 1)
    col_weights, row_weights = grid["col_weights"], grid["row_weights"]
    col_total, row_total = sum(col_weights), sum(row_weights)
    col_sizes = [total_w * weight / col_total for weight in col_weights]
    row_sizes = [total_h * weight / row_total for weight in row_weights]
    col_positions = [margin + sum(col_sizes[:i]) + gap * i for i in range(grid["cols"])]
    row_positions = [margin + sum(row_sizes[:i]) + gap * i for i in range(grid["rows"])]
    panels = []
    for panel in asset["panels"]:
        row, col = panel.get("row", 1) - 1, panel.get("col", 1) - 1
        rowspan, colspan = panel.get("rowspan", 1), panel.get("colspan", 1)
        width = sum(col_sizes[col:col + colspan]) + gap * (colspan - 1)
        height = sum(row_sizes[row:row + rowspan]) + gap * (rowspan - 1)
        x, y = col_positions[col], row_positions[row]
        label, role = html.escape(panel["label"]), html.escape(panel["role"][:42])
        panels.append(f'<rect x="{x:.2f}" y="{y:.2f}" width="{width:.2f}" height="{height:.2f}" rx="3" fill="#F1F5F7" stroke="#536A78"/><text x="{x+10:.2f}" y="{y+20:.2f}" font-size="16" font-weight="bold" fill="#26343D">{label}</text><text x="{x+10:.2f}" y="{y+height/2:.2f}" font-size="11" fill="#536A78">{role}</text>')
    title = html.escape(asset["name"])
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {view_w} {view_h}" role="img" aria-label="{title} layout preview"><rect width="{view_w}" height="{view_h}" fill="#fff"/>{"".join(panels)}</svg>\n'


def _positive_number(value, label: str, *, allow_zero: bool = False) -> bool:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        return False
    return value >= 0 if allow_zero else value > 0


def validate_layout(asset: dict, path: Path) -> None:
    count = asset.get("panel_count")
    roles = asset.get("roles")
    if isinstance(count, bool) or not isinstance(count, int) or not 2 <= count <= 10:
        raise ValueError(f"{path}: layout panel_count must be from 2 to 10")
    if not isinstance(roles, list) or len(roles) != count or not all(isinstance(role, str) and role.strip() for role in roles):
        raise ValueError(f"{path}: layout roles must name every panel")
    if not _positive_number(asset.get("minimum_width_mm"), "minimum_width_mm") or not _positive_number(asset.get("minimum_font_pt"), "minimum_font_pt") or asset["minimum_font_pt"] < 5:
        raise ValueError(f"{path}: minimum_width_mm must be positive and minimum_font_pt at least 5")

    layout = asset.get("layout")
    if isinstance(layout, dict) and "columns_fraction" in layout:
        # Legacy, immutable schema used by published layout v1.0.0.
        fractions = layout["columns_fraction"]
        if count != 2 or len(roles) != 2 or len(fractions) != 2:
            raise ValueError(f"{path}: legacy column-fraction layout is supported only for two panels")
        if not all(_positive_number(value, "column_fraction") and value < 1 for value in fractions) or abs(sum(fractions) - 1) > 1e-6:
            raise ValueError(f"{path}: invalid column fractions")
        if not _positive_number(layout.get("gutter_mm"), "gutter_mm") or layout["gutter_mm"] >= 15:
            raise ValueError(f"{path}: invalid physical dimensions")
        if layout.get("panel_letters") != [chr(ord("a") + i) for i in range(count)]:
            raise ValueError(f"{path}: panel letters must be a through the panel count")
        return

    canvas, grid, panels = asset.get("canvas"), asset.get("grid"), asset.get("panels")
    if not isinstance(canvas, dict) or not isinstance(grid, dict) or not isinstance(panels, list) or len(panels) != count:
        raise ValueError(f"{path}: grid layout needs canvas, grid, and one panel record per panel")
    for key in ("width_mm", "margin_mm", "gutter_mm"):
        if not _positive_number(canvas.get(key), key, allow_zero=(key != "width_mm")):
            raise ValueError(f"{path}: canvas.{key} has invalid physical size")
    rows, cols = grid.get("rows"), grid.get("cols")
    if any(isinstance(v, bool) or not isinstance(v, int) or not 1 <= v <= 10 for v in (rows, cols)):
        raise ValueError(f"{path}: grid rows and cols must be integers from 1 to 10")
    row_weights, col_weights = grid.get("row_weights"), grid.get("col_weights")
    if not isinstance(row_weights, list) or len(row_weights) != rows or not all(_positive_number(v, "row_weight") for v in row_weights):
        raise ValueError(f"{path}: row_weights must contain one positive value per row")
    if not isinstance(col_weights, list) or len(col_weights) != cols or not all(_positive_number(v, "col_weight") for v in col_weights):
        raise ValueError(f"{path}: col_weights must contain one positive value per column")
    if canvas["width_mm"] <= 2 * canvas["margin_mm"] + (cols - 1) * canvas["gutter_mm"]:
        raise ValueError(f"{path}: margins and gutters leave no usable panel width")
    occupied, labels = set(), set()
    for index, panel in enumerate(panels):
        if not isinstance(panel, dict):
            raise ValueError(f"{path}: each panel must be an object")
        label, role = panel.get("label"), panel.get("role")
        if not isinstance(label, str) or not re.fullmatch(r"[a-j]", label) or label in labels:
            raise ValueError(f"{path}: panel labels must be unique letters a–j")
        if label != chr(ord("a") + index):
            raise ValueError(f"{path}: panel labels must follow a, b, c … order")
        if not isinstance(role, str) or not role.strip() or len(role) > 120:
            raise ValueError(f"{path}: each panel needs a short role")
        labels.add(label)
        row, col = panel.get("row"), panel.get("col")
        rowspan, colspan = panel.get("rowspan", 1), panel.get("colspan", 1)
        if any(isinstance(v, bool) or not isinstance(v, int) for v in (row, col, rowspan, colspan)):
            raise ValueError(f"{path}: panel grid positions and spans must be integers")
        if row < 1 or col < 1 or rowspan < 1 or colspan < 1 or row + rowspan - 1 > rows or col + colspan - 1 > cols:
            raise ValueError(f"{path}: a panel extends outside the grid")
        for y in range(row - 1, row + rowspan - 1):
            for x in range(col - 1, col + colspan - 1):
                if (y, x) in occupied:
                    raise ValueError(f"{path}: panels overlap")
                occupied.add((y, x))
    if [panel["role"] for panel in panels] != roles:
        raise ValueError(f"{path}: top-level roles must match the panel records")


def search_terms(asset: dict) -> list[str]:
    """Create plain-language aliases from validated resource properties."""
    terms = ["科研资源"]
    if asset["category"] == "style":
        terms.extend(("配色", "颜色方案", "曲线配色", "科研配色"))
        hues = []
        for color in asset["series"]:
            red, green, blue = (int(color[i:i + 2], 16) / 255 for i in (1, 3, 5))
            hue, saturation, _ = colorsys.rgb_to_hsv(red, green, blue)
            if saturation >= .22:
                hues.append(hue * 360)
        if any(185 <= hue <= 255 for hue in hues) and any(140 <= hue < 185 for hue in hues):
            terms.extend(("蓝绿", "蓝绿色", "blue-green", "blue green"))
        count = asset["recommended_series_count"]
        if count >= 4:
            numeral = {4: "四", 5: "五", 6: "六", 7: "七", 8: "八"}.get(count, str(count))
            terms.extend((f"{count}条曲线配色", f"{numeral}条曲线配色", f"{count} series", "多条曲线"))
    else:
        terms.extend(("拼图", "拼版", "Figure布局", "面板布局"))
        count = asset["panel_count"]
        numeral = {2: "两", 3: "三", 4: "四", 5: "五", 6: "六", 7: "七", 8: "八", 9: "九", 10: "十"}.get(count, str(count))
        terms.extend((f"{count}面板布局", f"{numeral}面板布局", f"{count} panel layout"))
    return terms


def validate(path: Path) -> dict:
    asset = json.loads(path.read_text(encoding="utf-8"))
    missing = REQUIRED - set(asset)
    if missing:
        raise ValueError(f"{path}: missing {sorted(missing)}")
    if not SLUG.fullmatch(asset["id"]) or not VERSION.fullmatch(asset["version"]):
        raise ValueError(f"{path}: invalid stable id or semantic version")
    if path.stem != f'{asset["id"]}@{asset["version"]}':
        raise ValueError(f"{path}: filename must pin id@version")
    for key, limit in MAX_TEXT.items():
        if not isinstance(asset[key], str) or not asset[key].strip() or len(asset[key]) > limit:
            raise ValueError(f"{path}: {key} must be 1–{limit} characters")
    if asset["category"] not in {"style", "layout"} or asset["status"] not in STATUSES:
        raise ValueError(f"{path}: invalid category or status")
    if "maintainer_pick" in asset and not isinstance(asset["maintainer_pick"], bool):
        raise ValueError(f"{path}: maintainer_pick must be true or false")
    if asset["status"] != "community":
        review = asset.get("review")
        if not isinstance(review, dict) or not all(review.get(key) for key in ("reviewer", "date", "evidence")):
            raise ValueError(f"{path}: reviewed/verified/core status needs a named human review record")
    if asset["status"] in {"verified", "core"} and not asset.get("final_size_qa"):
        raise ValueError(f"{path}: verified/core status needs recorded final-size QA")
    if asset["license"] not in LICENSES:
        raise ValueError(f"{path}: missing approved license or author")
    permissions = asset["permissions"]
    if not isinstance(permissions, dict) or not all(permissions.get(key) is True for key in ("public_display", "registry", "automated_testing")) or not isinstance(permissions.get("model_training"), bool):
        raise ValueError(f"{path}: separate display, registry, test and training permissions are required")
    if not isinstance(asset["tags"], list) or len(asset["tags"]) > 12 or not all(isinstance(tag, str) and 1 <= len(tag) <= 40 for tag in asset["tags"]):
        raise ValueError(f"{path}: tags must be a string list")
    if asset["category"] == "style":
        colors = asset["series"]
        if not isinstance(colors, list) or not 2 <= len(colors) <= 8 or len(colors) != len(set(colors)):
            raise ValueError(f"{path}: use 2–8 unique series colors")
        if not isinstance(asset.get("background"), str) or asset["background"].upper() != "#FFFFFF":
            raise ValueError(f"{path}: phase 1 styles require white background")
        if not isinstance(asset.get("roles"), dict) or not isinstance(asset.get("pastels"), dict):
            raise ValueError(f"{path}: style roles and pastels must be color maps")
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
        validate_layout(asset, path)
    return asset


def load_reviews(pins):
    path = SOURCE / 'reviews.json'
    if not path.exists():
        return {}
    records = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(records, list):
        raise ValueError('Review records must be a list')
    reviews = {}
    for record in records:
        if not isinstance(record, dict) or set(record) - {'id', 'version', 'status', 'lifecycle', 'reviewer', 'reviewed_at', 'reason', 'evidence', 'final_size_qa'}:
            raise ValueError('Invalid review fields')
        pin = (record.get('id'), record.get('version'))
        if pin not in pins or pin in reviews:
            raise ValueError('Unknown or duplicate reviewed id@version')
        if record.get('status', 'community') not in STATUSES or record.get('lifecycle', 'active') not in {'active', 'deprecated', 'withdrawn'}:
            raise ValueError('Invalid review or lifecycle state')
        if any(not isinstance(record.get(key), str) or not record[key].strip() or len(record[key]) > 500 for key in ('reviewer', 'reviewed_at', 'reason')):
            raise ValueError('Review needs a reviewer, date and reason')
        date.fromisoformat(record['reviewed_at'])
        evidence = record.get('evidence')
        if not isinstance(evidence, list) or not 1 <= len(evidence) <= 10 or any(not isinstance(x, str) or not x.strip() or len(x) > 500 for x in evidence):
            raise ValueError('Review evidence must be recorded')
        if record.get('status') in {'verified', 'core'} and record.get('final_size_qa') is not True:
            raise ValueError('Verified status requires recorded final-size QA')
        reviews[pin] = record
    return reviews


def main() -> None:
    # Validate every input before touching any published file.
    validated = []
    seen = set()
    for category in ('styles', 'layouts'):
        for path in sorted((SOURCE / category).glob('*.json')):
            asset = validate(path)
            pin = (asset['id'], asset['version'])
            if pin in seen:
                raise ValueError(f'Duplicate community id@version: {pin}')
            seen.add(pin)
            previous = PUBLIC / category / path.name
            if previous.is_file() and previous.read_bytes() != path.read_bytes():
                raise ValueError('Published id@version is immutable; use a new version or separate review record')
            validated.append((category, path, asset))
    incoming = {(category, path.name) for category, path, _ in validated}
    for category in ('styles', 'layouts'):
        for previous in (PUBLIC / category).glob('*.json'):
            if (category, previous.name) not in incoming:
                raise ValueError('Keep published versions for provenance; withdraw with a separate review record')
    reviews = load_reviews(seen)
    PUBLIC.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.commons-build-', dir=PUBLIC.parent) as temp:
        staging = Path(temp) / 'site'
        staging.mkdir()
        _publish_validated(validated, reviews, staging)
        # Swapping the complete tree removes stale withdrawn/deleted previews and indexes.
        backup = Path(temp) / 'previous'
        assert staging.resolve().is_relative_to(Path(temp).resolve())
        assert backup.resolve().is_relative_to(Path(temp).resolve())
        if PUBLIC.exists():
            PUBLIC.replace(backup)
        try:
            staging.replace(PUBLIC)
        except Exception:
            if backup.exists():
                backup.replace(PUBLIC)
            raise
    (SOURCE / 'catalog.json').write_bytes((PUBLIC / 'catalog.json').read_bytes())
    for category, path, _asset in validated:
        preview = path.with_suffix('.svg')
        preview.write_bytes((PUBLIC / category / preview.name).read_bytes())


def _publish_validated(validated, reviews, staging):
    entries = []
    dates = []
    for category in ('styles', 'layouts'):
        (staging / category).mkdir()
    for category, path, asset in validated:
            dates.append(asset["updated_at"])
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            target = staging / category / path.name
            shutil.copyfile(path, target)
            preview = (style_preview(asset) if category == "styles" else layout_preview(asset))
            preview_name = path.stem + ".svg"
            (staging / category / preview_name).write_text(preview, encoding="utf-8")
            public_keys = ("id", "version", "name", "author", "description", "description_zh", "license", "category", "tags", "status", "created_at", "updated_at", "maintainer_pick")
            aliases = search_terms(asset)
            entries.append({key: asset[key] for key in public_keys if key in asset}
                           | {"search_terms": aliases}
                           | {"source_url": f"{BASE_URL}/{category}/{path.name}", "preview_url": f"commons/{category}/{preview_name}", "sha256": digest,
                              "quality": {"format_checked": True, "color_screen": "automated_only" if category == "styles" else "not_applicable", "scientific_review": "not_claimed"}}
                           | ({key: asset[key] for key in ("background", "recommended_series_count", "colorblind_status", "print_status", "dark_background_support", "series", "line_pt", "roles", "pastels") if key in asset}
                              if category == "styles" else {key: asset[key] for key in ("panel_count", "roles", "layout", "canvas", "grid", "panels", "recommended_use", "minimum_width_mm", "minimum_font_pt") if key in asset}))
            review = reviews.get((asset['id'], asset['version']))
            entries[-1]['lifecycle'] = review.get('lifecycle', 'active') if review else 'active'
            if review:
                entries[-1]['review'] = review
                entries[-1]['status'] = review.get('status', asset['status'])
                dates.append(review['reviewed_at'])
    catalog = {"schema_version": "1.0", "updated_at": max(dates, default=None), "execution_policy": "JSON and SVG only; never execute remote code", "assets": entries}
    payload = json.dumps(catalog, ensure_ascii=False, indent=2) + "\n"
    (staging / "catalog.json").write_text(payload, encoding="utf-8")
    search = [{"group": "社区",
               "title": item["name"],
               "url": f"community-resource.html?id={item['id']}&version={item['version']}",
               "keywords": " ".join([item["category"], "配色" if item["category"] == "style" else "布局", item["id"], item["author"], *item["tags"], *item["search_terms"], item["description"], item["description_zh"]]),
               "description": item["description_zh"], "cta": "查看资源"} for item in entries if item['lifecycle'] != 'withdrawn']
    (staging / "search-index.json").write_text(json.dumps(search, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Published {len(entries)} Battery Commons assets")


if __name__ == "__main__":
    main()
