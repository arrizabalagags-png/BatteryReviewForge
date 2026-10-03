# VoltPeer 0.10.2 — local Beta candidate

Prepared on 2026-10-01. This scientific candidate is local and has not been
pushed, tagged or deployed. The separately authorized GitHub README/showcase
update does not publish these packages. Previous 0.10.1 packages are retained.

## Changes under review

- Public synthetic examples now declare their equations, original parameters,
  model-definition sources, assumptions and limits in `scientific_basis`.
- The full-cell recipe and NMC811||Li half-cell are separate models. Coulombic
  loss and capacity relationships are checked only under their declared
  inventory assumptions; they are not universal rules for experimental data.
- Li||Cu stripping includes the declared cutoff; symmetric-cell records use
  an explicit switching timeline. Aurbach reserve and charge calculations have
  an inventory ledger.
- Solar J–V, flow-cell efficiency, iodine capacity, FTIR transmittance and MSD
  have testable calculations rather than unrelated illustrative numbers.
- The Starter adapts the same reviewed source data as the examples, with a
  source hash/model record. Author-supplied anomalies remain unchanged.
- Example bundles include their plotting code and an isolated replay entry.
  The agent still needs to confirm the author's fields, units and conditions
  before adapting this code to another experiment.

## Evidence and boundaries

See `validation/SCIENTIFIC_CORE_2026-10-01.md`,
`validation/SCIENTIFIC_DOMAINS_2026-10-01.md`,
`validation/DEMO_SOURCE_DELIVERY_2026-10-01.md` and the machine-readable records
alongside them. The inventory gate records input and figure hashes; physical
checks are separate tests of declared models. Neither validates a real
material, experimentally fitted parameter or mechanism.

Actual current runs: 18 core tests, 24 domain model/replay tests, 8 source-delivery
tests and 15 Starter tests passed. The Starter ran all ten demo routes and an
actual isolated dependency installation. Source delivery checked 32 bundles
and replayed six representative bundles after extraction into separate paths.
These are separate engineering scopes, not 65 independent validated physical
models. See `validation/SCIENCE_STARTER_2026-10-01.md` for the initial failed
protocol declaration, correction and retained evidence.

This candidate remains Beta. Native desktop discovery, the complete Flash/Pro
69-case behavior suite and macOS delivery have not been validated by these
scientific checks. Historical model trials refer to earlier frozen trees.
