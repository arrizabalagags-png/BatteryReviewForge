---
name: battery-review-polish
description: Polish, translate, or compress existing battery Review prose while preserving evidence, numbers, citations, technical terms, and claim strength. Not for new arguments.
---

# Battery Review prose polish

<!-- execution-contract -->
For model/tool adaptation or resuming a task, read [the execution guide](references/EXECUTION.md). DeepSeek Flash uses short stages and checkpoints; DeepSeek Pro can plan larger text/evidence batches, with the same scientific checks. Show the result, its file link and material unresolved questions; keep logs and recovery records inside the project's `.voltpeer/` folder. Use only capabilities actually available in the current model and host.
<!-- /execution-contract -->

Use this for language, flow, translation, concision, or journal-style adjustment of existing Review text. Preserve the author's intended argument and section structure unless the user asks for a substantive rewrite. When a paragraph lacks evidence, mark the gap; do not hide it with smoother prose.

## Preserve scientific meaning

Keep every value, unit, denominator, battery configuration, tested branch, cycle baseline, condition, source, citation key, and uncertainty attached to the same claim. Do not change `may`, `suggests`, or `is consistent with` into causal certainty. Keep material-level, electrode-level, cell-level, and system-level language distinct. Respect the manuscript's glossary for cathode/anode, lithiation/delithiation, sodiation/desodiation, efficiency, retention, and energy boundary.

If a phrase is ambiguous, propose a precise alternative and flag the decision. If the source is not available, do not assert that a scientific correction is verified. For translation, maintain technical meaning and citation positions while using natural prose in the target language. Avoid repeated template openings, empty claims of novelty, and inflated adjectives. Retain productive caveats and counterevidence.

## Deliverable

Return the revised text in the requested format plus a concise note of any substantive ambiguities or unsupported statements found. For a file edit, show a diff or change summary. If the requested word reduction would delete an essential limitation, explain the tradeoff and offer a shorter supported version. Use `battery-review-write` when the task requires a new section or a change to the article's argument.
