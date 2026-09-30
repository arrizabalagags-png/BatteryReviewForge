"""Coordinate-keyed raw diffraction maps; no phase fitting or synthetic fallback."""
import numpy as np
import matplotlib.pyplot as plt
from recipe_runtime import ContractError, groups, values, line, label, finish, checked_limits, pair, curve_colors


def edges(coordinates):
    points = np.asarray(coordinates)
    mid = (points[:-1] + points[1:]) / 2
    # End bins stop at measured coordinates; do not display invented SOC/time
    # beyond the measurement envelope (e.g. 122.5% from a last 100% sample).
    return np.r_[points[0], mid, points[-1]]


def render(cfg, tables):
    by = groups(tables['diffraction'])
    voltage = groups(tables['voltage']) if tables.get('voltage') else {}
    colors = curve_colors(cfg, [sample + ':measured_synchronized_voltage' for sample in voltage]) if voltage else {}
    fig = plt.figure(layout='constrained')
    gs = fig.add_gridspec(len(by) + 1, 2 if voltage else 1, width_ratios=[3, 1] if voltage else [1])
    checks, axes, handles, texts, maps = [], [], [], [], []
    raw_values = values(tables['diffraction']['rows'], 'intensity')
    color_limits = cfg.get('limits', {}).get('intensity')
    low, high = pair(color_limits, 'limits.intensity') if color_limits is not None else (min(raw_values), max(raw_values))
    if min(raw_values) < low or max(raw_values) > high:
        raise ContractError('limits.intensity会饱和/截断新数据；请扩展或删除范围，不静默复用演示色标。')
    for index, (sample, rows) in enumerate(by.items()):
        xs = sorted({r['two_theta'] for r in rows})
        ys = sorted({r['progress'] for r in rows})
        lookup = {(r['two_theta'], r['progress']): r['intensity'] for r in rows}
        matrix = np.asarray([[lookup[(x, y)] for x in xs] for y in ys])
        ax = fig.add_subplot(gs[index, 0])
        axes.append(ax)
        im = ax.pcolormesh(edges(xs), edges(ys), matrix, cmap=cfg.get('style', {}).get('cmap', 'viridis'), shading='flat', vmin=low, vmax=high, rasterized=True)
        if not np.array_equal(np.asarray(im.get_array()).reshape(matrix.shape), matrix):
            raise ContractError('热图坐标/强度未与原始网格精确对应。')
        item = {'identity': sample + ':raw_diffraction_grid', 'two_theta': xs, 'progress': ys, 'intensity': matrix.tolist(), 'check': 'exact_quadmesh_array', 'coordinate_reordering': 'sorted unique axes; coordinate-keyed lookup; no interpolation', 'edge_policy': 'interior midpoints; endpoint edges at measured coordinate envelope'}
        checks.append(item)
        maps.append((ax, item))
        ax.set(xlabel='2θ (deg)', ylabel=f'Progress ({cfg["units"]["progress"]})')
        ax.set_xlim(xs[0], xs[-1])
        ax.set_ylim(ys[0], ys[-1])
        ax.set_title(label(cfg, sample), fontsize=8)
        fig.colorbar(im, ax=ax, label=f'Intensity ({cfg["units"]["intensity"]})')
        checked_limits(ax, cfg.get('limits', {}).get('diffraction', {}), xs, ys, 'diffraction')
        if voltage:
            trace = voltage[sample]
            side = fig.add_subplot(gs[index, 1], sharey=ax)
            axes.append(side)
            artist = line(side, values(trace, 'voltage'), values(trace, 'progress'), checks, identity=sample + ':measured_synchronized_voltage', color=colors[sample + ':measured_synchronized_voltage'])
            handles.append(artist)
            texts.append(label(cfg, sample))
            side.set(xlabel='Voltage (V)', ylabel=f'Progress ({cfg["units"]["progress"]})')
            checked_limits(side, cfg.get('limits', {}).get('voltage', {}), values(trace, 'voltage'), values(trace, 'progress'), 'voltage')
    finish(fig, axes, cfg, handles, texts, base_height=max(3.4, len(by) * 3.4))
    for ax, item in maps:
        item['display_extent'] = {'two_theta': [float(v) for v in ax.get_xlim()], 'progress': [float(v) for v in ax.get_ylim()]}
    return fig, checks
