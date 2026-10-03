---
name: voltpeer-polish
description: Polish, translate, or compress existing battery manuscript prose while preserving evidence, numbers, citations, technical terms and claim strength. Covers research papers and Reviews; not for invented arguments.
---

# Battery manuscript polishing

<!-- execution-contract -->
For model/tool adaptation or resuming a task, read [the execution guide](references/EXECUTION.md). DeepSeek Flash uses short stages and checkpoints; DeepSeek Pro can plan larger text/evidence batches, with the same scientific checks. Reply in the user's language with the result, usable result/preview links and material unresolved questions. Keep mappings, configuration, logs and recovery records inside the project's `.voltpeer/` folder; do not link them in a normal final reply. Provide the corresponding source record only when the user explicitly requests provenance. Use only capabilities actually available in the current model and host.
<!-- /execution-contract -->

Use this for language, flow, translation, concision, or journal-style adjustment of existing battery manuscript text. Identify whether the text is a research article, Review, Perspective or another stated type, and its section's job before editing. Preserve the author's intended argument and section structure unless the user asks for a substantive rewrite. When a paragraph lacks evidence, mark the gap; do not hide it with smoother prose.

## Battery language references

Use the relevant sections of the [battery editing guide](references/battery-language-100/DOMAIN_GUIDE.md) before revising a battery passage. Consult the [terminology guide](references/battery-language-100/GLOSSARY.md) for terms present in the draft and [sentence functions](references/battery-language-100/PHRASE_FUNCTIONS.md) when expression needs repair. These are self-contained references; another polishing Skill need not be installed.

The guide is grounded in 100 inspected author abstracts and 31 selected body paragraphs from 15 articles. This is language and boundary guidance, not 100 full-paper readings or model training. Load the DOI index only to inspect a relevant source, not as routine context for every edit. Never add a corpus fact, citation, mechanism or performance value to the author's text merely because it appears in the guide. Preserve the author's evidence and resolve missing scientific meaning explicitly.

For a substantial edit, first lock the affected values, units, denominators, electrode pairs, test conditions, figure/citation pointers and claim qualifiers in a compact internal ledger. A short passage needs only the facts it contains. The [synthetic evaluation cases](references/battery-language-100/evaluation_cases.json) and conservative checker document engineering checks; their fixture results do not certify a model's prose quality.

## Preserve scientific meaning

Keep every value, unit, denominator, battery configuration, tested branch, cycle baseline, condition, source, citation key, and uncertainty attached to the same claim. Do not change `may`, `suggests`, or `is consistent with` into causal certainty. Keep material-level, electrode-level, cell-level, and system-level language distinct. Respect the manuscript's glossary for cathode/anode, lithiation/delithiation, sodiation/desodiation, efficiency, retention, and energy boundary.

If a phrase is ambiguous, propose a precise alternative and flag the decision. If the source is not available, do not assert that a scientific correction is verified. For translation, maintain technical meaning and citation positions while using natural prose in the target language. Avoid repeated template openings, empty claims of novelty, and inflated adjectives. Retain productive caveats and counterevidence.

## Deliverable

Return the revised text in the requested format plus a concise note of any substantive ambiguities or unsupported statements found. For a file edit, show a diff or change summary. If the requested word reduction would delete an essential limitation, explain the tradeoff and offer a shorter supported version. Use `voltpeer-write` when the task requires a new section or a change to the article's argument.
