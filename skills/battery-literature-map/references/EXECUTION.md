# Reliable work across models and interruptions

Read for multi-step work, a model switch, interrupted output, large input sets, or a failed check. For one local correction, keep the existing task record rather than creating a new workflow. These modes describe execution needs, not a model ranking; price and context-window size are not capability tests.

## Choose the amount of guidance

- **Guided (default when capabilities are unverified):** inventory one input group; confirm only material ambiguities; use a matching bundled recipe; produce one preview; inspect it; then process the next group. Keep one concrete next action. Ask the tool for small extracts rather than loading all PDFs, CSV rows, or reference files. Reuse working code. A successful pilot permits batching.
- **Adaptive:** when tools and a pilot work reliably, the model may compare layouts, choose processing batches, write code for a supported contract, or improve composition. Keep scientific constraints and user choices fixed. Do not invent a quantitative panel pairing, missing protocol, denominator, quotation, or source. Check code outputs and actual previews before reporting completion.
- **Review:** independently compare output with source data/pages and the declared requirements. Inspect final-size figures. A reviewer using the same model is a second pass, not independent validation or guaranteed correctness. Mark visual review pending if the current model cannot inspect the rendered image.

Use available tool/vision capabilities, a user's stated preference, and observed failures to choose. Do not claim to know a hidden model identity. If an image is unreadable or vision unavailable, request editable data or a readable export. For unavailable execution, provide a script and clearly report it as not run. Do not repeatedly change science or relax checks to accommodate a limited model.

## Keep a compact project record

For work crossing files or stages, copy `assets/templates/TASK_STATE.json` into the author's chosen output folder. Keep one record per task; preserve any previous task or ask which project to continue. Do not place credentials, private conversation transcripts, or entire datasets in it. Record:

- User objective, scope, selected skill, mode, and explicit choices: language, style ID, physical size, target journal, time/cost preference if supplied.
- Input paths and SHA-256; units, mappings, protocols, conditions, denominators and evidence state. Unknown values stay `null` with a pending question; unknown is not zero or “not reported.”
- Completed steps with output paths and hashes; checks actually run with pass/fail/pending and evidence paths. A plan or remembered assertion is not evidence of completion.
- Remaining issues and one concrete next action. Keep summaries concise; full source data, logs and page references live in linked files.

Save after a meaningful stage, before a long batch, and when changing tools/models. Do not rely on being warned before context compression. On resume, read the record, this skill's essential rules and only the needed reference. Verify input/output hashes and pending questions first. If files changed, mark affected work for recheck; do not silently use old QA or overwrite the author's edits. Apply the user's latest explicit correction to the record while preserving unrelated decisions. Conflicting or missing material instructions require clarification, not a guess.

## Limits and budget

Chunk long papers by figure or section, large tables by schema plus relevant groups, and large outputs into files. Keep DOI/page/panel anchors across chunks. Record coverage so an excerpt is not described as a full-paper review. Estimate batch cost only from verified current pricing and measured or explicitly assumed use; no fixed per-figure quote from an API rate or WorkBuddy plan alone. Respect a user-specified budget; do not switch to paid models or expand external actions on the skill's authority.

If output is truncated, save the last verified artifact and next action, then resume from that point. If the same error repeats after one targeted repair, report the concrete obstacle and keep the partial files; do not run unbounded retries or remove validation. Platform content/file restrictions remain in force; use a supported format or explain the limitation, never obfuscate inputs to evade it.

## Verify before handoff

Run `python scripts/check_task_state.py PATH/TO/TASK_STATE.json` after updating the record. It checks structure, hashes, pending requirements and evidence-file existence. It cannot certify the scientific truth of a check or perform visual inspection. Mark `status=complete` only after required checks actually pass and the user can open the promised outputs. Report what was made, where it is, and any checks still pending. Do not ask the author to approve each routine step when already authorized.
