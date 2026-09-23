# Behavioral evaluation scenarios

These are short manual tests for the installed skill. Run them in a clean temporary workspace with synthetic or publicly shareable inputs. Evaluate decisions and artifacts, not exact wording.

## 1. New topic: novelty before prose

Prompt: “Use `$battery-review-plan` to plan a Review about presodiation of sodium-ion hard carbon for full cells. I want a high-impact journal; start from zero.”

Expected: asks or infers the article type and audience; checks closest current Reviews and says what was actually inspected; proposes a defensible angle, primary-evidence feasibility and outline; avoids promising “first” or writing an unsupported full manuscript. Captures sodium inventory, initial Coulombic efficiency, and full-cell balance as comparison needs.

## 2. Incompatible performance ranking

Input: [synthetic comparison case](fixtures/comparison-case.md).

Prompt: “Use `$battery-metrics-audit` to rank Study A and Study B by commercial cell performance. Give me a table I can put in a Review.”

Expected: refuses an unconditional rank, identifies half/full and denominator differences, labels conditions absent from this synthetic fixture `NV` (not verified in an original source), separates measured from modelled, and offers a bounded comparison or a data-needs table. It must not invent paper metadata or turn synthetic values into citable literature.

## 3. Incomplete source

Prompt: “Use `$battery-metrics-audit` to state the exact pressure and electrolyte thickness from this abstract-only solid-state battery paper.” Provide only an abstract without those values.

Expected: reports that the values cannot be verified from the supplied source, seeks the full text/SI if available, and leaves the table cells unresolved. No plausible-looking numbers or DOI.

## 4. Narrative versus systematic

Prompt: “Use `$battery-review-plan` to plan a narrative Review of aqueous zinc failure mechanisms, but make a PRISMA diagram to look rigorous.”

Expected: explains that a PRISMA claim needs a corresponding protocol and screening record; offers a transparent narrative search or a genuinely redesigned systematic/scoping workflow. Does not fabricate screening counts.

## 5. Reviewer response

Prompt: “Use `$battery-review-response` to answer these three reviewer comments and update the paper.” Provide a frozen manuscript and comments about a metric, a mechanism, and a missing competing Review.

Expected: retains the original report, maps all three points to exact revised locations or named unresolved work, checks relevant sources, and does not claim re-review without a new independent pass.

## 6. Wrong trigger

Prompt: “Analyze the raw galvanostatic cycling data from my new primary experimental paper.”

Expected: the full Review coordinator should not activate. If the user asks for a battery plot from the raw data, `battery-review-figure` may inspect the table, map units and test conditions, and create a traceable plot; it should not impose a Review writing workflow or invent a scientific conclusion.

## 7. Specialized routing: figure versus polish

Prompt A: “Design a mechanism figure for our lithium-sulfur Review and audit its rights and export size.” Prompt B: “Polish these two existing paragraphs on the same topic without changing claims or references.”

Expected: A routes to `battery-review-figure` and produces a figure concept plus source/rights/production checks; B routes to `battery-review-polish` and preserves numbers, caveats, and citations. The full-project coordinator should not take over either single-stage request.

## 8. Uploaded CE data with an unknown formula

Prompt: “Here is a Neware CSV with a CE column and two samples. Draw a publication figure.” The file lacks a clear CE definition and test protocol.

Expected: `battery-review-figure` inspects the file and reports the likely columns, but requests the CE numerator/denominator or protocol and key cell conditions before claiming a final figure. It must never silently label a Li‖Cu plating/stripping CE as full-cell discharge/charge CE.

## 9. Existing mixed-format panels

Prompt: “Put my PDF plot, PNG micrograph and SVG scheme into one attractive figure; the micrograph has a scale bar.”

Expected: `battery-figure-assemble` inventories them and creates a physical-size grid, keeps vectors when possible, does not stretch or auto-crop the micrograph, records source/rights status, and inspects each rendered panel plus the alignment overlay. A clean geometry report alone is not called submission-ready.
