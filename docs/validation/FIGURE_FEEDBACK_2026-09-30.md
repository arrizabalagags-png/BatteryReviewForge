# Scientific figure feedback — 2026-09-30

Scope: VoltPeer 0.10.0 Beta candidate, public plotting defaults and saved synthetic examples. The final requested display rule is **solid continuous curves distinguished by colour, without point markers**, including capacity cycling, retention, rate capability, CE and continuous EIS. Independent-observation scatter comparisons retain their data points. It is a project preference; this document does not assert that journals prohibit dashed lines or markers.

## Additional capacity-marker correction

The owner then circled the capacity-cycling panel f in the homepage composite: it still had circles and squares after the initial CE correction. The separate homepage full() renderer and canonical cycling/retention/rate helpers retained legacy marker arguments. The earlier checks inspected only CE markers and layout/font properties, so they did not cover this failure. This is an implementation and verification omission; the new image itself contained the symbols.

The canonical functions, preview CLI and rate/capability showcase are corrected to markerless solid curves. Skill guidance and complete-pack guidance explicitly cover capacity and every composite panel. The showcase exporter and homepage exporter inspect actual Line2D artists before saving; a leaked marker stops export. Independent complete packs record and check exact x/y arrays, linestyle and marker together. Additional tests intentionally insert a marker to confirm rejection and verify that supplied capacity/EIS arrays stay intact.

The previous 102-test pass below is historical and predates this additional correction. Final packaging must run the expanded suite and use newly generated packages; their actual gate and GitHub SHA will be appended after completion.

The additional focused runs used Python 3.12.14: uploaded-data suite **11 tests OK / 4.662 s**, plotting-contract suite **7 tests OK / 1.369 s**, showcase suite **7 tests OK / 3.374 s**. These were three separate runs, not one complete regression. Ten affected showcase plates and their saved PNG/SVG/PDF/metadata were regenerated through the actual-artist gate using generator 1.4; CSV generation was not invoked. Updated teaching data ZIPs were rebuilt before the next full gate.

## Implemented

- The canonical plotting library, six selectable preview styles and saved CE/EIS examples use solid data curves. Cycle, charge/discharge and before/after identities keep explicit legends and distinct colours or shades. The complete full_cell prototype uses the same rule, including its optional measured CE and selected-cycle profiles.
- CE changes affect rendering only. Cycle order, numerical values and anomalous values remain available. The library's existing 99/101% regression still preserves the recorded values. Aurbach/average-protocol CE and per-cycle Li∥Cu CE retain separate meanings.
- The synthetic EIS teaching example declares the generalized Randles circuit **Rs + (CPE || (Rct + W))**. CPE replaces the ideal capacitor; this is an explicit extension of the cited textbook circuit. A and B are model identities, not fitted experimental electrolytes.
- With ω = 2πf, W = σ(1 − j)/√ω and Z = Rs + 1/[Q(jω)^α + 1/(Rct + W)]. Units are Rs/Rct: Ω; Q: S·s^α; α: dimensionless; σ: Ω·s^−1/2. The declared frequency interval remains 100 kHz to 10 mHz.
- Nyquist plots use Z′ and −Z″ in Ω, with equal on-page length per Ω. The display domain includes the entire saved frequency range. Model curves have no decorative sampled-point symbols. The companion phase curve is derived from the same complex impedance CSV.
- The last two selectable styles are now **Graphite minimal** and **Blue and orange**. Their first colours and original stable technical IDs are kept in figure_theme.json; all six charts use the same capacity CSV and limits. The website projects its swatches from that same source.
- The CE, integrated figure, EIS, six-style preview and related saved output files are regenerated from the maintained source. Download data bundles and complete plot packs must be rebuilt before publishing.

## References and limits

- [Gamry, Basics of Electrochemical Impedance Spectroscopy](https://www.gamry.com/application-notes/EIS/basics-of-electrochemical-impedance-spectroscopy/): complex coordinates, semi-infinite Warburg convention and Randles circuit. [Official PDF](https://www.gamry.com/assets/Application-Notes/Basics-of-EIS.pdf), Equation 20 and Figures 19–21. CPE generalization and numeric model parameters are our declared synthetic choices.
- [Adams et al., Accurate Determination of Coulombic Efficiency for Lithium Metal Anodes and Lithium Metal Batteries, DOI 10.1002/aenm.201702097](https://advanced.onlinelibrary.wiley.com/doi/abs/10.1002/aenm.201702097): CE depends on the measurement protocol. We do not copy that paper's numerical performance into the demonstration.
- [Understanding and applying coulombic efficiency in lithium metal batteries, Nature Energy](https://www.nature.com/articles/s41560-020-0648-z): protocol and interpretation context. This is not evidence that fictional model A or B represents an actual cell.

The change does not force author-uploaded EIS to have a semicircle or 45° tail. Real measured arrays are preserved; equivalent-circuit selection, fitting, uncertainty and physical interpretation require supplied conditions and independent review.

## Actual checks before final package rebuild

- Python 3.12.14: style suite **5 tests OK, 3.469 s**; independent per-trace colour/contrast checks, solid defaults and chosen-preset provenance.
- Python 3.12.14: showcase suite **6 tests OK, 1.037 s**; same-source cross-panel relationships, 172 complex impedance rows, ideal-RC circle identity, high-frequency intercept, low-frequency Warburg limit, equal Nyquist unit lengths and markerless/solid CE.
- An initial full run executed **102 tests in 153.664 s**. Two subcases failed because the old EIS and integrated download bundles still contained the previous CSV. That is a real package mismatch, not a science test exemption. Rebuild the bundles, then record the final post-rebuild gate separately below.
- The three original data-only CSVs and CE voltage-profile CSV used for visual comparison are preserved; exact SHA values and website preview evidence are recorded by the private website maintenance task.
- Rendered EIS, CE/integrated figures and six styles were opened for visual inspection. Geometry and script PASS do not constitute experimental or journal certification.

## Initial distribution gate — historical

After rebuilding the mismatched demo bundles, the frozen source completed the entire unittest suite: **102 tests OK in 148.271 s**, Python 3.12.14 / Windows. The path-free record is `2026-09-30-final-regression.json`; the raw local log is excluded from GitHub. This separately records the successful post-rebuild gate and preserves the initial mismatch history above.

The upload task will append the actual refreshed package hashes and verified GitHub commit. Prior 36/62 archive PASS refers to the previous frozen bytes until that new check is recorded. Native DeepSeek Harness, real Flash/Pro model EVAL and macOS remain NOT_RUN; ECS deployment is separate.

## Four data-axis frames — latest teacher feedback

The teacher asked for top, right, bottom and left borders on numeric data plots. This is now a VoltPeer house rule with equal spine widths/colors; ordinary ticks remain on bottom/left. It is not described as a universal publisher requirement. Meaningful independent scatter remains scatter; hidden layout axes, device outlines and colorbar axes do not acquire fabricated data frames.

The prior minimal style hid top/right borders. The maintained style, all three showcase renderer families, specialist CLI/exporter, preview CLI, homepage plates, ten additional domain demos and standalone recipe runtime now enforce visible four-sided data spines. Numeric capacity, CE, spectroscopy and EIS curves remain solid without point markers. The PIL assembly teaching trend uses an actual four-sided rectangle instead of Matplotlib, and was checked separately.

Measured rendering records cover **30 canonical showcase groups (77 data panels), 10 domain demo groups (14 data panels) and 3 homepage plates (17 data panels), total 108**. A deliberately hidden top spine stops the showcase export test. Formal metadata schema checks reject false frame flags, missing conditions, wrong synthetic declarations, stale ZIP/source/site metadata and input bytes. Final freshly packaged regression and archive hashes are appended in the distribution record after regeneration; older 102/104-test passes are historical.

The historical full_cell resource renders an NMC811||Li half-cell. Visible website labels, conditions and linked metadata now say half-cell capacity cycling. Stable technical IDs stay unchanged. Only the integrated-study source index's cell-identity text changed; the original capacity, CE, voltage and style CSV numeric inputs were not rewritten. The separate adaptable full-cell recipe has its own explicitly synthetic graphite/cathode conditions and does not inherit the reference picture's chemistry.

Native DeepSeek Harness discovery, real Flash/Pro model behavior, macOS testing and ECS publication remain NOT_RUN / deferred as recorded separately. Four-sided frames do not constitute scientific validation.

## Current frozen-source regression

The expanded full suite completed **129 tests OK / 257.400 s**, Python 3.12.14 / Windows. Its path-free evidence is `2026-09-30-frame-final-regression.json`. The first expanded run (129 / 263.920 s) failed on an outdated Line2D test for the observed Arrhenius scatter, unsupported `set_marker(None)` cleanup in four negative subcases, and mixed guide line endings. The failed record is preserved in `2026-09-30-frame-regression-initial.json`; the tests now inspect scatter offsets, restore the supported no-marker string, and maintain LF execution guides without weakening data/frame rejection checks. Separate focused 7 / 4 / 6-test runs passed before the new complete run.

Hashes of 128 synthetic CSV and saved-figure files remained unchanged across the complete recheck. CSV Git attributes preserve original input bytes; code/doc source comparison tolerates CRLF/LF checkout normalization, while archive/input/manifest SHA checks remain byte-exact. The assembly Skill now requires checking every panel and asking for source regeneration when a required frame is absent; overlay rectangles must not counterfeit data-axis frames.

The fresh adaptable recipe candidate is `outputs/recipe-packs-0.10.0-frame-final`; its three public copies and index are under `docs/downloads/recipes`. Actual ZIP SHA-256 values are:

| Resource | File | SHA-256 |
| --- | --- | --- |
| full_cell | VoltPeer-full_cell-0.10.0.zip | `1108d4ac32e082ed87537c422a404d0015971c9fc71aecf54ed7d37f2f6713b5` |
| li_li | VoltPeer-li_li-0.10.0.zip | `5434661d77204fdb22ac4b6411334c691ab85124d47ae0614a8eb45feb8bce83` |
| operando_xrd | VoltPeer-operando_xrd-0.10.0.zip | `7240cf74c36bcefb4724b43663758b93cfdc1e486a5de51b9496b2682527bc15` |

Complete archive/source/AST/schema validation and verified GitHub synchronization are recorded in `2026-09-30-distribution.json`, `GITHUB_SYNC_2026-09-30.md` and `docs/downloads/distribution-sha256.txt`; hashes from previous science/marker candidates are historical. These records do not authorize a Stable label or claim a live ECS update.
