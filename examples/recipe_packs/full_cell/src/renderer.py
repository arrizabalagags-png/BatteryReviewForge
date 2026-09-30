"""Full-cell cycling with optional measured CE and matched voltage profiles."""
import matplotlib.pyplot as plt
from recipe_runtime import groups, values, line, label, finish, checked_limits, curve_colors


def render(cfg, tables):
    cycling, profiles = tables['cycling'], tables.get('profiles')
    cols = 2 if profiles else 1
    fig = plt.figure(layout='constrained')
    gs = fig.add_gridspec(2, cols)
    axes = [fig.add_subplot(gs[0, i]) for i in range(cols)]
    by = groups(cycling)
    linked = {}
    if profiles:
        for row in profiles['rows']:
            linked.setdefault((row['sample'], row['cycle']), []).append(row)
    identities = [f'{sample}:{quantity}' for sample in by for quantity in ('capacity', 'CE') if quantity == 'capacity' or 'ce' in cycling['columns']]
    identities.extend(f'{sample}:profile:{cycle:g}' for sample, cycle in linked)
    colors = curve_colors(cfg, identities)
    checks, handles, texts = [], [], []
    units = cfg['units']
    ce_ax = axes[0].twinx() if 'ce' in cycling['columns'] else None
    for sample, rows in by.items():
        color = colors[f'{sample}:capacity']
        name = label(cfg, sample)
        artist = line(axes[0], values(rows, 'cycle'), values(rows, 'capacity'), checks, identity=f'{sample}:capacity', color=color, label=name)
        handles.append(artist)
        texts.append(name)
        if ce_ax is not None:
            artist = line(ce_ax, values(rows, 'cycle'), values(rows, 'ce'), checks, identity=f'{sample}:CE', color=colors[f'{sample}:CE'])
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
        for (sample, cycle), rows in linked.items():
            color = colors[f'{sample}:profile:{cycle:g}']
            artist = line(axes[1], values(rows, 'capacity'), values(rows, 'voltage'), checks, identity=f'{sample}:profile:{cycle:g}', color=color, linestyle='-')
            handles.append(artist)
            texts.append(label(cfg, sample) + f' · cycle {cycle:g}')
        axes[1].set(xlabel=f'Discharge capacity ({units["capacity"]})', ylabel='Voltage (V)')
        checked_limits(axes[1], cfg.get('limits', {}).get('profiles', {}), values(profiles['rows'], 'capacity'), values(profiles['rows'], 'voltage'), 'profiles')
    finish(fig, axes, cfg, handles, texts)
    return fig, checks
