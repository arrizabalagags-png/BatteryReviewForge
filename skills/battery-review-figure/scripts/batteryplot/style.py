"""A restrained, original palette and final-size Matplotlib styling."""

from __future__ import annotations

import json
import colorsys
import hashlib
import re
from functools import lru_cache
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import font_manager, ft2font
from matplotlib.backends.backend_agg import RendererAgg
from matplotlib.layout_engine import ConstrainedLayoutEngine
from matplotlib.text import Text

from .data import DataContractError

MM_PER_INCH = 25.4
THEME = json.loads((Path(__file__).resolve().parents[2] / "assets" / "figure_theme.json").read_text(encoding="utf-8-sig"))
PRESETS = THEME["presets"]
COLOR = re.compile(r"^#[0-9A-Fa-f]{6}$")
DEFAULT_STYLE = "forge"
COLORS = tuple(PRESETS[DEFAULT_STYLE]["series"])
MARKERS = ("o", "s", "^", "D", "v")
LINESTYLES = ("-",) * len(MARKERS)
PLOT_STYLE = {
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
    "font.size": 7,
    "text.color": THEME["ink"],
    "axes.labelcolor": THEME["ink"],
    "axes.edgecolor": THEME["ink"],
    "xtick.color": THEME["ink"],
    "ytick.color": THEME["ink"],
    "axes.labelsize": 8,
    "axes.titlesize": 8,
    "xtick.labelsize": 6,
    "ytick.labelsize": 6,
    "legend.fontsize": 6,
    "axes.spines.top": True,
    "axes.spines.right": True,
    "axes.spines.bottom": True,
    "axes.spines.left": True,
    "axes.linewidth": 0.8,
    "xtick.major.width": 0.7,
    "ytick.major.width": 0.7,
    "lines.linewidth": 1.5,
    "hatch.linewidth": 0.4,
    "svg.fonttype": "none",
    "pdf.fonttype": 42,
    "savefig.facecolor": "white",
}


def get_preset(style: str) -> dict:
    if style not in PRESETS:
        raise DataContractError(f"Unknown figure style {style!r}; choose one of {', '.join(PRESETS)}")
    return PRESETS[style]


def register_community_style(lock_path: str | Path) -> tuple[str, dict]:
    """Load one pinned JSON style from an explicit local lock; no network or code execution."""
    lock_file = Path(lock_path)
    lock = json.loads(lock_file.read_text(encoding="utf-8-sig"))
    pin = lock.get("style_id", "")
    if not re.fullmatch(r"community:[a-z][a-z0-9-]*@[0-9]+\.[0-9]+\.[0-9]+", pin):
        raise DataContractError("Community style needs a pinned community:id@version lock")
    asset_file = (lock_file.parent / lock["asset_file"]).resolve()
    if asset_file.parent != lock_file.parent.resolve() or not asset_file.is_file():
        raise DataContractError("Community style JSON must sit beside its lock file")
    raw = asset_file.read_bytes()
    if hashlib.sha256(raw).hexdigest() != lock.get("sha256"):
        raise DataContractError("Community style hash changed after locking")
    asset = json.loads(raw)
    identity = f'community:{asset.get("id")}@{asset.get("version")}'
    if asset.get("category") != "style" or identity != pin or asset.get("background", "").upper() != "#FFFFFF":
        raise DataContractError("Community style identity or background is invalid")
    series = asset.get("series", [])
    if not isinstance(series, list) or not 2 <= len(series) <= 8 or not all(isinstance(c, str) and COLOR.fullmatch(c) for c in series):
        raise DataContractError("Community style needs 2–8 valid series colors")
    required_roles = set(THEME["roles"])
    required_pastels = set(THEME["pastels"])
    roles, pastels = asset.get("roles"), asset.get("pastels")
    if not isinstance(roles, dict) or not isinstance(pastels, dict) or not required_roles <= set(roles) or not required_pastels <= set(pastels):
        raise DataContractError("Community style roles or pastels are incomplete")
    if not all(isinstance(c, str) and COLOR.fullmatch(c) for c in list(roles.values()) + list(pastels.values())):
        raise DataContractError("Community style roles or pastels contain invalid colors")
    line_pt = asset.get("line_pt")
    if not isinstance(line_pt, (int, float)) or not .5 <= line_pt <= 3:
        raise DataContractError("Community style line width must be 0.5–3 pt")
    PRESETS[pin] = {"series": series, "roles": roles, "pastels": pastels, "line_pt": line_pt,
                    "label_zh": asset["name"], "label_en": asset["name"], "purpose": asset["description"]}
    return pin, {key: lock[key] for key in ("asset_id", "asset_version", "source_url", "sha256", "retrieved_at", "review_status")}


def colors_for(style: str) -> tuple[str, ...]:
    return tuple(get_preset(style)["series"])


def trace_shade(color, index: int, count: int) -> str:
    """Keep a sample's hue while distinguishing its labelled solid traces."""
    if count < 1 or not 0 <= index < count:
        raise DataContractError("Trace colour index is outside its group")
    if index == 0:
        return mpl.colors.to_hex(color)
    hue, lightness, saturation = colorsys.rgb_to_hls(*mpl.colors.to_rgb(color))
    candidates = [0.20 + 0.22 * step / (2 * count + 2) for step in range(2 * count + 3)]
    candidates = [value for value in candidates if abs(value - lightness) > 0.025]
    return mpl.colors.to_hex(colorsys.hls_to_rgb(hue, candidates[index - 1], saturation))


def theme_for(style: str) -> dict:
    preset = get_preset(style)
    return {**THEME, "roles": preset["roles"], "pastels": preset["pastels"]}


@lru_cache(maxsize=256)
def _font_characters(path: str):
    return frozenset(ft2font.FT2Font(path).get_charmap())


def _font_properties_for(fig, text):
    current = text.get_fontproperties().copy()
    face = (tuple(current.get_family()), current.get_file())
    resolved = getattr(text, '_batteryplot_resolved_face', None)
    if resolved != face:
        if resolved and face[0] != resolved[0] and face[1] == resolved[1]:
            current.set_file(None)  # A later caller family change replaces our resolved fname.
        text._batteryplot_requested_font = current.copy()
    original = text._batteryplot_requested_font.copy()
    original.set_size(current.get_size())
    original.set_weight(current.get_weight())
    original.set_style(current.get_style())
    required = {ord(char) for char in text.get_text() if not char.isspace() and ord(char) >= 32}
    families = []
    for family in original.get_family():
        families.extend(fig.batteryplot_font_preferences.get('font.' + family, [family]))
    # Prefer the actual caller's font; installed candidates are checked for the
    # exact text, not approved by a filename or by a generic "CJK" label.
    if original.get_file() and required <= _font_characters(original.get_file()):
        actual = font_manager.FontProperties(fname=original.get_file()).get_name()
        original.set_family([actual])
        return original, {'requested_families': text._batteryplot_requested_font.get_family(),
                          'actual_family': actual, 'glyphs_checked': len(required), 'text': text.get_text(),
                          'status': 'PASS_GLYPH_COVERAGE_ONLY'}
    fallback = ['Microsoft YaHei', 'Noto Sans CJK SC', 'Source Han Sans SC', 'SimHei',
                'PingFang SC', 'WenQuanYi Zen Hei', 'Arial Unicode MS', 'DejaVu Sans']
    candidates = list(dict.fromkeys([*families, *fallback, *(f.name for f in font_manager.fontManager.ttflist)]))
    missing = set(required)
    for family in candidates:
        properties = original.copy()
        properties.set_family([family])
        properties.set_file(None)
        try:
            path = font_manager.findfont(properties, fallback_to_default=False)
        except ValueError:
            continue
        # Avoid opening every installed font if the requested one already works.
        available = _font_characters(path)
        missing -= available
        if required <= available:
            properties.set_file(path)
            actual = font_manager.FontProperties(fname=path).get_name()
            properties.set_family([actual])
            return properties, {'requested_families': original.get_family(), 'actual_family': actual,
                                'glyphs_checked': len(required), 'text': text.get_text(),
                                'status': 'PASS_GLYPH_COVERAGE_ONLY'}
    codes = ', '.join(f'U+{code:04X}' for code in sorted(missing or required)[:12])
    raise DataContractError('No usable installed font covers this label (' + codes +
                            '). Install a font containing these glyphs or select an available font; text was not removed.')


def _prepare_fonts(fig):
    report = []
    for text in fig.findobj(match=Text):
        if not text.get_visible() or not text.get_text().strip():
            continue
        properties, record = _font_properties_for(fig, text)
        text.set_fontproperties(properties)
        text._batteryplot_resolved_face = (tuple(properties.get_family()), properties.get_file())
        report.append(record)
    fig.batteryplot_font_report = report


def _wrap_measured(value, properties, renderer, width):
    """Wrap all content by actual glyph widths; never truncate lines or tokens."""
    lines, current = [], ''
    for token in re.findall(r'\n|[^\S\n]+|[A-Za-z0-9_]+|.', value):
        if token == '\n':
            lines.append(current); current = ''
            continue
        size = renderer.get_text_width_height_descent(current + token, properties, False)[0]
        if current and size > width:
            lines.append(current); current = ''
        if renderer.get_text_width_height_descent(token, properties, False)[0] <= width:
            current += token
            continue
        # Long identifiers/URLs must fit too; all their characters are retained.
        for char in token:
            size = renderer.get_text_width_height_descent(current + char, properties, False)[0]
            if current and size > width:
                lines.append(current); current = ''
            current += char
    lines.append(current)
    return '\n'.join(lines)


def _layout_banner(fig, renderer):
    banner = getattr(fig, 'batteryplot_condition_text', None)
    if banner is None:
        return
    properties = banner.get_fontproperties()
    banner.set_text(_wrap_measured(fig.batteryplot_condition_full_text, properties, renderer, fig.bbox.width * .94))
    # A small physical allowance covers renderer-specific ascenders/line metrics.
    height = max(banner.get_window_extent(renderer).height / fig.dpi,
                 len(banner.get_text().splitlines()) * properties.get_size_in_points() / 72 * 1.35)
    base = fig.batteryplot_condition_base_height
    total = base + height + .14  # 0.08 inch top margin and 0.06 inch separation.
    fig.set_size_inches(fig.get_figwidth(), total, forward=False)
    banner.set_position((.5, 1 - .08 / total))
    engine = fig.get_layout_engine()
    if isinstance(engine, ConstrainedLayoutEngine):
        x, y, width, top = fig.batteryplot_condition_base_rect
        engine.set(rect=(x, y * base / total, width, top * base / total))
    elif engine is None:
        for ax, (x, y, width, axes_height) in fig.batteryplot_condition_axes:
            ax.set_position((x, y * base / total, width, axes_height * base / total))
    else:
        raise DataContractError('Condition-note layout needs constrained layout or explicitly positioned axes.')
    fig.batteryplot_condition_layout = {'full_text_retained': True, 'line_count': len(banner.get_text().splitlines()),
                                      'note_height_inches': height, 'reserved_height_inches': total-base,
                                      'visual_review': 'NOT_TESTED'}


def _install_text_guard(fig):
    if getattr(fig, 'batteryplot_text_guard', False):
        return
    original_draw = fig.draw
    original_canvas_draw = fig.canvas.draw
    original_savefig = fig.savefig
    def preflight():
        _prepare_fonts(fig)
        # Allocate the final size before a bitmap buffer/PDF page is allocated.
        metrics = RendererAgg(max(1, int(fig.bbox.width)), max(1, int(fig.bbox.height)), fig.dpi)
        _layout_banner(fig, metrics)
    def canvas_draw(*args, **kwargs):
        preflight()
        return original_canvas_draw(*args, **kwargs)
    def savefig(*args, **kwargs):
        preflight()
        return original_savefig(*args, **kwargs)
    def checked_draw(renderer):
        _prepare_fonts(fig)
        original_draw(renderer)
        banner = getattr(fig, 'batteryplot_condition_text', None)
        if banner is not None:
            box = banner.get_window_extent(renderer)
            bounds = fig.bbox
            if box.x0 < bounds.x0-.5 or box.x1 > bounds.x1+.5 or box.y0 < bounds.y0-.5 or box.y1 > bounds.y1+.5:
                raise DataContractError('Condition note exceeds the final figure boundary; all text retained for repair.')
            if any(box.overlaps(ax.get_window_extent(renderer)) for ax in fig.axes if ax.get_visible()):
                raise DataContractError('Condition note overlaps data coordinates; all text retained for repair.')
            fig.batteryplot_condition_layout['boundary_and_data_overlap_check'] = 'PASS'
    fig.draw = checked_draw
    fig.canvas.draw = canvas_draw
    fig.savefig = savefig
    fig.batteryplot_text_guard = True


def make_figure(width_mm: float = 89, height_mm: float = 65, *, style: str = DEFAULT_STYLE):
    if width_mm <= 0 or height_mm <= 0:
        raise ValueError("Figure dimensions must be positive")
    preset = get_preset(style)
    selected_theme = theme_for(style)
    plot_style = {**PLOT_STYLE,
                  "text.color": THEME["ink"],
                  "axes.labelcolor": THEME["ink"],
                  "axes.edgecolor": THEME["ink"],
                  "lines.linewidth": preset["line_pt"]}
    font_keys = ('font.family', 'font.sans-serif', 'font.serif', 'font.cursive', 'font.fantasy', 'font.monospace')
    if any(mpl.rcParams[key] != mpl.rcParamsDefault[key] for key in font_keys):
        plot_style.update({key: list(mpl.rcParams[key]) for key in font_keys})
    with mpl.rc_context(plot_style):
        fig, ax = plt.subplots(
            figsize=(width_mm / MM_PER_INCH, height_mm / MM_PER_INCH),
            layout="constrained",
        )
        fig.batteryplot_font_preferences = {key: list(mpl.rcParams[key]) for key in font_keys}
    fig.batteryplot_style = style
    fig.batteryplot_theme = selected_theme
    fig.batteryplot_linewidth = float(preset["line_pt"])
    _install_text_guard(fig)
    return fig, ax


def condition_banner(fig, note: str) -> None:
    if not isinstance(note, str) or not note.strip():
        raise DataContractError('A contextual comparison requires a complete condition_note.')
    if not hasattr(fig, 'batteryplot_font_preferences'):
        fig.batteryplot_font_preferences = {key: list(mpl.rcParams[key]) for key in ('font.family', 'font.sans-serif', 'font.serif', 'font.cursive', 'font.fantasy', 'font.monospace')}
    if not hasattr(fig, 'batteryplot_condition_text'):
        fig.batteryplot_condition_base_height = fig.get_figheight()
        engine = fig.get_layout_engine()
        fig.batteryplot_condition_base_rect = engine.get()['rect'] if isinstance(engine, ConstrainedLayoutEngine) else (0, 0, 1, 1)
        fig.batteryplot_condition_axes = [(ax, ax.get_position().bounds) for ax in fig.axes]
        fig.batteryplot_condition_text = fig.text(.5, .99, '', ha='center', va='top', fontsize=6,
            color=getattr(fig, 'batteryplot_theme', THEME)['roles']['limitation_or_failure'], in_layout=False)
    fig.batteryplot_condition_full_text = 'Comparison limits · ' + note
    fig.batteryplot_condition_text.set_text(fig.batteryplot_condition_full_text)
    _install_text_guard(fig)
