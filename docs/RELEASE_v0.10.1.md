# VoltPeer 0.10.1 Beta

Prepared on 2026-10-01. This candidate adds a small plotting Starter to the existing 15-Skill distribution. The public source branch remains `codex/public-skills`; a GitHub source push, a tagged Release and the Shanghai ECS deployment are separate actions.

## Start with your data

Download [VoltPeer-Plot-Starter-v0.10.1.zip](downloads/starter/VoltPeer-Plot-Starter-v0.10.1.zip), extract the complete folder and let your agent read `AGENT_GUIDE.md`. It contains the plotting Skill, fixed Python source, six palettes and ten explicitly synthetic demos.

The model identifies the chart and maps the author's actual fields and conditions. It calls the supplied program instead of rebuilding plotting code for every request. `start.py setup` installs dependencies in an isolated `.venv`; `install --host dsh` and `install --host codex` copy the same Skill to their project directories. The installation itself does not require an API key.

An existing palette is preserved. An explicit `--style` selection is recorded without changing the source CSV or mapping JSON. Output versions are retained. Quantitative continuous curves use distinct colors, solid lines, no markers and four plot borders. Missing units, provenance or required scientific conditions stop the request; demos never supply missing author conditions.

## Engineering evidence

- All ten downloaded chart routes exported PDF, SVG and 300 dpi PNG in an isolated Windows environment.
- Thirteen focused tests covered dependencies, installation paths, raw values, explicit palette changes, missing conditions, changed files and preservation of old output.
- The three existing recipe downloads still ran from independent ZIP extractions.
- The current distribution has 37 verified ZIPs, 63 extracted Skill reference/AST checks and 30 canonical demo schema checks.
- All 36 historical 0.10.0 ZIPs remain byte identical.

Details: [Starter execution](validation/2026-10-01-plot-starter.json) and [current distribution verification](validation/2026-10-01-release-distribution.json). The earlier Starter distribution checks remain as historical records. These are software engineering checks, not independent certification of experiments or journal compliance.

## Model and host scope

Client discovery, actual model behavior and operating-system installation are recorded separately. The shortened Starter route was tested with a real DeepSeek Flash API tool session and an actual Codex `gpt-6-luna` collaboration agent. Both independently mapped author-declared synthetic CE inputs and exported PNG/SVG/PDF; 48 raw values, the 100.5% anomaly, colors, solid unmarked curves and four borders passed independent scoring. Luna also stopped on a separate CSV-only input with missing author conditions. Flash's final response still used non-clickable relative paths, so its delivery formatting remains PARTIAL. A separate Codex CLI/ChatGPT-account attempt rejected the Luna model before executing tools.

See [compatibility and exact evidence](COMPATIBILITY.md). These finite runs do not establish full behavior coverage, native desktop Skill discovery or the complete 69-case EVAL. Previous failures are retained with their exact frozen package hashes.

The website source, payment image, credentials and private conversation material remain outside public Skill archives. Website publication is prepared separately for the existing ECS host.
