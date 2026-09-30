---
name: battery-experiment-plan
description: Turn a battery research question into a testable variable/control matrix, measurement plan, decision criteria and evidence checklist before experiments; does not configure instruments or replace safety SOPs.
---

# Plan battery experiments

<!-- execution-contract -->
For model/tool adaptation or resuming a task, read [the execution guide](references/EXECUTION.md). DeepSeek Flash uses short stages and checkpoints; DeepSeek Pro can plan larger text/evidence batches, with the same scientific checks. Show the result, its file link and material unresolved questions; keep logs and recovery records inside the project's `.voltpeer/` folder. Use only capabilities actually available in the current model and host.
<!-- /execution-contract -->

Use this when the author needs to decide **what to compare and what evidence would answer the question**. Start with the precise claim, cell chemistry and failure mode or mechanism being tested. Read the author's proposal, existing data and relevant primary protocols before adopting any parameter. If the project is a Review-only task with no new experiment, route to `battery-review-plan` instead.

Produce a plan using [the compact experiment-plan template](assets/EXPERIMENT_PLAN.md). Define one primary response variable, a controlled comparison, and the known confounders. For battery work, explicitly record electrode identity/area/loading, cell type and stack, electrolyte and amount, N/P or lithium excess where relevant, formation history, SOC, temperature, pressure, current density or C-rate, voltage/capacity cutoffs, rest periods, batch and replicate identity. Distinguish what is held constant from what cannot be matched. Do not promise that a comparison is causal while these differ unexplained.

Specify primary and secondary measurements, measurement windows, raw file names/units, and how each proposed figure or metric would be calculated. Give a decision rule and an alternative explanation that would change the conclusion. If the author has not fixed replicates or power, identify that as an unresolved design choice; do not invent a universal sample size. For Aurbach-like CE, transference numbers, EIS fitting, GITT diffusion or self-discharge, write the exact method and required inputs before any calculation. Follow current primary sources and the lab's approved protocol for chemistry-specific settings.

Return a study matrix, sequence, data capture checklist, analysis/figure plan and a short list of unresolved choices. This is a research design aid. The lab's approved safety SOP, chemical hazard review, instrument manual and qualified operator determine safe handling, limits and actual instrument settings. Do not generate an executable cycler program or override those controls from a generic example. Once data exist, use `battery-data-prepare` for traceable column mapping and `battery-review-figure` for plots.
