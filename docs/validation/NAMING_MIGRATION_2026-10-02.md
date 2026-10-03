# VoltPeer 0.11.0 Beta — naming, migration and packaging closure

Recorded on 2026-10-02. Status: **PASS for the stated local engineering scope**. The active brand is VoltPeer, the plugin/marketplace technical ID is `voltpeer`, and the repository slug remains `arrizabalagags-png/Voltpeer-skills`. This is a local candidate; this scope performed no remote writes, GitHub Release or ECS deployment.

## Canonical Skill map

| Previous Skill ID | Current Skill ID | Product group |
| --- | --- | --- |
| `battery-review-figure` | `voltpeer-plot` | Primary |
| `battery-figure-assemble` | `voltpeer-assemble` | Primary |
| `battery-data-prepare` | `voltpeer-data` | Primary |
| `battery-review-write` | `voltpeer-write` | Primary |
| `battery-review-plan` | `voltpeer-plan` | Primary |
| `battery-review-polish` | `voltpeer-polish` | Primary |
| `battery-claim-check` | `voltpeer-claim-check` | Supporting |
| `battery-experiment-plan` | `voltpeer-experiment-plan` | Supporting |
| `battery-literature-map` | `voltpeer-literature` | Supporting |
| `battery-metrics-audit` | `voltpeer-metrics` | Supporting |
| `battery-review-audit` | `voltpeer-review-audit` | Supporting |
| `battery-review-forge` | `voltpeer-workflow` | Supporting |
| `battery-review-response` | `voltpeer-response` | Supporting |
| `battery-review-submission` | `voltpeer-submission` | Supporting |
| `battery-reviewer` | `voltpeer-reviewer` | Supporting |

The first six are drawing, Figure assembly, data import, paper writing, argument/outline planning and polishing. Research-paper and Review inputs/deliverables are separately documented in the writing/planning/polishing Skills. A standalone data Skill prepares tables; rendering requires `voltpeer-plot` as well. The map is a migration aid and does not create fifteen duplicate alias Skills or automatic old-name invocations.

## Actual verification scopes

| Scope | Actual result | Limit |
| --- | --- | --- |
| Installer transactions | 26 PASS, including explicit legacy migration, customisation backups, conflicts, missing maps and CRLF maps | PowerShell and Git Bash on Windows; native AI discovery not run |
| Links/junctions | 2 actual Windows junction refusals PASS; 2 file-symlink cases skipped | Windows did not grant file-symlink privilege |
| Final downloaded full package | 2 actual clean installs PASS; each 15 canonical Skills / 232 files with exact SHA-256 closure | New isolated Chinese/space paths, synthetic protection fixture |
| Source Skill entry checks | 15 structural, reference and dependency checks PASS | Structure/declaration; no complete current-model gate |
| Downloaded distribution | 34 new ZIPs / 63 isolated Skill copies PASS | Body, requirements, contracts, assets, safe paths and CRC checks |
| Full ZIP source payload | All 300 source files and the exact member set PASS | Includes installer maps, marketplace and referenced brand logo |
| Separate historical scope | 3 preserved recipe ZIPs and 30 historical demo metadata sets PASS | Preserved earlier versions; not new model/science validation |
| Pre-migration public inventory | 1,159 files, including 194 old ZIPs, byte-identical | Compared with the task's saved baseline, not inferred from Git status |
| Unchanged native code | Native helper and importer hashes match their prior identities | No additional author experiment read or native host execution |

Other meaningful tests retain their own records: portability 16, data preparation 6, reference sync 1, Starter protection/closure 2 and old-install update 1. These totals are not added to the package count or reused as a score. The complete current native-host discovery and model gates remain **NOT_RUN**. The main project's separate eight-case polishing trial does not supply the missing sixteen responses for its complete 24-case gate.

## Protected legacy installations

Ordinary installation, including `Overwrite`, refuses a legacy tree until migration is explicit. An old/new collision stops without changing either tree. The complete old tree and user customisations are moved into a timestamped `.voltpeer-install-backups` sibling outside Skill discovery; explicit canonical overwrites receive their own backup. New source is staged before existing trees move. Ancestor links/junctions are rejected and move/delete targets are bounded. Two real downloaded-package installs preserved the unrelated research fixture. Commit-stage rollback is implemented but no injected rollback-failure test is claimed.

The installed new instructions are fresh; desired customisations can be reviewed and merged from the intact backup. Historical published archive names and source URLs pinned to their recorded commits remain unchanged. Active directories contain the canonical IDs only.

## Language-guide integration addendum

The original corpus engineering `FINAL_AUDIT` and its ten hashes describe the **initial snapshot**: 10 files / 525,075 bytes. The new 0.11.0 integrated Skill has 10 files / **525,484 bytes**. Exactly one file changed: `evaluation_cases.json`, from SHA-256 `afe25df7c8e6a04a5030f8401283cb48c7ed3b94ec93eaf1aee4325a60f237cb` to `d7883ead8ff54c0b4ac54235ccc56a9f8702462eb07aac14ba2b0a5455139f24`.

BP10 accepts the source-strength phrase “is consistent with”; BP22 accepts an equivalent explicit negative translation. A small `engineering_revision` record documents the change. The other nine files, all original case inputs and the 48 deliberately corrupted responses are byte/field-identical to the initial package. The revised checker's actual self-test accepts 24 fixtures and rejects 48 deliberate corruptions; its additional protection guards pass. The 100 DOI records, glossary, domain guide and source/reading boundaries were preserved. This packages original editorial material and bibliographic metadata, not article full texts or figures, and it does not certify model writing quality.

Only 4 candidates were rebuilt: full, polish single, polish WorkBuddy single and WorkBuddy collection. All **30 unaffected new ZIPs** retained their previous bytes. The earlier full package `b841fe5c…` and its two install trials are retained as an intermediate checkpoint, separately from the final identities and install trials below.

## Final local archive identities

| Path relative to the version download root | Bytes | SHA-256 |
| --- | ---: | --- |
| `VoltPeer-v0.11.0.zip` | 1162137 | `ef7dbe2b46b6ea3f9beccaadc685333164b07f4758a85fb5729a36ac8d1b1478` |
| `VoltPeer-WorkBuddy-v0.11.0.zip` | 914107 | `d05dfe58485a7be9fe6db389506aa7a6c58bd8b1313709bc64b5daf6b6e6d602` |
| `VoltPeer-WorkBuddy-Starter-v0.11.0.zip` | 672932 | `d725d24be62ddafface0a61a1490752581d4be66f28016f7f964b4f9f87396fd` |
| `starter/VoltPeer-Plot-Starter-v0.11.0.zip` | 737059 | `e60a22c1f04284a4b7b3eb95c2c78f54aff1d64316a5c4fc098535aec32fbb36` |
| `single/voltpeer-polish-v0.11.0.zip` | 93629 | `c61afc8b6da4c12fa43d83edf1100406f9aba76dace5b5be29d4717619380348` |
| `workbuddy/voltpeer-polish-workbuddy-v0.11.0.zip` | 93868 | `aa5fc7574f88094deac40ab5afe04dc98e6321abffb3665435a13a2aff4545b7` |

All 34 archive identities are in `docs/downloads/v0.11.0/download-index.json`. The checksum file is `docs/downloads/v0.11.0/distribution-sha256.txt`; its lines are relative to **that version directory**. The Starter-specific index is `docs/downloads/v0.11.0/starter/plot-starter.json`. The website uses the equivalent `downloads/v0.11.0/` root. Original `downloads/starter/`, recipes and immutable science/example URLs retain the old files.

```text
docs/downloads/v0.11.0/
  VoltPeer-v0.11.0.zip
  VoltPeer-WorkBuddy-v0.11.0.zip
  VoltPeer-WorkBuddy-Starter-v0.11.0.zip
  download-index.json
  distribution-sha256.txt
  single/<canonical-id>-v0.11.0.zip                 (15)
  workbuddy/<canonical-id>-workbuddy-v0.11.0.zip     (15)
  starter/VoltPeer-Plot-Starter-v0.11.0.zip
  starter/plot-starter.json
```

## Mirror inputs and next owner actions

The exact source-relative list and per-file hashes are in `docs/NAMING_MIGRATION_FILES.json`. Copy the fifteen canonical Skill trees, the ten root guide files, active manifests/README/CHANGELOG/docs, the named public scripts/tests/eval references and the entire new version download directory. Replace the old fifteen directories only in the bounded website source mirror; actual user installations use the explicit migration installer. Copy public scripts individually, preserving the website's own builders and private configuration. Historical examples, old packages, community pins and audit snapshots are not regenerated by this work.

The main agent owns the final website mirror/build, GitHub display/About decision, remote publication and ECS release. Source commit at packaging was `18c659ecc46442497fd7e921161ea951640cc52b` with a dirty worktree; the per-file Skill tree digest identifies the effective packaged source. This report does not represent a new source commit, full model gate, native-client certification or current remote deployment.

Machine evidence: `2026-10-02-naming-integration-v0.11.0.json`, `2026-10-02-naming-distribution-v0.11.0.json`, `2026-10-02-naming-installer-v0.11.0.json`, `2026-10-02-naming-bundle-install-v0.11.0.json`, `2026-10-02-naming-preservation-v0.11.0.json` and the separate intermediate `2026-10-02-naming-checkpoint-01-v0.11.0.json`.
