---
name: battery-review-polish
description: Polish, translate, or compress existing battery Review prose while preserving evidence, numbers, citations, technical terms, and claim strength. Not for new arguments.
---

# Battery Review prose polish

<!-- execution-contract -->
For multi-step work or resuming after interruption, use [the execution and recovery guide](references/EXECUTION.md). Save verified inputs, user choices, pending conditions, outputs and the next action in the project's `TASK_STATE.json`; check file hashes before resuming. Start with guided execution when tool/vision capabilities are unverified; allow adaptive planning after a successful pilot. All modes retain the same scientific and output checks. For a one-step edit, keep the existing record and proceed directly.
<!-- /execution-contract -->

Use this for language, flow, translation, concision, or journal-style adjustment of existing Review text. Preserve the author's intended argument and section structure unless the user asks for a substantive rewrite. When a paragraph lacks evidence, mark the gap; do not hide it with smoother prose.

## Preserve scientific meaning

Keep every value, unit, denominator, battery configuration, tested branch, cycle baseline, condition, source, citation key, and uncertainty attached to the same claim. Do not change `may`, `suggests`, or `is consistent with` into causal certainty. Keep material-level, electrode-level, cell-level, and system-level language distinct. Respect the manuscript's glossary for cathode/anode, lithiation/delithiation, sodiation/desodiation, efficiency, retention, and energy boundary.

If a phrase is ambiguous, propose a precise alternative and flag the decision. If the source is not available, do not assert that a scientific correction is verified. For translation, maintain technical meaning and citation positions while using natural prose in the target language. Avoid repeated template openings, empty claims of novelty, and inflated adjectives. Retain productive caveats and counterevidence.

## Deliverable

Return the revised text in the requested format plus a concise note of any substantive ambiguities or unsupported statements found. For a file edit, show a diff or change summary. If the requested word reduction would delete an essential limitation, explain the tradeoff and offer a shorter supported version. Use `battery-review-write` when the task requires a new section or a change to the article's argument.
