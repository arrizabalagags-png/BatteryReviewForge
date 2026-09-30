"""Local-only CSV/config adapter and delivery runtime for independent figure packs."""
from __future__ import annotations
import argparse
import csv
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import math
from pathlib import Path
import platform
import sys
import tempfile
import textwrap

from cli_runtime import configure_utf8
from delivery_contract import collect_working_bundle, digest, check_working_bundle


class ContractError(ValueError):
    """A missing or conflicting scientific input; no synthetic fallback is permitted."""


def write_json(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def number(value, name):
    if isinstance(value, bool):
        raise ContractError(f'{name}: 不能用布尔值代替数值。')
    try:
        result = float(value)
    except (ValueError, TypeError):
        raise ContractError(f'{name}: 缺少有限数值；请核对列映射和缺失值。') from None
    if not math.isfinite(result):
        raise ContractError(f'{name}: 不接受 NaN/Infinity；不能静默删行。')
    return result


def positive(value, name):
    result = number(value, name)
    if result <= 0:
        raise ContractError(f'{name}: 必须大于0。')
    return result


def required_text(value, name):
    if not isinstance(value, str) or not value.strip() or value.strip().lower() in {'unknown', 'todo', 'tbd', '待确认', '未填写'}:
        raise ContractError(f'{name}: 请提供并确认真实信息，不能继承演示条件。')
    return value.strip()


def pair(value, name):
    if not isinstance(value, list) or len(value) != 2:
        raise ContractError(f'{name}: 需要两个升序的有限数值。')
    low, high = (number(v, name) for v in value)
    if low >= high:
        raise ContractError(f'{name}: 下限必须小于上限。')
    return low, high


def csv_table(config, config_path, key, numeric, *, optional=False):
    table = config.get('data', {}).get(key)
    if table is None and optional:
        return None
    if not isinstance(table, dict):
        raise ContractError(f'data.{key}: 需要 path 和 columns。')
    relative = required_text(table.get('path'), f'data.{key}.path')
    if '://' in relative:
        raise ContractError('数据必须是当前授权项目内的本地文件；本程序不联网下载。')
    path = (config_path.parent / relative).resolve()
    if not path.is_file():
        raise ContractError(f'找不到数据文件：{path.name}。没有演示数据后备路径。')
    columns = table.get('columns', {})
    if not isinstance(columns, dict):
        raise ContractError(f'{key}.columns: 需要物理量到CSV列名的对象。')
    required = ['sample', *numeric]
    if any(not isinstance(columns.get(field), str) or not columns[field] for field in required):
        raise ContractError(f'{key}: 缺少列映射 {required}。')
    if len(set(columns.values())) != len(columns):
        raise ContractError(f'{key}: 不同物理量不能映射到同一列。')
    with path.open(encoding='utf-8-sig', newline='') as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or len(set(reader.fieldnames)) != len(reader.fieldnames):
            raise ContractError(f'{key}: CSV列名为空或重复。')
        if set(columns.values()) - set(reader.fieldnames):
            raise ContractError(f'{key}: CSV没有配置映射的列，请修正columns。')
        rows = []
        for index, raw in enumerate(reader, 2):
            if None in raw or any(raw.get(column) is None for column in columns.values()):
                raise ContractError(f'{key}第{index}行: 列数不一致。')
            row = {'sample': required_text(raw[columns['sample']], f'{key}第{index}行样品')}
            for field in columns:
                if field != 'sample':
                    row[field] = number(raw[columns[field]], f'{key}第{index}行{field}')
            rows.append(row)
    if not rows:
        raise ContractError(f'{key}: CSV没有数据。')
    return {'rows': rows, 'path': path, 'sha256': digest(path), 'columns': columns}


def groups(table):
    grouped = {}
    for row in table['rows']:
        grouped.setdefault(row['sample'], []).append(row)
    return grouped


def increasing(rows, key, name, *, nonnegative=True):
    values = [r[key] for r in rows]
    if len(values) < 2 or any(b <= a for a, b in zip(values, values[1:])):
        raise ContractError(f'{name}: 至少两点，坐标必须严格递增；重复/倒序需单独适配，不能静默覆盖。')
    if nonnegative and min(values) < 0:
        raise ContractError(f'{name}: 不接受负坐标。')


def conditions_for(config, samples, kind):
    condition = config.get('conditions', {})
    if not isinstance(condition, dict):
        raise ContractError('conditions需要对象。')
    common = condition.get('common', {})
    specific = condition.get('by_sample', {})
    if not isinstance(common, dict) or not isinstance(specific, dict) or set(specific) - set(samples):
        raise ContractError('conditions需common/by_sample对象，且不能包含CSV中不存在的样品。')
    result = {}
    for sample in samples:
        declared = {**common, **specific.get(sample, {})}
        if kind == 'full_cell':
            for name in ('cathode', 'anode', 'capacity_basis', 'rate_or_current', 'formation', 'loading_or_areal_capacity'):
                required_text(declared.get(name), f'{sample}.{name}')
            pair(declared.get('voltage_window_V'), f'{sample}.voltage_window_V')
            for name in ('N_P', 'E_C'):
                if name in declared:
                    required_text(declared[name], f'{sample}.{name}（可明确写not reported，但不能猜）')
        elif kind == 'li_li':
            metal = required_text(declared.get('metal'), f'{sample}.metal')
            if metal not in {'Li', 'Na'}:
                raise ContractError('此原型只支持明确的Li或Na对称电池；其他体系需要独立契约。')
            if declared.get('cell_configuration') != f'{metal}||{metal}':
                raise ContractError(f'{sample}: metal与cell_configuration必须一致，不能把半电池当对称电池。')
            for name in ('area_basis', 'rest_protocol', 'failure_rule'):
                required_text(declared.get(name), f'{sample}.{name}')
            for name in ('current_density_mA_cm2', 'half_cycle_areal_capacity_mAh_cm2'):
                positive(declared.get(name), f'{sample}.{name}')
        else:
            for name in ('radiation', 'cell_configuration', 'progress_definition', 'synchronization', 'intensity_normalization'):
                required_text(declared.get(name), f'{sample}.{name}')
            positive(declared.get('wavelength_A'), f'{sample}.wavelength_A')
        if kind != 'operando_xrd':
            number(declared.get('temperature_C'), f'{sample}.temperature_C')
        result[sample] = declared
    return result


def validate(config_path, kind):
    config_path = Path(config_path).resolve()
    cfg = read_json(config_path)
    if not isinstance(cfg, dict):
        raise ContractError('配置顶层必须是JSON对象。')
    for field in ('data', 'units', 'conditions', 'style', 'labels', 'provenance', 'export', 'limits', 'view'):
        if field in cfg and not isinstance(cfg[field], dict):
            raise ContractError(f'{field}: 需要JSON对象，请按input_contract填写。')
    if cfg.get('schema_version') != 1 or cfg.get('resource_id') != kind:
        raise ContractError('schema_version/resource_id与此包不匹配。')
    status = cfg.get('data_status')
    if status not in {'author_data', 'synthetic_demo'}:
        raise ContractError('data_status必须明确是author_data或synthetic_demo。')
    if status == 'author_data':
        if cfg.get('provenance', {}).get('input_origin') != 'author_supplied' or cfg.get('provenance', {}).get('demo_conditions_cleared') is not True:
            raise ContractError('真实入口请确认provenance.input_origin=author_supplied和demo_conditions_cleared=true，并重新填写条件。')
        visible = json.dumps({k: cfg.get(k) for k in ('title', 'labels', 'conditions')}, ensure_ascii=False).lower()
        if any(marker in visible for marker in ('synthetic', 'illustrative', 'synthetic_demo', '演示条件', 'demo sample')):
            raise ContractError('真实配置仍含演示身份/条件；先清除并重新确认。')
    units = cfg.get('units', {})
    tables = {}
    if kind == 'full_cell':
        if units.get('capacity') not in {'mAh g^-1', 'mAh cm^-2', 'mAh'} or units.get('voltage') != 'V' or units.get('cycle') != '1':
            raise ContractError('全电池需要cycle=1、voltage=V、capacity=mAh g^-1/mAh cm^-2/mAh；不自动换算未知单位。')
        tables['cycling'] = csv_table(cfg, config_path, 'cycling', ['cycle', 'capacity'])
        by = groups(tables['cycling'])
        for sample, rows in by.items():
            increasing(rows, 'cycle', sample)
            if any(r['cycle'] < 1 or r['cycle'] != int(r['cycle']) or r['capacity'] < 0 for r in rows):
                raise ContractError(f'{sample}: 圈数须正整数、容量不能为负。')
        if 'ce' in tables['cycling']['columns'] and units.get('ce') != '%':
            raise ContractError('CE列存在时需units.ce=%，不能默认用分数代替百分数。')
        tables['profiles'] = csv_table(cfg, config_path, 'profiles', ['cycle', 'capacity', 'voltage'], optional=True)
        if tables['profiles']:
            profile_groups = {}
            for row in tables['profiles']['rows']:
                if row['sample'] not in by or row['cycle'] not in {r['cycle'] for r in by[row['sample']]}:
                    raise ContractError('电压剖面样品/圈数必须在对应循环数据中有真实记录。')
                profile_groups.setdefault((row['sample'], row['cycle']), []).append(row)
            for identity, rows in profile_groups.items():
                increasing(rows, 'capacity', f'剖面{identity}')
    elif kind == 'li_li':
        if units.get('time') not in {'h', 's'} or units.get('voltage') not in {'V', 'mV'}:
            raise ContractError('对称电池需明确time=h/s和voltage=V/mV；电压保留符号。')
        tables['trace'] = csv_table(cfg, config_path, 'trace', ['time', 'voltage'])
        by = groups(tables['trace'])
        for sample, rows in by.items():
            increasing(rows, 'time', sample)
        if cfg.get('view', {}).get('zoom') is not None:
            low, high = pair(cfg['view']['zoom'], 'view.zoom')
            for sample, rows in by.items():
                if low < rows[0]['time'] or high > rows[-1]['time'] or sum(low <= r['time'] <= high for r in rows) < 2:
                    raise ContractError(f'{sample}: 所选放大窗口没有至少两个点或超出完整记录；请修改窗口。')
    else:
        if units.get('two_theta') != 'deg' or units.get('progress') not in {'%', 'fraction', 'h', 's', 'cycle'} or units.get('intensity') not in {'counts', 'a.u.'}:
            raise ContractError('XRD需two_theta=deg、progress=%/fraction/h/s/cycle、intensity=counts/a.u.；不猜归一化或SOC定义。')
        tables['diffraction'] = csv_table(cfg, config_path, 'diffraction', ['two_theta', 'progress', 'intensity'])
        by = groups(tables['diffraction'])
        for sample, rows in by.items():
            xs, ys = {r['two_theta'] for r in rows}, {r['progress'] for r in rows}
            cells = {(r['two_theta'], r['progress']) for r in rows}
            if min(len(xs), len(ys)) < 2 or len(cells) != len(rows) or len(cells) != len(xs) * len(ys):
                raise ContractError(f'{sample}: XRD需完整矩形坐标网格且每对坐标唯一；不得按原始行顺序reshape、补点或插值。')
            if units['progress'] in {'%', 'fraction'}:
                cap = 100 if units['progress'] == '%' else 1
                if min(ys) < 0 or max(ys) > cap:
                    raise ContractError('SOC超出明确单位范围；请核对%/fraction，程序不自动缩放。')
        tables['voltage'] = csv_table(cfg, config_path, 'voltage', ['progress', 'voltage'], optional=True)
        if tables['voltage']:
            if units.get('voltage') != 'V' or set(groups(tables['voltage'])) != set(by):
                raise ContractError('联动电压需单位V，且每个XRD样品都有同名电压记录。')
            for sample, rows in groups(tables['voltage']).items():
                increasing(rows, 'progress', sample)
                coordinates = [r['progress'] for r in by[sample]]
                if min(r['progress'] for r in rows) != min(coordinates) or max(r['progress'] for r in rows) != max(coordinates):
                    raise ContractError(f'{sample}: XRD与电压进程区间不一致；需要先明确同步，不外推补值。')
    conditions = conditions_for(cfg, by, kind)
    if kind == 'full_cell':
        for sample, condition in conditions.items():
            basis = condition['capacity_basis'].lower()
            expected = {'mAh g^-1': ('mass', '质量'), 'mAh cm^-2': ('area', '面积'), 'mAh': ('absolute', 'total', '绝对', '总容量')}
            if not any(s in basis for s in expected[units['capacity']]):
                raise ContractError(f'{sample}: 容量单位与capacity_basis不一致；请明确归一化分母。')
    labels = cfg.get('labels', {})
    if not isinstance(labels, dict) or set(labels) - set(by):
        raise ContractError('labels只能重命名实际存在的样品，不能注入演示分组。')
    for sample in by:
        required_text(labels.get(sample, sample), '样品显示名')
    existing = [v for v in tables.values() if v]
    pack = Path(__file__).resolve().parents[1]
    if status == 'author_data':
        version = read_json(pack / 'VERSION.json')
        demo_hashes = set(version.get('demo_sha256', {}).values())
        for table in existing:
            if table['path'].is_relative_to((pack / 'demo').resolve()) or table['sha256'] in demo_hashes:
                raise ContractError('真实入口读取了本包演示文件/完全相同演示数值；请提供作者数据，或明确选择synthetic_demo。')
    return cfg, tables, conditions


def checked_limits(ax, bounds, x_values, y_values, name):
    """Explicit ranges cannot hide recorded values; auto ranges show all values."""
    if not isinstance(bounds, dict):
        raise ContractError(f'limits.{name}: 需要x/y对象，或删除范围使用auto。')
    for coordinate, values in (('x', x_values), ('y', y_values)):
        limit = bounds.get(coordinate)
        if limit is not None:
            low, high = pair(limit, f'{name}.{coordinate}')
            if min(values) < low or max(values) > high:
                raise ContractError(f'{name}.{coordinate}: 旧范围会截掉新数据，请扩大范围或使用auto；不会静默截图。')
            getattr(ax, 'set_' + coordinate + 'lim')((low, high))


def values(rows, key):
    return [row[key] for row in rows]


def line(ax, x, y, checks, *, identity, color_identity=None, **kwargs):
    import numpy as np
    from matplotlib.colors import to_hex
    kwargs.setdefault('linestyle', '-')
    kwargs.setdefault('marker', None)
    artist, = ax.plot(x, y, **kwargs)
    artist.set_gid('voltpeer-curve:' + (color_identity or identity))
    if not np.array_equal(artist.get_xdata(), np.asarray(x)) or not np.array_equal(artist.get_ydata(), np.asarray(y)):
        raise ContractError('绘图坐标与规范化原始记录不一致。')
    marker, line_style = artist.get_marker(), artist.get_linestyle()
    if marker not in (None, 'None', '', ' ') or line_style != '-':
        raise ContractError('连续曲线需为无点实线；请核对项目副本的绘图样式。')
    checks.append({'identity': identity, 'points': len(x), 'x': list(x), 'y': list(y),
                   'check': 'exact_artist_array', 'line_style': line_style,
                   'marker': marker, 'style_check': 'solid_without_markers',
                   'color_identity': color_identity or identity, 'color': to_hex(artist.get_color())})
    return artist


def label(cfg, sample):
    return '\n'.join(textwrap.wrap(cfg.get('labels', {}).get(sample, sample), width=36))


def curve_colors(cfg, identities):
    """Assign one opaque, distinguishable colour per actual curve identity.

    A repeated view of the same raw trace uses the same identity. Different
    quantities/cycles are different identities even when their sample is shared.
    The finite default palette deliberately stops instead of silently cycling.
    """
    import matplotlib.pyplot as plt
    from matplotlib.colors import to_rgba, to_hex
    identities = list(dict.fromkeys(identities))
    style = cfg.get('style', {})
    named, palette = style.get('curve_colors'), style.get('colors')
    if named is not None and palette is not None:
        raise ContractError('style.colors与style.curve_colors只能选一种，避免颜色来源冲突。')
    if named is not None:
        if not isinstance(named, dict) or set(named) != set(identities):
            raise ContractError('style.curve_colors必须逐一覆盖当前真实曲线身份，不得遗漏或沿用不存在的样品/圈数。')
        raw = [named[identity] for identity in identities]
    else:
        if palette is None:
            palette = list(plt.get_cmap('tab10').colors)
        if not isinstance(palette, (list, tuple)) or not palette or len(palette) < len(identities):
            count = len(palette) if isinstance(palette, (list, tuple)) else 0
            raise ContractError(f'实际需要{len(identities)}种曲线颜色，只提供{count}种；请补齐style.colors或style.curve_colors，不会循环复用。')
        raw = list(palette)
    rgba = []
    for value in raw:
        try:
            color = to_rgba(value)
        except (ValueError, TypeError):
            raise ContractError('曲线颜色需为Matplotlib可识别的颜色名、#RRGGBB或RGB数值。') from None
        if color[3] != 1:
            raise ContractError('曲线颜色必须不透明，透明色会隐藏或混淆真实记录。')
        # This is an explicit project display gate, not a colour-vision claim.
        linear = [v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4 for v in color[:3]]
        luminance = sum(v * w for v, w in zip(linear, (.2126, .7152, .0722)))
        if 1.05 / (luminance + .05) < 2:
            raise ContractError('曲线颜色对白底对比不足2:1，请换深一些的颜色并复核图件。')
        for previous in rgba:
            if to_hex(color) == to_hex(previous) or math.dist(color[:3], previous[:3]) < .10:
                raise ContractError('曲线颜色重复或过近（sRGB距离小于0.10），请提供互异颜色；不会静默换色。')
        rgba.append(color)
    return {identity: to_hex(color) for identity, color in zip(identities, rgba)}


def finish(fig, axes, cfg, handles, texts, *, base_height=3.4):
    import matplotlib.font_manager as fm
    font = number(cfg.get('style', {}).get('font_pt', 8), 'style.font_pt')
    if not 6 <= font <= 16:
        raise ContractError('style.font_pt需6–16 pt；更大字号请改项目副本布局后检查。')
    rows = math.ceil(len(texts) / min(3, max(1, len(texts))))
    max_lines = max((t.count('\n') + 1 for t in texts), default=1)
    legend_height = max(.28, rows * max_lines * font / 72 * 1.65 + .12)
    width_mm = positive(cfg.get('style', {}).get('width_mm', 180), 'style.width_mm')
    if width_mm < 100:
        raise ContractError('此多面板原型宽度至少100 mm；请改布局而非强行缩小。')
    fig.set_size_inches(width_mm / 25.4, base_height + legend_height)
    gs = axes[0].get_subplotspec().get_gridspec()
    gs.set_height_ratios([*([1] * (gs.nrows - 1)), legend_height / (base_height / (gs.nrows - 1))])
    legend_ax = fig.add_subplot(gs[-1, :])
    legend_ax.axis('off')
    legend = legend_ax.legend(handles, texts, loc='center', ncol=min(3, max(1, len(texts))), frameon=False, fontsize=font * .9) if handles else None
    title = str(cfg.get('title') or 'Battery data')
    if cfg['data_status'] == 'synthetic_demo':
        title = 'SYNTHETIC DEMO — ' + title
    fig.suptitle(title, fontsize=font + 1)
    for i, ax in enumerate(axes):
        ax.tick_params(labelsize=font * .88, direction='out')
        ax.xaxis.label.set_size(font)
        ax.yaxis.label.set_size(font)
        ax.text(0, 1.03, chr(97 + i), transform=ax.transAxes, fontweight='bold', fontsize=font)
    fig.canvas.draw()
    if legend is not None:
        box = legend.get_window_extent(fig.canvas.get_renderer())
        frame = fig.bbox
        if box.x0 < frame.x0 or box.x1 > frame.x1 or box.y0 < frame.y0 or box.y1 > frame.y1:
            raise ContractError('图例超出画布；增大style.width_mm、缩短经作者确认的显示名或修改项目副本布局。')


def run(kind, render, argv=None):
    configure_utf8()
    parser = argparse.ArgumentParser(description=f'VoltPeer {kind}: 先确认输入，再生成版本化Working结果；不生成后备Demo。')
    parser.add_argument('--config', required=True, type=Path)
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        cfg, tables, conditions = validate(args.config, kind)
        warnings = []
        if kind == 'full_cell' and 'ce' in tables['cycling']['columns'] and any(not 0 <= row['ce'] <= 100 for row in tables['cycling']['rows']):
            warnings.append('CE存在0–100%以外的记录，已保留原值；请核对效率定义、单位和计算记录。')
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import matplotlib.font_manager as fm
        names = {f.name for f in fm.fontManager.ttflist}
        cjk = next((n for n in ('Microsoft YaHei', 'Noto Sans CJK SC', 'SimHei', 'PingFang SC') if n in names), None)
        visible = str(cfg.get('title', '')) + ''.join(cfg.get('labels', {}).values()) + ''.join(r['sample'] for t in tables.values() if t for r in t['rows'][:50])
        if any('\u4e00' <= ch <= '\u9fff' for ch in visible) and cjk is None:
            raise ContractError('中文标签需要本机CJK字体（如微软雅黑/Noto Sans CJK）；请在隔离环境中配置，不输出缺字图。')
        style = cfg.get('style', {})
        font = number(style.get('font_pt', 8), 'style.font_pt')
        with plt.rc_context({'font.family': [cjk, 'DejaVu Sans'] if cjk else ['DejaVu Sans'], 'font.size': font, 'pdf.fonttype': 42, 'svg.fonttype': 'none', 'axes.spines.top': True, 'axes.spines.right': True, 'axes.spines.bottom': True, 'axes.spines.left': True, 'lines.linewidth': 1.1}):
            fig, checks = render(cfg, tables)
            frames, color_checks, assigned_colors = [], [], {}
            from matplotlib.colors import to_hex
            for index, ax in enumerate(fig.axes):
                if not ax.axison or hasattr(ax, '_colorbar'):
                    continue
                sides = {side: ax.spines[side].get_visible() for side in ('top','right','bottom','left')}
                if not all(sides.values()):
                    raise ContractError('数据图需保留上下左右四条框线，请检查项目副本。')
                frames.append({'axis_index': index, 'spines': sides})
                for artist in ax.lines:
                    gid = artist.get_gid() or ''
                    if not gid.startswith('voltpeer-curve:'):
                        raise ContractError('数据曲线缺少可追溯身份，请使用line助手并记录真实样品/物理量/圈数。')
                    identity = gid.removeprefix('voltpeer-curve:')
                    color = to_hex(artist.get_color())
                    if artist.get_marker() not in (None, 'None', '', ' ') or artist.get_linestyle() != '-':
                        raise ContractError('最终数据曲线需为无点实线，请检查项目副本。')
                    if identity in assigned_colors and assigned_colors[identity] != color:
                        raise ContractError('同一真实轨迹在不同视图中颜色不一致，请核对曲线身份。')
                    assigned_colors[identity] = color
                    color_checks.append({'axis_index': index, 'color_identity': identity, 'color': color,
                                         'check': 'actual_line2d_identity_color'})
            if len(set(assigned_colors.values())) != len(assigned_colors):
                raise ContractError('不同真实曲线身份使用了同一种颜色，请补齐互异颜色后重新生成。')
            export = cfg.get('export', {})
            formats = export.get('formats', ['pdf', 'svg', 'png', 'tiff'])
            if not formats or len(set(formats)) != len(formats) or set(formats) - {'pdf', 'svg', 'png', 'tiff'}:
                raise ContractError('export.formats需互不重复的pdf/svg/png/tiff。')
            dpis = {fmt: export.get(f'{fmt}_dpi', 300) for fmt in ('png', 'tiff')}
            if any(type(n) is not int or not 300 <= n <= 2400 for n in dpis.values()):
                raise ContractError('PNG/TIFF DPI需300–2400整数；向量文件没有DPI合规声明。')
            with tempfile.TemporaryDirectory(prefix='voltpeer-recipe-') as temp:
                stage = Path(temp)
                outputs = []
                for fmt in formats:
                    target = stage / f'figure.{fmt}'
                    fig.savefig(target, format=fmt, dpi=dpis.get(fmt, 300), facecolor='white', **({'pil_kwargs': {'compression': 'tiff_lzw'}} if fmt == 'tiff' else {}))
                    outputs.append(target)
                data_hash = hashlib.sha256(json.dumps(checks, ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()
                version = read_json(Path(__file__).resolve().parents[1] / 'VERSION.json')
                record = {'schema_version': 1, 'resource_id': kind, 'pack_version': version['version'], 'data_status': cfg['data_status'], 'conditions': conditions,
                          'input_records': [{'file': t['path'].name, 'sha256': t['sha256'], 'rows': len(t['rows']), 'columns': t['columns']} for t in tables.values() if t],
                          'exact_data_artist_checks': checks, 'data_frame_checks': frames, 'data_color_checks': color_checks,
                          'curve_color_assignments': assigned_colors, 'plotted_data_sha256': data_hash, 'unit_mapping': cfg['units'],
                          'export': {'formats': formats, 'dpi_by_format': {f: dpis[f] if f in dpis else None for f in formats}, 'tiff_compression': 'tiff_lzw' if 'tiff' in formats else None},
                          'scientific_review': 'pending_author_review', 'material_questions': warnings, 'model_behavior_eval': 'NOT_RUN',
                          'generated_at': datetime.now(timezone.utc).isoformat(timespec='seconds'),
                          'environment': {'python': platform.python_version(), 'os': platform.system(), 'matplotlib': matplotlib.__version__, 'numpy': importlib.metadata.version('numpy')}}
                write_json(stage / 'data_checks.json', record)
                outputs.append(stage / 'data_checks.json')
                root = collect_working_bundle(outputs, args.out, inputs=[args.config.resolve(), *[t['path'] for t in tables.values() if t]], skill_id='battery-review-figure', objective=f'{kind} new-data rendering', specification={'status': 'author_requested_working_preview', 'journal_requirements': 'needs_confirmation', 'data_status': cfg['data_status'], 'resource_id': kind}, title=f'{kind} 图件结果')
                state_path = root / '.voltpeer/TASK_STATE.json'
                state = read_json(state_path)
                state['scientific_context'] = {'data_status': cfg['data_status'], 'units': cfg['units'], 'conditions': conditions}
                state['user_choices']['recipe_pack_version'] = version['version']
                state['pending_questions'].extend(warnings)
                write_json(state_path, state)
                with (root / 'README.md').open('a', encoding='utf-8') as notes:
                    notes.write('\n## 数据与条件\n\n' + ('**这是原创合成演示，不是实验数据。**\n\n' if cfg['data_status'] == 'synthetic_demo' else '使用作者提供的CSV；没有平滑、补点、拟合或借用演示数值。\n\n') + '单位：' + json.dumps(cfg['units'], ensure_ascii=False) + '\n\n')
                    for sample, condition in conditions.items():
                        notes.write(f'- {sample}: ' + json.dumps(condition, ensure_ascii=False) + '\n')
                    if warnings:
                        notes.write('\n## 需要确认\n\n' + '\n'.join('- ' + w for w in warnings) + '\n')
                if warnings:
                    import html
                    with (root / 'index.html').open('a', encoding='utf-8') as page:
                        page.write('<h2>需要确认</h2><p>' + '</p><p>'.join(html.escape(w) for w in warnings) + '</p>')
                print(f'结果已保存：{root}\n打开 index.html 看图，最终文件在 results。\n请核对实验条件、图例和期刊最新要求。')
                for warning in warnings:
                    print(warning)
            plt.close(fig)
        return 0
    except (ContractError, OSError, ValueError, KeyError, TypeError, ImportError) as exc:
        print(f'需要先处理输入：{exc}', file=sys.stderr)
        return 2


def verify(working):
    problems = check_working_bundle(Path(working))
    try:
        record = read_json(Path(working) / '.voltpeer/records/data_checks.json')
        actual = hashlib.sha256(json.dumps(record['exact_data_artist_checks'], ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()
        if record['plotted_data_sha256'] != actual:
            problems.append('绘图数组检查摘要发生改变。')
        if record['scientific_review'] != 'pending_author_review':
            problems.append('技术检查不能冒充作者科学审查。')
    except (OSError, ValueError, KeyError, TypeError) as exc:
        problems.append(str(exc))
    return problems
