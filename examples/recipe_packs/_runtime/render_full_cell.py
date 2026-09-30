"""Full-cell cycling with optional measured CE and matched voltage profiles."""
import matplotlib.pyplot as plt
import colorsys
from matplotlib.colors import to_rgb, to_hex
from recipe_runtime import groups, values, line, label, finish, checked_limits


def trace_shade(color, index, count):
    if index == 0:
        return to_hex(color)
    hue, lightness, saturation = colorsys.rgb_to_hls(*to_rgb(color))
    candidates = [0.20 + 0.22 * step / (2 * count + 2) for step in range(2 * count + 3)]
    candidates = [value for value in candidates if abs(value - lightness) > 0.025]
    return to_hex(colorsys.hls_to_rgb(hue, candidates[index - 1], saturation))


def render(cfg, tables):
    cycling, profiles = tables['cycling'], tables.get('profiles')
    cols = 2 if profiles else 1
    fig = plt.figure(layout='constrained')
    gs = fig.add_gridspec(2, cols)
    axes = [fig.add_subplot(gs[0, i]) for i in range(cols)]
    palette = cfg.get('style', {}).get('colors') or list(plt.get_cmap('tab10').colors)
    checks, handles, texts, sample_colors = [], [], [], {}
    units = cfg['units']
    ce_ax = axes[0].twinx() if 'ce' in cycling['columns'] else None
    for index, (sample, rows) in enumerate(groups(cycling).items()):
        color = palette[index % len(palette)]
        sample_colors[sample] = color
        name = label(cfg, sample)
        artist = line(axes[0], values(rows, 'cycle'), values(rows, 'capacity'), checks, identity=f'{sample}:capacity', color=color, label=name)
        handles.append(artist)
        texts.append(name)
        if ce_ax is not None:
            artist = line(ce_ax, values(rows, 'cycle'), values(rows, 'ce'), checks, identity=f'{sample}:CE', color=trace_shade(color, 1, 2), linestyle='-', marker=None)
            handles.append(artist)
            texts.append(name + ' · CE')
    all_rows = cycling['rows']
    axes[0].set(xlabel='Cycle number', ylabel=f'Discharge capacity ({units["capacity"]})')
    checked_limits(axes[0], cfg.get('limits', {}).get('cycling', {}), values(all_rows, 'cycle'), values(all_rows, 'capacity'), 'cycling')
    if ce_ax is not None:
        ce_ax.spines['right'].set_visible(True)
        ce_ax.set_ylabel('Recorded Coulombic efficiency (%)')
        checked_limits(ce_ax, cfg.get('limits', {}).get('ce', {}), values(all_rows, 'cycle'), values(all_rows, 'ce'), 'ce')
    if profiles:
        linked = {}
        for row in profiles['rows']:
            linked.setdefault((row['sample'], row['cycle']), []).append(row)
        for index, ((sample, cycle), rows) in enumerate(linked.items()):
            sample_keys = [key for key in linked if key[0] == sample]
            color = trace_shade(sample_colors[sample], sample_keys.index((sample, cycle)), len(sample_keys))
            artist = line(axes[1], values(rows, 'capacity'), values(rows, 'voltage'), checks, identity=f'{sample}:profile:{cycle:g}', color=color, linestyle='-')
            handles.append(artist)
            texts.append(label(cfg, sample) + f' · cycle {cycle:g}')
        axes[1].set(xlabel=f'Discharge capacity ({units["capacity"]})', ylabel='Voltage (V)')
        checked_limits(axes[1], cfg.get('limits', {}).get('profiles', {}), values(profiles['rows'], 'capacity'), values(profiles['rows'], 'voltage'), 'profiles')
    finish(fig, axes, cfg, handles, texts)
    return fig, checks
