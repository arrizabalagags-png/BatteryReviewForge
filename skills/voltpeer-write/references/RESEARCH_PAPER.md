# Research-paper writing from author-owned evidence

Use this route for a battery research article, short communication or a section reporting the author's actual experiments. For a Review/Perspective, use the main Skill's synthesis route. Polishing existing text without changing its argument belongs to `voltpeer-polish`.

## Start from the supplied claim and result

Establish the requested section, article type, target language, author-approved scientific question and available materials. Reuse the project brief when one exists. Ask only for missing information that prevents the requested section. A local paragraph edit does not require an entire manuscript intake.

Sources may include existing methods, figure files, checked numerical tables, analysis outputs, notes and inspected references. Record which source actually supports each proposed factual statement. Preserve source filenames and checks in `.voltpeer/`; show the user only a necessary evidence question or a short unresolved list.

An outline or phrasing alternative may be proposed when the author has not fixed the argument, but label it as a proposal. Do not manufacture the central scientific finding, a comparison with unseen literature, or a mechanism to make the draft appear complete.

## Assign one job to each section

| Section | Its job | Required evidence |
|---|---|---|
| Title / abstract | State the bounded question, method or finding and its meaning | Author-approved claim and checked main results; no new fact or unsupported novelty |
| Introduction | Explain the problem, relevant prior work, unresolved question and scope | Inspected primary sources with read-depth recorded; use proposal wording for a gap not yet verified |
| Methods | Describe what was actually done clearly enough to understand or repeat it | Actual materials, preparation, instruments, analysis procedure and relevant conditions; missing parameters remain questions |
| Results | Describe observations and comparisons attached to figures/tables | Actual observations, conditions, uncertainty and denominator; reproduce any requested derived quantity first |
| Discussion | Explain what the results support, counterevidence and limits | Checked results plus inspected sources; distinguish observation, association, interpretation and causality |
| Conclusion | Answer the original question within the tested scope | Already-supported findings; no additional experiment, claim of universality or unverified application |

Do not force a journal-independent IMRaD layout on every paper. Preserve the author's section structure or verify the named venue's current instructions before changing it. Do not claim that wording alone makes a manuscript ready for submission.

## Battery-specific invariants

Keep these attached to the same result throughout drafting:

- Chemistry, electrode role, counter/reference electrode and full-cell versus half-cell configuration.
- Current or C-rate and its capacity basis, loading, active mass or geometric area when relevant, voltage window, temperature and electrolyte quantity when actually reported.
- Charge/discharge capacity, cycle numbering and retention baseline. Do not infer Coulombic efficiency or capacity retention from an incompatible source layer.
- Every reported value, unit, precision, uncertainty, sample count, statistical method and citation key.
- Active-material, electrode, cell and system denominators. An electrode-level `Wh kg⁻¹` result must not become a cell-level energy density through editing.
- Measured versus fitted versus simulated signals, assumed equivalent circuit, and the model's identification limits.

Ask for missing active mass only when converting or discussing mass-specific quantities; plotting a verified voltage-time trace does not require it. Do not inherit the conditions of a demo or another cell. Do not round or standardize reported values silently.

## Write and check

1. Identify the section's reader question and available evidence.
2. Draft only claims supported by those materials; use a clear placeholder or an author question for a necessary missing fact.
3. Separate measured observations from interpretations and comparisons. Preserve qualifiers such as `may`, `suggests`, `under these conditions` and `is consistent with`.
4. Check values, units, figure references, citations, terminology and claim scope against the supplied evidence after every rewrite.
5. Put redundant procedural detail in a suggested Methods/SI/caption location only when the user accepts that structural edit; do not delete information required to interpret the result.

Do not invent replicates, significance, control experiments, fit quality, reference details or additional characterization. A reference search result is not a verified citation for a new mechanistic statement. If only an abstract was inspected, label the evidence limit in the internal source record.

## Deliver

Return the requested draft or edited file first. Add a short explanation of substantive changes and only the unresolved decisions that affect the text. Preserve the old version; file writes use a new version or a diff according to the user's request. Internal evidence ledgers and recovery logs stay in `.voltpeer/` unless explicitly requested.

These instructions support evidence-bound drafting. They do not certify any model's behaviour, reproduce a new experiment or guarantee acceptance by a journal.
