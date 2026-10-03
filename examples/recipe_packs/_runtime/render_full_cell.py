"""Full-cell capacity/CE and explicit-reference retention on matched cycles."""
import matplotlib.pyplot as plt
from recipe_runtime import groups, values, line, label, finish, checked_limits, curve_colors


def render(cfg, tables):
    cycling, profiles = tables['cycling'], tables.get('profiles')
    cols = 2 if profiles else 1
    fig = plt.figure(layout='constrained')
    gs = fig.add_gridspec(3, cols)
    axes = [fig.add_subplot(gs[0, i]) for i in range(cols)]
    retention_ax=fig.add_subplot(gs[1, :],sharex=axes[0])
    axes.append(retention_ax)
    by = groups(cycling)
    linked = {}
    if profiles:
        for row in profiles['rows']:
            linked.setdefault((row['sample'], row['cycle']), []).append(row)
    identities = [f'{sample}:{quantity}' for sample in by for quantity in ('capacity', 'CE')]
    identities.extend(f'{sample}:profile:{cycle:g}' for sample, cycle in linked)
    colors = curve_colors(cfg, identities)
    checks, handles, texts = [], [], []
    units = cfg['units']
    ce_ax = axes[0].twinx() if 'ce' in cycling['columns'] else None
    for sample, rows in by.items():
        color = colors[f'{sample}:capacity']
        name = label(cfg, sample)
        artist = line(axes[0], values(rows, 'cycle'), values(rows, 'capacity'), checks, identity=f'{sample}:capacity', color=color, label=name,sampling='cycle')
        handles.append(artist)
        texts.append(name)
        if ce_ax is not None:
            artist = line(ce_ax, values(rows, 'cycle'), values(rows, 'ce'), checks, identity=f'{sample}:CE', color=colors[f'{sample}:CE'],sampling='cycle',markerfacecolor='none')
            handles.append(artist)
            texts.append(name + ' · CE')
        ref=cycling['derived_quantities'][sample]
        line(retention_ax,values(rows,'cycle'),values(rows,'retention'),checks,identity=f'{sample}:retention',color_identity=f'{sample}:capacity',color=color,sampling='cycle')
        retention_ax.text(.02,.94-.12*list(by).index(sample),f"{name}: cycle {int(ref['reference_cycle'])}, Qref={ref['reference_capacity']:.4g} {units['capacity']}",transform=retention_ax.transAxes,fontsize=7,va='top')
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
    retention_ax.set(xlabel='Cycle number',ylabel='Capacity retention (%)')
    # Reserve a genuine text area above the largest observation. Both sample
    # references must remain visible without crossing the early-cycle points.
    retention_values=values(all_rows,'retention')
    low,high=min(retention_values),max(retention_values)
    span=max(high-low,1)
    retention_ax.set_ylim(low-.12*span,high+.55*span)
    retention_ax.margins(x=.03)
    finish(fig, axes, cfg, handles, texts,base_height=5.5)
    return fig, checks
