"""Physical plot rectangles and post-render alignment gates (no image stretching)."""
from __future__ import annotations

import math


def axes_mm(fig, *, left, top, width, height, **kwargs):
    """Place an axes by its plot box, in mm measured from the page top-left."""
    fw, fh = fig.get_size_inches() * 25.4
    values = (left, top, width, height)
    if not all(math.isfinite(v) for v in values) or min(left, top) < 0 or min(width, height) <= 0:
        raise ValueError("Plot rectangle requires finite coordinates and positive dimensions")
    if left + width > fw + 1e-8 or top + height > fh + 1e-8:
        raise ValueError("Plot rectangle lies outside the figure")
    return fig.add_axes([left / fw, 1 - (top + height) / fh, width / fw, height / fh], **kwargs)


def measure_layout(fig, axes, relations, *, tolerance_mm=0.3):
    """Measure actual boxes after draw. Each relation is (panel, panel, edge).

    Examples: ('a','b','top'), ('a','c','left'), ('b','c','right').
    Empty checks are NOT a pass. Include colorbars as named axes when needed.
    """
    if not relations:
        raise ValueError("Declare alignment relations; an empty audit cannot pass")
    if not math.isfinite(tolerance_mm) or tolerance_mm <= 0:
        raise ValueError("Alignment tolerance must be finite and positive")
    fig.canvas.draw()
    fw, fh = fig.get_size_inches() * 25.4
    boxes = {}
    for name, ax in axes.items():
        b = ax.get_position()
        boxes[name] = dict(left=float(b.x0 * fw), right=float(b.x1 * fw),
                           top=float((1 - b.y1) * fh), bottom=float((1 - b.y0) * fh),
                           width=float(b.width * fw), height=float(b.height * fh))
    checks = []
    for first, second, edge in relations:
        delta = abs(boxes[first][edge] - boxes[second][edge])
        checks.append(dict(panels=[first, second], edge=edge, delta_mm=round(delta, 6),
                           **{"pass": delta <= tolerance_mm}))
    failures = [r for r in checks if not r['pass']]
    return dict(status='fix_before_publish' if failures else 'pass',
                tolerance_mm=tolerance_mm, checks=checks, failures=failures,
                plot_rectangles_mm=[dict(panel=name, **box) for name, box in boxes.items()])


def pouch_layout(fig):
    """180 x 106 mm recipe: map, separate colorbar, line profile, spanning history.

    Map limits must stay x=0..100, y=0..76 (70 mm pouch plus tabs).
    A 60 x 45.6 mm box preserves equal physical x/y units without shrinking.
    """
    fw, fh = fig.get_size_inches() * 25.4
    if abs(fw - 180) > 1e-6 or abs(fh - 106) > 1e-6:
        raise ValueError("Pouch recipe requires a 180 x 106 mm page")
    boxes = {'a': (18, 8, 60, 45.6), 'b': (113, 8, 53, 45.6),
             'c': (18, 74, 148, 23), 'colorbar': (82, 8, 2.4, 45.6)}
    axes = {key: axes_mm(fig, left=x, top=y, width=w, height=h)
            for key, (x, y, w, h) in boxes.items()}
    relations = [('a', 'b', edge) for edge in ('top', 'bottom', 'height')]
    relations += [('a', 'colorbar', edge) for edge in ('top', 'bottom', 'height')]
    relations += [('a', 'c', 'left'), ('b', 'c', 'right')]
    return axes, relations
