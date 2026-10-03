# Editing battery manuscripts without changing the science

Use this guide to polish, translate or compress text supplied by the author. Repair its expression and make its existing reasoning visible. If a stronger argument would require a new experiment, mechanism, citation or conclusion, identify the gap in the revision notes. Do not fill it with a fluent assertion.

The guide combines independent reading of the [100-paper index](corpus.json) with general editorial principles. The papers provide terminology and concrete evidence boundaries. They do not make every published sentence a model to imitate, and they do not establish official journal policy.

## 1. Set the edit scope from the supplied text

Identify the paper type, section, source language and target journal when this information is available. Use generic scientific prose if no journal is named. A title containing “Nature” does not make flagship Nature length or significance rules applicable to another journal. Check current publisher instructions only when a journal-specific requirement affects the edit.

| Author's task | Editing action | Boundary |
|---|---|---|
| Grammar or fluency | Improve syntax, articles, tense and information order | Preserve every scientific proposition |
| Chinese-to-English translation | Express the same relations in natural English; keep terminology stable | Preserve negatives, qualifiers, quantities and the author's intended comparisons |
| Compression | Remove repetition and combine sentences with the same function | Retain decisive evidence and conclusion-changing qualifications |
| Results restructuring | Order observation, decisive comparison and bounded inference | Keep conflicting evidence visible; retain reproducibility information where required |
| Discussion restructuring | Connect findings, prior work, interpretation and a named boundary | Do not invent a causal explanation or broader application |
| Review polishing | Clarify a synthesis already supported by supplied references | Do not manufacture a consensus, literature gap or comparison |

Choose a reasonable default for cosmetic choices and continue. Ask for clarification only when the unresolved choice changes scientific meaning or the requested deliverable. An isolated sentence does not require a complete manuscript intake.

## 2. Lock facts and terms before rewriting

For the affected passage, keep a compact ledger of protected facts and canonical terms. Record each quantity as a tuple:

`quantity → value → unit → denominator/reference → cell/electrode → protocol/condition → source marker`

For example, the wording around a CE result needs the electrode pair, average or individual-cycle status, plating/stripping capacity, current and cycle range when the draft supplies them. A specific-energy result needs its mass boundary. Preserve these facts during compression even when they require a second sentence.

Keep chemical formulas, stoichiometric subscripts, sample labels, reference-electrode couples, figure/table numbers and citation keys attached to their original claims. Preserve symbols that carry meaning, including `<`, `>`, `≈`, `±`, signs and ranges. Do not turn a range into its midpoint, remove a negative temperature, or turn an approximate value into an exact one.

One material needs one stable name in the affected manuscript. Do not vary “hard carbon”, “carbon host” and “current collector” for elegance if they refer to different objects. Follow the author's established NCM/NMC, CE, SEI and electrolyte naming unless it is ambiguous or demonstrably inconsistent. Expand abbreviations at first relevant use, not repeatedly.

If the draft lacks a denominator needed to understand a result, retain its existing wording and flag the missing denominator. Do not invent active mass, electrode area, excess metal, electrolyte amount or a test temperature. A unit that appears wrong is a factual question, not an invitation to repair the data silently. The corpus itself contains an abstract that uses current units for a purported capacity ([BL010](https://doi.org/10.1039/d5sc07537h)) and a metric-assignment discrepancy between an abstract and its conclusion ([BL050](https://doi.org/10.1002/advs.202514583)).

## 3. Preserve the battery and measurement boundary

| Quantity or term | Preserve in the edited passage | Common meaning-changing edit |
|---|---|---|
| Specific capacity, mAh g⁻¹ | Mass of the stated active material, composite, sulfur, Se or other basis | Replacing material capacity with cell capacity |
| Areal capacity, mAh cm⁻² | Electrode area and supplied loading context | Relabelling it as mAh g⁻¹ or current density |
| Current density, mA cm⁻² | Area normalization | Calling A g⁻¹ an areal current density |
| Specific current, A g⁻¹ | Stated mass basis | Treating it as the absolute current through a pouch cell |
| C-rate | Definition of 1 C and separate charge/discharge rates | Inferring 1 C from a theoretical capacity not specified by the author |
| Capacity retention | Reference capacity, cycle number, current, voltage range and temperature | Replacing post-formation reference with first-cycle capacity |
| Coulombic efficiency | Protocol-specific recovered/input charge ratio and averaging method | Equating it with energy efficiency or capacity retention |
| Energy efficiency / round-trip efficiency | Electrical or system boundary, supplied voltage/energy definitions | Treating high CE as equally high energy recovery |
| Specific energy, Wh kg⁻¹ | Total cell, stack, electrodes, active materials and inclusion of packaging | Dropping an electrode-only or packaging-excluded qualifier |
| Volumetric energy density, Wh L⁻¹ | Cell, stack or electrolyte-volume basis | Exchanging it with gravimetric specific energy |
| Energy retention | Reference energy and the same measurement conditions | Rewriting it as capacity retention |
| N/P | Negative/positive capacity ratio and stated capacity bases | Replacing a capacity ratio with a mass ratio |
| E/S, μL mg⁻¹ | Electrolyte volume per sulfur mass | Replacing it with electrolyte per all active material |
| E/C, g Ah⁻¹ | Electrolyte mass per cell capacity | Equating it with E/S or a volume ratio |
| Ionic conductivity | Unit, temperature and method when supplied | Exchanging S cm⁻¹ with S m⁻¹ or electronic conductivity |
| Transference number | Ion, definition and measurement/model assumptions | Treating it as conductivity or diffusion coefficient |
| Activation barrier / binding energy | Process, sign, units, model and reference states | Relabelling an equilibrium binding energy as a kinetic barrier |
| M / m concentration symbols | Definition actually used in Methods | Silently converting molarity to molality or inferring the denominator from typography alone |

Equivalent typography such as `mA h g−1` and `mAh g⁻¹` may be standardized consistently. A missing hour, changed exponent or different normalization is a scientific change. Do not convert units or calculate a new quantity unless the author requested it and the conversion is explicit and verified.

Discharge capacity divided by charge capacity is a common full-cell CE convention. Metal-deposition protocols often use stripped charge divided by plated charge. Initial efficiency for an insertion electrode may be expressed using extraction/insertion charge. Use the draft's verified definition and protocol rather than imposing one formula on every cell. Preserve average CE versus a single-cycle CE and formation-cycle exclusions. Do not infer capacity retention from a repeated CE product without a verified charge-inventory model; the relation can be altered by compensation between electrodes ([BL003](https://doi.org/10.1038/s41467-025-60833-y)).

Keep electrode pairs explicit. Li||Cu or Na||Cu tests probe plating/stripping reversibility. Li||Li, Na||Na or Zn||Zn tests report symmetric-cell behavior. A full cell couples the specified negative and positive electrodes. Hours in a symmetric cell do not become full-cell cycles, and neither test demonstrates a complete device's energy density. A paper can report all three successfully while using different conditions ([BL024](https://doi.org/10.1038/s41467-025-63902-4)). If an author calls a Li||LFP configuration a half cell, preserve the pairing and resolve the label from the actual Methods and purpose; do not repair the label by guessing the metal inventory.

“Initially anode-free” describes the starting metal inventory. Do not rewrite it as a cell that never forms a metal negative electrode. Keep solid-state, quasi-solid-state, gel and liquid qualifiers tied to the composition actually used. The guide does not infer liquid fraction from a technology label.

For stable names across charge and discharge, “negative electrode” and “positive electrode” can be clearer than role-dependent anode/cathode labels. Respect established manuscript usage and electrochemical direction. Do not reverse the working and counter electrodes or the order of a reference redox couple as a stylistic edit.

## 4. Give each section its scientific job

| Section | Useful sentence order | Editing check |
|---|---|---|
| Title | Object or relationship plus actual advance | Remove generic praise; avoid “first” or “unprecedented” without verification |
| Abstract | Specific problem, study action, central finding, decisive support, bounded implication | Keep only necessary numbers and their metric boundaries; add no result absent from the manuscript |
| Introduction | Relevant problem, credited prior work, exact unresolved question, current approach | Do not create a gap by erasing earlier work or using an unsupported “no study” claim |
| Results | Question/comparison, condition, observation, quantitative support, local inference | A characterization list is not an evidence chain; move broad field implications to Discussion |
| Methods | What was used, what was done, how it was measured or calculated | Preserve electrode loading, electrolyte definition, protocol, model and analysis settings when supplied |
| Discussion | Central finding, synthesis, relation to literature, interpretation, claim boundary, useful next test | Every recap should support a new interpretation; retain credible rival explanations |
| Conclusion | Established contribution and its tested scope | Do not introduce new data or strengthen a mechanism beyond Results |
| Review / Perspective | Synthesis by mechanism or question, comparable conditions, disagreement, open question | Avoid a sequence of disconnected paper summaries or a universal conclusion from mismatched cells |

Results usually use past tense for completed measurements. Established physical relations may use present tense. Discussion can use present tense for the interpretation while keeping completed experiments in past tense. Apply tense to function, not with a global find-and-replace.

Keep the shortest evidence chain that makes the claim assessable. Remove duplicated performance numbers in a paragraph when their authoritative location remains clear and reporting requirements permit it. Compression must retain contrary results, failure regimes and qualifications that change the conclusion. State any proposed relocation to a caption or SI in the revision notes; do not move material without a supplied destination when editing a small excerpt.

## 5. Calibrate mechanism language to the actual evidence

| Evidence available in the draft | Suitable function | Wording that needs more evidence |
|---|---|---|
| Measured peak, morphology, voltage or capacity | Report the observation: increased, shifted, remained, was detected | “Proves” a unique molecular mechanism |
| Fit, simulation or spectral assignment | State the inferred/model-dependent quantity and assumptions | Presenting it as a direct measurement |
| Multiple compatible probes | Explain that findings support or are consistent with an interpretation | Excluding every credible alternative |
| Controlled perturbation that separates rival explanations | State the causal inference licensed by that design | Generalizing it outside the tested material, regime or cell |
| Plausible extension beyond the experiment | Use may/could, and name the unresolved condition | A commercial, safety or universal-performance guarantee |

Raman or NMR changes can support changed coordination. They do not automatically quantify a coordination number, prove the absence of free solvent, or identify the rate-limiting step. MD coordination numbers depend on the first-shell cutoff and model. Calculated binding energies and activation energies answer different questions. XPS and ToF-SIMS probe chemical/depth information within their sampling and fitting assumptions; a surface LiF signal does not establish a uniform bulk interphase. EIS assignments depend on the measurement and equivalent-circuit model; a smaller arc is not itself proof of faster bulk diffusion.

Keep free-water amount, water activity, hydrogen-bond structure and interfacial water access distinct. Solvation, desolvation, adsorption and diffusion are related processes, not synonyms. Anion-rich coordination, inorganic-rich SEI and good full-cell retention are separate links in an evidence chain. Use a causal connective only when the supplied study supports that link.

One calibrated verb is usually enough. Replace stacked uncertainty such as “may perhaps possibly indicate” with the appropriate single marker. Do not automatically weaken an observation that is directly measured; reserve the hedge for its interpretation.

## 6. Use counterexamples to keep implications bounded

- Weak solvent coordination does not by itself guarantee better cycling. Intrinsic solvent reactivity can overturn the trend within a tested solvent series ([BL055](https://doi.org/10.1039/d5sc01495f)). Edit “weaker solvation improves all metal batteries” into the author's narrower tested relation, or flag the unsupported generalization.
- A reactive Na-metal counter electrode can change the working electrode's SEI. A half-cell inference therefore needs its actual cell configuration ([BL069](https://doi.org/10.1002/advs.202504717)). Do not rewrite half-cell observations as intrinsic full-cell behavior.
- Tracking electrolyte decomposition with FTIR is different from identifying every reduced CEI species. Preserve the spectroscopy limitation when combining techniques ([BL068](https://doi.org/10.1002/advs.202518282)).
- A temperature interval needs its tested endpoints and failure boundary. A liquid-sulfur observation at −20 °C did not extend to the lower tested temperature in a representative study ([BL100](https://doi.org/10.1002/advs.202410628)). Do not compress this into unrestricted low-temperature operation.
- No degradation detected by the chosen probes does not establish zero degradation over years. Keep detection and time boundaries visible ([BL084](https://doi.org/10.1002/advs.202514452)).
- Capacity fade can follow supporting-salt reactions and cross-compartment protonation while the active redox molecule remains otherwise intact ([BL086](https://doi.org/10.1021/acsaem.5c03070)). Avoid treating all fade as complete active-material destruction.

These observations license editorial safeguards, not insertion of new scientific arguments into an author's manuscript. Use a counterexample only when the author has supplied or verified the relevant evidence and citation for the requested scientific revision.

## 7. Keep the prose natural and precise

Use a clear subject and an informative verb. Name the object that changed: capacity, overpotential, resistance, solvation population or morphology. Replace “excellent performance was realized” with the measured result when the draft already provides it. Do not manufacture an effect size to make the sentence concrete.

Prefer one main proposition per sentence and one controlling idea per paragraph. A 10–30-word sentence is often easy to read, but it is not a hard gate: factual completeness, equations and necessary conditions take priority. Split an overloaded sentence while keeping quantities attached to the same test. Keep the same technical term instead of introducing elegant synonyms.

Avoid stock promotion such as “a new paradigm”, “paves the way”, “remarkable”, “ultrahigh”, “facile” or “universal” when the text can state a concrete contribution. “Significantly” describes statistical significance only when the supplied analysis supports it; otherwise use the actual magnitude or a neutral comparison. Do not fabricate a statistical test or replicate count. A published paper's promotional phrase is not evidence that the author's result merits it.

Use logical connections that describe the relation: a contrast, a cause, a consequence, an additional test or a qualification. Remove a connector that adds no meaning. Keep punctuation simple and respect an author's requested style.

## 8. Deliver the revision and show material changes

Return the polished passage first. Add three to five short revision notes only when useful. Identify a changed paragraph/section function, a protected metric boundary or an unresolved factual issue. Keep the notes proportionate to the task and avoid dumping the full internal ledger into a short edit.

For substantial Results compression, keep a compact record of what was retained, combined, removed or proposed for relocation, with before/after word counts. Keep the author's complete evidential record and stable citation/figure pointers. For follow-up edits, reuse the terminology ledger and recheck the affected facts; widen the check when a discrepancy warrants it.

The following sentences are original synthetic teaching examples, not article quotations or measured results:

**Results:** “At 25 °C, Zn||Cu cells achieved an average CE of 99.6% over 250 cycles. The test used 1 mA cm⁻² and 1 mAh cm⁻².” The electrode pair, averaging, temperature, cycles, current and plating capacity remain explicit.

**Discussion:** “The Raman shift supports altered Na⁺ coordination, but it does not establish whether ligand exchange limits charging.” The interpretation remains distinct from the observed spectral change.

**Boundary:** “The coating improved cycling at 25 °C; its effect under lean-electrolyte conditions remains untested.” The limitation names the claim's unresolved operating condition without erasing the demonstrated result.
