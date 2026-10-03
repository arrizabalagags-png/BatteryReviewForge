# VoltPeer Skill naming and installation migration

The 0.11.0 Beta candidate uses the VoltPeer brand, plugin ID `voltpeer` and 15 canonical `voltpeer-*` Skills. The repository remains `arrizabalagags-png/Voltpeer-skills`. Six main entry points are plotting, Figure assembly, data import and preparation, paper writing, argument/outline planning and polishing; nine supporting workflows remain available. Writing, planning and polishing now include separately documented research-paper and review inputs and deliverables. These instruction contracts do not constitute completed full host/model validation.

## Canonical map

| Legacy ID | Canonical ID | Entry point |
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

`SKILL_MIGRATION.json` is the structured map. `../skill-migration.tsv` carries the identical pairs for the POSIX installer. These are migration aliases, not additional installed Skills. `$battery-review-figure` is a historical invocation; after migration use `$voltpeer-plot`. A host will not automatically resolve the old name through this JSON.

## Existing installations

Extract the complete new package. For DeepSeek Harness desktop use the existing project workspace. Check first:

```powershell
.\install.ps1 -Workspace "C:\Research\project" -CheckOnly
```

```sh
sh install.sh --workspace "/path/to/research project" --check-only
```

Ordinary installation refuses legacy IDs, so it does not leave 15 old and 15 new Skills in discovery. If both the old and new ID already exist for a task, it stops without changing either tree. Codex checks its other discovery roots for both IDs and requests resolving that root first. Links/junctions in source or target paths are rejected.

After reviewing the detected trees, explicitly migrate:

```powershell
.\install.ps1 -Workspace "C:\Research\project" -MigrateLegacy
```

```sh
sh install.sh --workspace "/path/to/research project" --migrate-legacy
```

For Codex/Kimi choose `-Agent Codex` / `-Agent KimiCode`, or `--agent codex` / `--agent kimi`. An explicit `-TargetRoot` / `--target-root` is available when updating the exact existing installation. The installer's copy result does not establish native host discovery.

Complete source trees are staged before any existing tree moves. Legacy trees, including custom instructions, extra files and configuration, are moved byte for byte into a timestamped `.voltpeer-install-backups/<stamp>/legacy/` sibling outside the `skills` discovery directory. Existing canonical Skills require the separate explicit `-Overwrite` / `--overwrite` flag and are saved under `canonical/`. Unrelated Skills and research files are left in place.

The new Skill starts from the checked package. User customisations are preserved in the backup rather than guessed into the new instructions. Review and merge desired customisations manually, applying the alias map to their references. Keep the backups until the new host session locates the actual canonical `SKILL.md` and a small task succeeds. If rollback is needed, move the new canonical tree aside first and restore the exact old backup into the original target; do not leave both discoverable. The installer attempts rollback if a commit-stage file operation fails.

## Package and history boundaries

The full and WorkBuddy candidates are `VoltPeer-v0.11.0.zip`, `VoltPeer-WorkBuddy-v0.11.0.zip`, and `VoltPeer-WorkBuddy-Starter-v0.11.0.zip`. Single packages use the canonical IDs. New plot Starter files are maintained in `scripts/starter/` and its candidate index is under `docs/downloads/v0.11.0/starter/`; original `examples/plot_starter/` remains fixed. Its installer detects old plotting IDs and directs migration through the complete package.

All 34 current ZIPs are under `docs/downloads/v0.11.0/`. The website mirrors this directory to `downloads/v0.11.0/`:

```text
v0.11.0/
  VoltPeer-v0.11.0.zip
  VoltPeer-WorkBuddy-v0.11.0.zip
  VoltPeer-WorkBuddy-Starter-v0.11.0.zip
  download-index.json
  distribution-sha256.txt
  single/<canonical-skill-id>-v0.11.0.zip             (15)
  workbuddy/<canonical-skill-id>-workbuddy-v0.11.0.zip (15)
  starter/VoltPeer-Plot-Starter-v0.11.0.zip
  starter/plot-starter.json
```

`download-index.json` records the exact size and SHA-256 of each current archive. `distribution-sha256.txt` uses paths relative to this version directory. The original `downloads/starter/` and `downloads/recipes/` retain their older files and indexes. For a single `voltpeer-data` install, also install `voltpeer-plot` before requesting rendered plots: the data Skill imports and prepares tables without its own plotting runtime.

Published legacy archive names, scientific examples, immutable community pins and fixed-commit historical source URLs retain their original identity. Old paths can be read at the recorded commit or through their preserved archive. The active tree provides only the 15 new Skill folders; keeping duplicate discoverable aliases would defeat migration.

This is a local naming candidate. Earlier host/model/scientific results belong to their recorded trees. Current naming, installation and package checks are recorded separately; no earlier score or discovery result is automatically transferred. No GitHub release, remote About edit or ECS deployment is performed by the migration scripts.
