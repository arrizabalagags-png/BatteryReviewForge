# Original figure gallery

These figures are original, editable design examples distributed under the repository's MIT license. All numeric observations are **synthetic**. None are measured data, material rankings or validated electrochemical simulations. Electrode names and protocol settings describe an illustrative example only.

Run `python docs/assets/gallery/render_gallery.py` from the repository to regenerate the seven PNG plates, their PDF/SVG versions, source CSVs, layout manifests and visual contact sheet. The script requires NumPy and Matplotlib; it uses Arial where installed and DejaVu Sans for missing characters and other systems. The theme is read from the bundled `figure_theme.json` file. Text remains editable in SVG and PDF.

| Figure | Content | Raster size |
| --- | --- | --- |
| `ce-demo` | Formation and extended Coulombic-efficiency cycling | 2400 × 1600 |
| `full-cell-demo` | Discharge profiles and capacity cycling | 2400 × 1600 |
| `symmetric-demo` | Full trace and explicitly located time window | 2400 × 1600 |
| `assembled-demo` | Cell geometry, cycling, individual synthetic replicates and voltage | 2400 × 1800 |
| `style-preview` | Identical example curves in six bundled palettes | 2400 × 1800 |
| `lab-primitives` | Six idealized laboratory and cell elements | 2400 × 1800 |
| `morphology-primitives` | Core–shell particles, rods, sheets and an open network | 2400 × 1800 |

Each basename provides `.png`, `.svg`, `.pdf`, and `.layout.json`. CSVs are in `data/`; the equations are directly visible in the renderer. The assembled figure combines independent invented examples to demonstrate layout. It does not describe one combined experiment.

The drawings are deliberately geometric. They do not imply validated atomic bonding, crystal phases, transport pathways, real instrument construction, or a physical scale. The diagrams should be adapted and checked against the actual system before scientific use.

The PNGs are website previews. For a manuscript, set the final physical dimensions and typography, map real data and units, verify the cell/protocol metadata, export fresh vector files, and inspect the complete figure again. Scaling these website plates to a journal column does not itself make them submission-ready.
