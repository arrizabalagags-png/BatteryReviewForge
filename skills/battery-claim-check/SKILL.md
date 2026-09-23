---
name: battery-claim-check
description: Verify whether cited sources support specific claims, numbers, mechanisms, and references in a battery Review or Perspective. Use for citation audit, not corpus search.
---

# Battery claim and citation check

Use this when a draft, table, caption, or bibliography needs source-level verification. Work from the actual cited paper or authorized full text when possible. A title, abstract, or another Review is insufficient for detailed quantitative or mechanistic claims. If the source is inaccessible, say what remains unverified instead of filling it from memory.

## One claim, one traceable check

For each consequential claim, record a stable claim ID, manuscript location, cited source ID/DOI, exact source page/figure/table/SI location, what the source directly reports, the manuscript's wording, conditions, counterevidence, and a verdict: `supported`, `supported with narrower wording`, `not supported`, or `not verifiable yet`. The [EVIDENCE_LEDGER.csv](assets/templates/EVIDENCE_LEDGER.csv) is an optional starter. Link `source_id` to the source register if one exists; do not count claim rows as unique papers.

Prioritize numbers and units, mechanism/causality, priority or “first” claims, absence claims, safety, scale-up, cost, and the central thesis. Cite primary studies for their own measurements. A Review can support field interpretation, but a citation chain through a Review does not verify a primary measurement.

Check the source's *actual scope*: cell type and format, tested branch and cycle, denominator, conditions, uncertainty, and whether a value is measured, recalculated, or modelled. Use `battery-metrics-audit` for cross-study comparability or a full battery extraction table. Distinguish `NR` (checked source does not report it), `NV` (source or section not yet verified), and `NA` (not applicable).

## Bibliography and negative claims

Verify title, authors, journal, year, DOI, correction/retraction status where relevant, and duplicate records against authoritative source metadata. A plausible DOI is not a verified DOI. Inspect whether cited works actually address the sentence next to the citation; a paragraph-end cluster may mask unsupported intermediate claims.

Bound a negative claim to the searched corpus and date. Prefer “not found in the sources searched through [date]” to an untestable “never reported,” unless a stronger statement has specific evidence. Name what was checked, including standards, protocols, or programs when claiming absence. Record important contradictory papers rather than silently excluding them.

## Completion

Deliver a claim-to-source table or prioritized findings with precise manuscript and source locations. For each failure, propose a narrower sentence, a source to verify, or deletion. Do not polish unsupported wording into apparent certainty or invent citations to close gaps.
