---
name: battery-literature-map
description: Search, screen, and map literature for a battery Review, with reproducible queries and distinct source-state counts. Use before evidence synthesis.
---

# Literature mapping and source states

Use this for searching, screening, and source inventory. Use the user's authorized databases and supplied libraries when available. Search the current literature when currency matters; record the search date. For verifying whether citations support specific manuscript claims, use `battery-claim-check`.

## Search and screen

Keep a reproducible search note: databases or sites, query strings and synonyms, date, search fields, filters, and language/access limits. Expand terms across materials, cell configurations, and competing naming conventions. Record an exclusion reason for studies that would materially change the conclusion. Separate original experiments, computational studies, reviews, standards, protocols, editorials, and preprints; a review's summary does not make its cited numbers independently verified.

For a systematic or scoping review, establish eligibility and reporting before screening. Use [PRISMA 2020](https://www.prisma-statement.org/prisma-2020) for systematic reviews or [PRISMA-ScR](https://www.prisma-statement.org/scoping) for scoping reviews when applicable. Preserve [SEARCH_RUNS.csv](assets/templates/SEARCH_RUNS.csv) with raw hits per query/export and [SCREENING_LOG.csv](assets/templates/SCREENING_LOG.csv) with each raw record, duplicate link, title/abstract decision, full-text eligibility decision, and exclusion reason. Reconstruct flow counts from these records; never invent them from the deduplicated source register. A narrative Review can still document its search without claiming a PRISMA-compliant selection process.

Track source states separately: `candidate`, `metadata_verified`, `full_text_obtained`, `SI_obtained`, `read`, `data_extracted`, `claim_used`. Use [SOURCE_REGISTER.csv](assets/templates/SOURCE_REGISTER.csv): one row per unique paper or source, with a stable `source_id` and independent status fields. Use dates for completed states; use `pending`, `unavailable`, or `not applicable` in access-status columns as appropriate. Count distinct `source_id` values that meet each state; never count claim rows as papers. A paper can be read without its SI being obtained, so the states are not one exclusive ladder. An abstract-only source may support that the paper exists or its stated claim, but usually not a detailed methods or numeric comparison.

For extracted claims, hand off stable `source_id` values and exact source locations to `battery-claim-check` or `battery-metrics-audit`. Keep short copyrighted excerpts only as needed for verification; do not publish private PDFs or extracted full text in an open repository.

Useful outputs: search note, screening decisions, source register with distinct-state counts, and a prioritized list of sources needing full text or SI. Deliver only those relevant to the request.
