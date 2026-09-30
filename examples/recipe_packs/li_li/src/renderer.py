"""Signed Li/Na symmetric traces; optional zoom is explicitly linked to raw trace."""
import matplotlib.pyplot as plt
from recipe_runtime import groups, values, line, label, finish, checked_limits


def render(cfg, tables):
    table = tables['trace']
    zoom = cfg.get('view', {}).get('zoom')
    fig = plt.figure(layout='constrained')
    gs = fig.add_gridspec(2, 2 if zoom else 1)
    axes = [fig.add_subplot(gs[0, i]) for i in range(2 if zoom else 1)]
    palette = cfg.get('style', {}).get('colors') or list(plt.get_cmap('tab10').colors)
    checks, handles, texts = [], [], []
    all_zoom = []
    for index, (sample, rows) in enumerate(groups(table).items()):
        color = palette[index % len(palette)]
        artist = line(axes[0], values(rows, 'time'), values(rows, 'voltage'), checks, identity=f'{sample}:full_signed_trace', color=color)
        handles.append(artist)
        texts.append(label(cfg, sample))
        if zoom:
            low, high = zoom
            selected = [r for r in rows if low <= r['time'] <= high]
            all_zoom.extend(selected)
            line(axes[1], values(selected, 'time'), values(selected, 'voltage'), checks, identity=f'{sample}:declared_zoom:{low:g}-{high:g}', color=color)
    for ax in axes:
        ax.set(xlabel=f'Time ({cfg["units"]["time"]})', ylabel=f'Signed cell voltage ({cfg["units"]["voltage"]})')
    checked_limits(axes[0], cfg.get('limits', {}).get('trace', {}), values(table['rows'], 'time'), values(table['rows'], 'voltage'), 'trace')
    if zoom:
        axes[0].axvspan(*zoom, color='#e0ecf3', zorder=-2)
        axes[1].set_xlim(zoom)
        checked_limits(axes[1], cfg.get('limits', {}).get('zoom', {}), values(all_zoom, 'time'), values(all_zoom, 'voltage'), 'zoom')
    finish(fig, axes, cfg, handles, texts)
    return fig, checks
