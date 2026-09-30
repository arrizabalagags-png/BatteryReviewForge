"""Check the actual visible figure text against installed font cmap data."""
from __future__ import annotations

from functools import lru_cache
import hashlib
from pathlib import Path
import warnings

from matplotlib import font_manager, ft2font, rcParams
from matplotlib.axis import Axis
from matplotlib.text import Text


class FontCoverageError(ValueError):
    """No final drawing may silently substitute a missing glyph."""


@lru_cache(maxsize=256)
def font_characters(path):
    return frozenset(ft2font.FT2Font(path).get_charmap())


@lru_cache(maxsize=64)
def font_digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def visible_texts(fig):
    """Walk visible artists, never raw table rows or unrelated metadata."""
    seen = set()
    def walk(artist):
        if id(artist) in seen or not artist.get_visible():
            return
        seen.add(id(artist))
        if isinstance(artist, Axis) and not artist.axes.axison:
            return
        if isinstance(artist, Text):
            if artist.get_text().strip():
                yield artist
            return
        for child in artist.get_children():
            yield from walk(child)
    for ax in fig.axes:
        if ax.get_visible() and ax.axison:
            for axis in (ax.xaxis, ax.yaxis):
                if axis.get_visible():
                    axis.get_ticklabels(which='both')
    yield from walk(fig)


def resolve_text(fig, text):
    current = text.get_fontproperties().copy()
    face = (tuple(current.get_family()), current.get_file())
    resolved = getattr(text, '_voltpeer_resolved_face', None)
    if resolved != face or not hasattr(text, '_voltpeer_requested_font'):
        if resolved and face[0] != resolved[0] and face[1] == resolved[1]:
            current.set_file(None)
        text._voltpeer_requested_font = current.copy()
    original = text._voltpeer_requested_font.copy()
    original.set_size(current.get_size())
    original.set_weight(current.get_weight())
    original.set_style(current.get_style())
    required = {ord(char) for char in text.get_text() if not char.isspace() and ord(char) >= 32}
    families = []
    for family in original.get_family():
        families.extend(fig.voltpeer_font_preferences.get('font.' + family, [family]))
    fallback = ['Microsoft YaHei', 'Noto Sans CJK SC', 'Source Han Sans SC', 'SimHei',
                'PingFang SC', 'WenQuanYi Zen Hei', 'Arial Unicode MS', 'DejaVu Sans']
    def candidate_paths():
        if original.get_file():
            yield original.get_file(), None
        for family in dict.fromkeys([*families, *fallback, *(f.name for f in font_manager.fontManager.ttflist)]):
            props = original.copy()
            props.set_file(None)
            props.set_family([family])
            try:
                yield font_manager.findfont(props, fallback_to_default=False), family
            except ValueError:
                continue
    inspected = set()
    missing = set(required)
    for path, family in candidate_paths():
        if path in inspected:
            continue
        inspected.add(path)
        try:
            available = font_characters(path)
        except (OSError, RuntimeError):
            continue
        missing -= available
        if not required <= available:
            continue
        props = original.copy()
        props.set_file(path)
        actual = font_manager.FontProperties(fname=path).get_name()
        props.set_family([actual])
        return props, {'text': text.get_text(), 'requested_families': original.get_family(),
                       'actual_family': actual, 'font_file': Path(path).name,
                       'font_sha256': font_digest(path), 'glyphs_checked': len(required),
                       'required_codepoints': [f'U+{code:04X}' for code in sorted(required)],
                       'fallback_used': family is not None and family not in families,
                       'status': 'PASS_GLYPH_COVERAGE_ONLY'}
    codes = ', '.join(f'U+{code:04X}' for code in sorted(missing or required)[:12])
    raise FontCoverageError('当前可用字体不能覆盖绘图文字的全部字形（' + codes +
                            '）。请安装覆盖这些字形的字体或选用可用字体；没有删除或替换原文字。')


def prepare_fonts(fig):
    report = []
    for text in visible_texts(fig):
        props, record = resolve_text(fig, text)
        text.set_fontproperties(props)
        text._voltpeer_resolved_face = (tuple(props.get_family()), props.get_file())
        report.append(record)
    fig.voltpeer_font_report = report


def install_font_guard(fig):
    if getattr(fig, 'voltpeer_font_guard', False):
        return
    keys = ('font.family', 'font.sans-serif', 'font.serif', 'font.cursive', 'font.fantasy', 'font.monospace')
    fig.voltpeer_font_preferences = {key: list(rcParams[key]) for key in keys}
    original_draw = fig.draw
    def checked_draw(renderer):
        prepare_fonts(fig)
        try:
            with warnings.catch_warnings():
                warnings.filterwarnings('error', message=r'Glyph .* missing from font.*', category=UserWarning)
                original_draw(renderer)
        except UserWarning as exc:
            raise FontCoverageError('最终渲染检测到字体缺字；请核对字体和原文字，不输出缺字图。') from exc
    fig.draw = checked_draw
    fig.voltpeer_font_guard = True
