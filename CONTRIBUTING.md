# Contributing to BatteryReviewForge

Thanks for improving the workflow. Changes should make a battery Review more accurate, easier to audit, or easier to finish.

## Good contributions

- A real failure mode reduced to a shareable, anonymized example.
- A correction to a battery metric, chemistry profile, journal-check rule, or source workflow with a primary paper, official guidance, or a clearly labeled expert rationale.
- A shorter instruction or better task routing that preserves the outcome.
- A new test scenario that reveals a meaningful wrong decision.

Please explain the user request, what the current skill does, what it should do, the evidence for the change, and which scenario would catch a regression. Keep rules conditional where chemistry, article type, or venue changes the answer. Do not turn one paper's suggested loading, electrolyte amount, or pressure into a universal threshold.

## Scientific and publication hygiene

Use only material you may share. Never upload unpublished manuscripts, confidential peer-review correspondence, subscribed PDFs, private datasets, access credentials, institutional download instructions, or copied figures without clear rights. Paraphrase a case and link to public sources when possible. Do not copy text or code from another skill without respecting its license and attribution requirements.

If correcting a source-backed rule, include the DOI or official URL, what part was checked, and any contradictory source. A webpage being reachable does not establish that a manuscript claim is supported by it. For a journal rule, give the official URL, exact article type, and date checked.

## Pull request checklist

1. Edit the relevant specialist `SKILL.md`; add a focused `references/` file only when conditional detail would otherwise crowd its entry point.
2. Update a template only if it improves an actual workflow.
3. Add or adjust a behavioral scenario for a substantive rule change.
4. Run the local skill validator when available, and check relative links and the portable `plugin.json`.
5. State any remaining uncertainty or chemistry-specific limitation in the PR description.

Project maintainers review contributions for scientific fit, clarity, source traceability, and licensing. A contribution may be narrowed before merging if it would over-constrain unrelated batteries or manuscript types.
