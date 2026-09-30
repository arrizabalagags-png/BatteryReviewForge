---
name: battery-claim-check
description: Verify whether cited sources support specific claims, numbers, mechanisms, and references in a battery Review or Perspective. Use for citation audit, not corpus search.
---

# Battery claim and citation check

<!-- execution-contract -->
For model/tool adaptation or resuming a task, read [the execution guide](references/EXECUTION.md). DeepSeek Flash uses short stages and checkpoints; DeepSeek Pro can plan larger text/evidence batches, with the same scientific checks. Reply in the user's language with the result, usable result/preview links and material unresolved questions. Keep mappings, configuration, logs and recovery records inside the project's `.voltpeer/` folder; do not link them in a normal final reply. Provide the corresponding source record only when the user explicitly requests provenance. Use only capabilities actually available in the current model and host.
<!-- /execution-contract -->

Use this when a draft, table, caption, or bibliography needs source-level verification. Work from the actual cited paper or authorized full text when possible. A title, abstract, or another Review is insufficient for detailed quantitative or mechanistic claims. If the source is inaccessible, say what remains unverified instead of filling it from memory.

## One claim, one traceable check

For each consequential claim, record a stable claim ID, manuscript location, cited source ID/DOI, exact source page/figure/table/SI location, what the source directly reports, the manuscript's wording, conditions, counterevidence, and a verdict: `supported`, `supported with narrower wording`, `not supported`, or `not verifiable yet`. The [EVIDENCE_LEDGER.csv](assets/templates/EVIDENCE_LEDGER.csv) is an optional starter. Link `source_id` to the source register if one exists; do not count claim rows as unique papers.

Prioritize numbers and units, mechanism/causality, priority or “first” claims, absence claims, safety, scale-up, cost, and the central thesis. Cite primary studies for their own measurements. A Review can support field interpretation, but a citation chain through a Review does not verify a primary measurement.

Check the source's *actual scope*: cell type and format, tested branch and cycle, denominator, conditions, uncertainty, and whether a value is measured, recalculated, or modelled. Use `battery-metrics-audit` for cross-study comparability or a full battery extraction table. Distinguish `NR` (checked source does not report it), `NV` (source or section not yet verified), and `NA` (not applicable).

When sources give opposite effects, retain each within-source result and denominator. List the conditions actually verified in common; if E/C or other comparison fields remain NR/NV, do not describe the sources as having identical complete conditions or pool an effect. Missing supplementary information does not erase an already reported opposite result. A percentage-point difference is not a relative percentage change.

Match mechanistic evidence to the exact claim. Cycling, CE and EIS can describe performance or impedance under a declared model; EIS alone is not direct evidence of SEI chemical composition or proof that an additive forms an inorganic-rich SEI. Such a composition claim needs relevant, assigned chemical/structural measurements and controls (for example source-supported XPS), with limitations retained; merely naming an instrument is not verification. Keep a supported observation separate from an unverified causal explanation.

Preserve the original manuscript as an unchanged input. If a copy is requested, use the host's actual file-copy operation and check its byte hash; do not reconstruct a purported unchanged copy from model text. If no copy tool is available, link the retained original and state that no byte-verified copy was made. Write edits to a separately named revision and label it as a revision.

## Bibliography and negative claims

Verify title, authors, journal, year, DOI, correction/retraction status where relevant, and duplicate records against authoritative source metadata. A plausible DOI is not a verified DOI. Inspect whether cited works actually address the sentence next to the citation; a paragraph-end cluster may mask unsupported intermediate claims.

Bound a negative claim to the searched corpus and date. Prefer “not found in the sources searched through [date]” to an untestable “never reported,” unless a stronger statement has specific evidence. Name what was checked, including standards, protocols, or programs when claiming absence. Record important contradictory papers rather than silently excluding them.

## Completion

Deliver a claim-to-source table or prioritized findings with precise manuscript and source locations. For each failure, propose a narrower sentence, a source to verify, or deletion. Do not polish unsupported wording into apparent certainty or invent citations to close gaps.
