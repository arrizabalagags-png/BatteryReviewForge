# Fixed plotting for beginners

When the author supplies an extracted VoltPeer Plot Starter, use its `start.py` and short `AGENT_GUIDE.md`. Read the installed Skill, the Starter's `INPUT_GUIDE.md` and only the current chart's field/condition section in [UPLOADED_DATA.md](UPLOADED_DATA.md). This fixed short route takes priority over general Review figure-planning requirements for supported numeric uploads. It contains this exact Skill and one `batteryplot` implementation. DSH and Codex only differ in their project installation directory; never create another plotting implementation for the host/model.

Run `python start.py setup` in the Starter directory once to install into its isolated `.venv`. Installation needs no API key. Use `install --host dsh --workspace PROJECT` (Codex: `--host codex`), then verify actual Skill discovery in the host's new conversation. `demo --out PROJECT/demo-result` uses explicitly synthetic bundled inputs. If setup/installation is already complete, proceed with the author's data; do not repeat installation or Demo.

## Author route: one stage target, one factual action

1. `inspect --data DATA`: inspect real headers; an empty candidate list does not reject a chart whose author-confirmed fields match a supported kind.
2. Write independent mapping JSON from actual headers and author-confirmed scientific statements. Keep the author's chosen style; do not run styles or reopen all previews.
3. `plot --data DATA --metadata AUTHOR_MAPPING --out PROJECT/result`: call the fixed program with requested `--dpi` and formats; use real absolute paths.
4. `check --working ACTUAL_RESULT`: check the actual Working files, then inspect the image with available tools or mark visual review pending.
5. Reply in the user's language with a few clickable result/preview links and only genuine anomalies or unresolved questions.

Before an actual relevant tool error, do not load Python implementations, the whole grammar/registry/primary-paper ledger, atlas, styles or audit templates. Use those references for new/unsupported types, mechanisms/evidence figures, manuscript composition or publication audits. The execution guide is for actual host capability questions or recovery. After an implementation/runtime error, read only the affected material and attempt at most two justified repairs; never rewrite the program, relax validation or invent data/conditions.

Author-confirmed mappings and conditions belong to independent JSON. Required science still stops the route when missing. `source_id` and author-declared `evidence_state=verified` do not authenticate experiments. NA means confirmed inapplicable; NR means checked/unreported; NV means unverified. `direct` only screens matching declared conditions. Missing/different comparison conditions stop that comparison unless the author explicitly requests a valid `contextual` presentation with visible limitations and complete core fields. Neither mode authorizes Demo fallback. Preserve original values, CE anomalies and the chosen palette.

## CE field names at a glance

These are field names and placeholders, not a runnable experimental example. Values must come from the author's actual file and confirmed statements; never copy fixture conditions or fill unknown science to make the command pass.

| Mapping location | Fields to confirm |
| --- | --- |
| `columns` | `series` → `<actual group header>`; `cycle` → `<actual cycle header>`; `ce_pct` → `<actual percent header>`, or both `ce_numerator`/`ce_denominator` with confirmed same basis |
| Core `common` or actual per-row fields | `source_id`, `evidence_state`, `chemistry`, `cell_configuration`, `temperature_c`, `ce_definition`, `rate` |
| Additional multi-series/source direct conditions | `current_density_ma_cm2`, `areal_capacity_mah_cm2`, `cutoff_rule`, `ce_protocol`, `loading_mg_cm2`, `electrolyte_ul_mg`, `voltage_window_v` |
| Figure metadata | confirmed `kind`, `style`, `claim`, `caption_notes`; optional `width_mm` and `height_mm`; `mode`/`condition_note` only according to the actual comparison scope |

Shared confirmed conditions may go in `common`; different conditions remain in their real rows. NA is allowed only where the author confirms inapplicability, not in place of unknown or quantitative values. CE protocol must be per-cycle, not Aurbach average. Preserve percentages above 100% and disclose them; do not clip/smooth. See only the matching CE section of UPLOADED_DATA for the complete contract.

The complete set of supported top-level JSON keys is: `kind`, `style`, `community_style_lock`, `sheet`, `columns`, `common`, `mode`, `condition_note`, `width_mm`, `height_mm`, `sample_id`, `fragment`, `claim`, `caption_notes`. Size is `width_mm`/`height_mm`; resolution is the CLI `--dpi`, not a `dpi` or `figure_size_mm` JSON key. Do not use unsupported keys or an unrelated chart's metadata.
