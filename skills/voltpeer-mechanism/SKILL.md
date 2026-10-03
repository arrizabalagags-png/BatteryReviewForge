---
name: voltpeer-mechanism
description: Create or revise an original battery mechanism schematic from author evidence and literature; choose a scientific template and palette, validate charges and reaction directions, and deliver editable SVG with reproducible parameters and sources. Use for solvation, desolvation, interphase, ion transport, metal deposition and conceptual pathways. Do not use this skill to fabricate evidence or trace a publication figure.
---

# VoltPeer mechanism drawing

<!-- execution-contract -->
For model/tool adaptation or resuming a task, read [the execution guide](references/EXECUTION.md). DeepSeek Flash uses short stages and checkpoints; DeepSeek Pro can plan larger text/evidence batches, with the same scientific checks. Reply in the user's language with the result, usable result/preview links and material unresolved questions. Keep mappings, configuration, logs and recovery records inside the project's `.voltpeer/` folder; do not link them in a normal final reply. Provide the corresponding source record only when the user explicitly requests provenance. Use only capabilities actually available in the current model and host.
<!-- /execution-contract -->

Use the scientific catalogue as an evidence contract. For publication illustration
requests, develop an original image-generation composition draft, inspect its
scientific relationships, then reconstruct editable native SVG. The bundled
standard-library renderer is a deterministic base for that reconstruction.
Read `references/scientific-sources.json` and the selected template record before
drawing. Do not read unrelated templates to start a simple task.

## Begin with the evidence

1. Ask for the material/electrode system, charge or discharge direction, intended
   relationship, and supplied measurements or verified literature. Ask only for
   necessary missing conditions. A decorative ionic drawing is not experimental
   evidence. Separate measured support, a conceptual process and a hypothesis.
2. Choose the supported scientific relationship from `references/catalog.json`.
   Its limitations apply. Templates marked rejected_draft are previous visual
   studies, not approved figure candidates. Existing renderer supports monovalent
   Li+, Na+, K+ in coordination, migration/diffusion and dual-path scenes. Spatial
   metal/interphase illustrations are lithium-specific and must remain Li+.
   Zn2+, multivalent ions or reactions not in
   the catalogue require an original revised scientific contract and review;
   do not relabel an unsupported template.
3. Select four distinct categorical colours. The 200-palette website library is
   at https://dazi.gsarrizabalaga.xyz/palettes.html. A downloaded palette record's
   series colours can be copied into the `colors` array. Sequential/diverging
   maps are for quantities, not four material identities. Colour choice must not
   change the mechanism, arrow direction or numerical information.

## Compose, inspect and reconstruct

For a scientific illustration, use an available image-generation tool to create
an original composition draft. Plan electrode perspective or cutaway, solvation
coordination, interphase position, and separate ion/electron paths. Keep text
minimal, leave space for native labels, and use clear material hierarchy.

Use publication figures only to understand general visual grammar and scientific
relations. Do not copy their pixels, geometry or distinctive compositions. The
generated draft is artwork, not measured or simulated evidence. Record the tool
actually used; do not claim a model name or version the host cannot select.

Keep the material or molecular illustration dominant. Use short, fine process
paths with small open arrowheads whose size is independent of line width. Do not
use oversized triangular heads, thick sweeping arrows or decorative flowchart
connectors. Tighten unused space between the depicted stages while preserving
readable labels, distinct paths and the scientific relationship. If a long path
is scientifically necessary, keep it fine rather than enlarging the arrow.

Inspect the draft for ion charge, coordination geometry, interphase placement,
reaction direction and electron confinement. Correct scientific errors before
vector reconstruction. Rebuild shapes, editable labels and paths from your own
draft in native SVG; embedding the raster inside an SVG does not satisfy this
delivery. Keep the generated draft as a separate optional reference asset.

## Render predictably

Create a new result directory and a params.json with `template`, `cation`, four
`colors` hex values, and `background` (`white` or `transparent`). Standalone
use explicit colours, not palette_id lookup. Run:

```sh
python scripts/renderer.py --params result/params.json --output result/mechanism.svg
```

Use the script or a revised native renderer to reconstruct reviewed scientific
geometry. Native text, shapes, groups and arrows stay editable. Read `--help`
if needed. Image generation assists composition and material depiction; it does
not establish a mechanism or replace the evidence checks.
Never overwrite original files or a previous result; use a new result directory.
Keep source code and references with the output. SVG is the native deliverable;
PDF/PNG exports use an available vector editor and must be checked at final size.
Do not claim an export format was produced unless the file exists and opens.

## Scientific and rights checks

- Check ion valence, charge conservation and any written reaction balance.
- Distinguish ion transport, electron paths and process arrows. In an electrolyte,
  never draw a free electron conduction path through the bulk solvent.
- Distances, coordination counts, layer thicknesses and arrow length are schematic
  unless the author provides a quantitative basis. Do not turn them into numbers.
- Do not copy or trace paper pixels, geometry, distinctive composition or logos.
  Reorganise the scientific relation with original shapes. Cite the actual source
  and record which claim it supports. Source-paper licences remain independent
  of this MIT renderer and original SVG.
- Check no cropped labels, distinct colours, sufficient contrast and readable
  typography at the journal's actual final width. A template is not a guarantee
  of acceptance by a journal. Recheck that journal's current requirements.
- Data plots included alongside a schematic keep four spines and continuous
  solid lines with no point markers, unless actual discrete measurements require
  points. Keep original values, units and raw data.

## Delivery

Deliver the editable SVG, params JSON, renderer source and short source/claim
record; confirm where the files are. If evidence is insufficient, label the
figure conceptual/hypothetical and give the specific missing evidence.
Keep command logs and detailed checks in the working directory. Reply with the
result and necessary next step, not the internal log. The same route works in
DSH Flash/Pro and Codex Luna by running the existing source; new model or native
desktop compatibility must not be called verified without a recorded test.
