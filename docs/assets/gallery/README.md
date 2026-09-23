# Original figure gallery

These figures are original, editable design examples distributed under the repository's MIT license. All numeric observations are **synthetic**. None are measured data, material rankings or validated electrochemical simulations. Electrode names and protocol settings describe an illustrative example only.

Run `python docs/assets/gallery/render_gallery.py` from the repository to regenerate the eleven PNG plates, their PDF/SVG versions, source CSVs, layout manifests and visual contact sheet. The script requires NumPy and Matplotlib; it uses Arial where installed and DejaVu Sans for missing characters and other systems. The theme is read from the bundled `figure_theme.json` file. Text remains editable in SVG and PDF. The figures have no brand header, narrative subtitle or footer; scientific context belongs in the website caption, data files and source/provenance record.

| Figure | Content | Raster size |
| --- | --- | --- |
| `tofsims-demo` | Simulated ion maps, overlay and sputter-time traces | 2232 × 1152 |
| `operando-xrd-demo` | Synthetic state-resolved diffraction map and selected traces | 2232 × 1152 |
| `ce-demo` | Formation and extended Coulombic-efficiency cycling | 2232 × 1152 |
| `full-cell-demo` | Discharge profiles and capacity cycling | 2232 × 1152 |
| `symmetric-demo` | Full trace and explicitly located time window | 2232 × 1152 |
| `assembled-demo` | Cell geometry, cycling, individual synthetic replicates and voltage | 2232 × 1296 |
| `style-preview` | Identical example curves in six bundled palettes | 2232 × 1296 |
| `lab-primitives` | Six idealized laboratory and cell elements | 2232 × 1296 |
| `morphology-primitives` | Core–shell particles, rods, sheets and an open network | 2232 × 1296 |
| `cell-architecture-demo` | Original exploded, idealized Li-metal full-cell stack | 2232 × 1296 |
| `solvation-evidence-demo` | Synthetic stacked Raman spectra and separate RDF examples | 2232 × 1152 |

Each basename provides `.png`, `.svg`, `.pdf`, and `.layout.json`. CSVs are in `data/`; the equations are directly visible in the renderer. The assembled figure combines independent invented examples to demonstrate layout. It does not describe one combined experiment.

The ToF-SIMS example is mathematical, not an acquired ion image. Its two map channels are scaled independently to their own maxima; they cannot be read as relative chemical abundance. The depth trace uses sputter time, not physical depth. The gallery code, two CSV inputs and layout JSON are provided so viewers can inspect exactly how the example was drawn.

The exploded cell is an idealized Al/cathode/separator/Li/Cu stack, with invented texture and exaggerated spacing. It is not a generic specification for every Li-metal cell. The Raman/RDF plate combines independent invented traces to demonstrate a spectral evidence layout; it does not describe one tested electrolyte or prove a coordination mechanism. The operando-XRD plate is an invented peak-shift example; its normalized state is a display coordinate, not a measured state of charge or a phase assignment.

The drawings are deliberately geometric. They do not imply validated atomic bonding, crystal phases, transport pathways, real instrument construction, or a physical scale. The diagrams should be adapted and checked against the actual system before scientific use.

The PNGs are website previews. For a manuscript, set the final physical dimensions and typography, map real data and units, verify the cell/protocol metadata, export fresh vector files, and inspect the complete figure again. Scaling these website plates to a journal column does not itself make them submission-ready.
