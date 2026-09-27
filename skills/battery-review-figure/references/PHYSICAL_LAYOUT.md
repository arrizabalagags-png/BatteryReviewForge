# Rendered edges, image aspect and colorbars

Use this when a plot combines a calibrated image/heatmap, colorbar and ordinary axes. File edges and declared axes positions are not sufficient evidence of alignment: `imshow(aspect='equal')` can shrink an axes after placement, and `fig.colorbar(..., ax=...)` can take space from it.

## Repeatable sequence

1. State final page width/height in mm and scientific image x/y limits. Calculate image plot width/height from that aspect ratio; preserve physical calibration. Tabs included in the limits also count toward that ratio.
2. Use `batteryplot.layout.axes_mm`. Place **a separate colorbar axes** and use `fig.colorbar(image, cax=bar_ax)`. Reserve its tick labels and label outside the data axes. Do not use colorbar `fraction`/`pad` to steal space from an already aligned panel.
3. Declare exact relations: same row = top/bottom/height; same column = left/right/width; spanning panel = the leftmost plot's left edge and the rightmost plot's right edge. Include colorbar top/bottom relations when aligned.
4. Draw the full figure, then run `measure_layout(fig, named_axes, relations)`. It reads the **actual** post-render axes. An empty relation list is an error. The native recipe tolerance is **0.3 mm**, stricter than the assembly maximum of 1.5 pt. Never call an aligned group “independent” to avoid the measurement.
5. Inspect tick/axis text, panel letters, colorbar labels and legends visually. Place letters by a shared physical inset from the plot box, not a fractional x-offset that changes with panel width. Align plot boxes without forcing unrelated data to use the same numerical scales.
6. Export on the fixed page. Do not apply per-panel `bbox_inches='tight'`, stretching or separate post-export crop operations after measuring. If any layout-affecting setting changes, redraw and measure again.

## Tested pouch-temperature example

Page: **180 × 106 mm**. Data rectangle x=0–100 mm, y=0–70 mm; full map y limit=76 mm to contain tabs. Recipe: `pouch_layout(fig)`.

| Element | Left | Top | Width | Height (mm) |
|---|---:|---:|---:|---:|
| a: spatial map | 18 | 8 | 60 | 45.6 |
| colorbar | 82 | 8 | 2.4 | 45.6 |
| b: line profile | 113 | 8 | 53 | 45.6 |
| c: history | 18 | 74 | 148 | 23 |

The 60:45.6 ratio matches 100:76. a/b/colorbar share top and bottom; c shares a's left and b's right. The eight edge checks must pass before export. The supplied map, line profile and history must still refer to the same temperature dataset/state; geometry does not establish that link.

The 2026-09-27 correction fixed the showcase generator and its missing audit coverage. Original map/history CSVs did not change. It is not evidence that every possible model or imported image layout has been tested.

## Handoff to the assembly skill

Give the assembler the final-size panel file, measured plot rectangle and intended edge relations. For a raster panel with unknown plot bounds, request an editable source or visually measure and record the box. A blank border detector cannot certify a plot boundary.
