---
name: voltpeer-write
description: Draft or restructure battery research papers, Reviews or Perspectives from author-supplied results and checked sources. Use polish for language-only edits, not new sections.
---

# Battery paper drafting and restructuring

<!-- execution-contract -->
For model/tool adaptation or resuming a task, read [the execution guide](references/EXECUTION.md). DeepSeek Flash uses short stages and checkpoints; DeepSeek Pro can plan larger text/evidence batches, with the same scientific checks. Reply in the user's language with the result, usable result/preview links and material unresolved questions. Keep mappings, configuration, logs and recovery records inside the project's `.voltpeer/` folder; do not link them in a normal final reply. Provide the corresponding source record only when the user explicitly requests provenance. Use only capabilities actually available in the current model and host.
<!-- /execution-contract -->

Use this for a new section, abstract, conclusion, or substantive restructure of a battery paper. Follow the user's requested file format and target journal. Preserve valid existing text, citations, and author decisions; do not replace the whole draft for a local problem. For existing prose needing only language work, use `voltpeer-polish`.

## Choose the article route

For a research paper or short communication using the author's actual experiments, read [research-paper writing](references/RESEARCH_PAPER.md). Methods and Results must follow the supplied records; missing experiments, statistics or conditions remain missing. For a Review/Perspective, use the synthesis instructions below. When the user has not specified the article type, infer it from the materials or ask one necessary question; do not quietly treat original results as a literature Review.

## Section construction

Start each major section from its job in the project brief. A useful paragraph usually connects a question, evidence, interpretation, limitation or counterexample, and implication. Vary this pattern when the argument needs it; avoid a mechanical paper-by-paper tour or identical paragraph shapes. Explain why a comparison matters to a materials, cell-design, manufacturing, or research decision.

Distinguish field facts, representative examples, the authors' synthesis, and forward-looking proposals. State scope when the evidence is chemistry- or configuration-specific. If cited papers disagree, examine protocol, denominator, cell architecture, sample count, and mechanism method before smoothing them into one statement. Retain productive disagreement in the final prose.

Before sentence-level polish, inspect title, abstract, section sequence, conclusion, and display items against the current brief. Verify that the designated centre of the Review still carries appropriate space and evidence, and that each figure is owned by a section and says one clear thing. Measure actual prose word counts by section for the venue limit; do not confuse markup or legends with body text. Propose a brief amendment when the argument truly changes. Use `voltpeer-plot` for visual design, source, rights, and export checks.

## Language and terminology

Use one term for each defined concept, with distinctions where a single label would hide important differences: cathode/anode under charge versus discharge, sodiation/desodiation or lithiation/delithiation, capacity basis, cycle-life baseline, nominal versus measured energy, and “practical” versus “commercial.” Avoid “breakthrough,” “unprecedented,” or “universal” unless a bounded comparison supports it. Do not convert “may enable” in a source into “enables” in the manuscript.

Edit for clarity after claim-to-source checks. If an unsupported sentence is attractive, flag it for evidence or remove it rather than polishing it into authority. Preserve authorial voice and the journal's article type.

## Editing outcomes

For a requested draft or rewrite, deliver the text or edited file plus a short change log and unresolved evidence checks. Do not claim journal readiness merely because the prose reads smoothly.
