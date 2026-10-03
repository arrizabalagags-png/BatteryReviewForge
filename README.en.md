# VoltPeer · 电研搭子

[简体中文](README.md) · English

**Less time adjusting figures. More time for research.**

Open source AI Skills for battery research: prepare data, plot scientific figures and assemble panels into a Figure. Mechanism illustration, paper writing and polishing are also available.

Choose an example, get its data and source code, then work with your own data. Keep figures and code together so you can check, reproduce and revise them.

A Skill provides instructions and tools for an AI assistant. It runs inside an AI application that can read Skills and execute the required tools.

[Browse examples](https://dazi.gsarrizabalaga.xyz/gallery.html) · [Get started](#get-started) · [Download plotting Starter (0.12.0 Beta)](docs/assets/cycling-rule-v1.2.1/starter/VoltPeer-Plot-Starter-v0.12.0.zip) · [Project website](https://dazi.gsarrizabalaga.xyz/)

## See an example

**Structure and spectra · Original synthetic teaching data, not experimental results.** Diffraction, Raman and spectral-component examples illustrate plotting methods; they do not establish material performance.

<a href="assets/github-showcase/structure-spectra.png"><img src="assets/github-showcase/structure-spectra.png" alt="Synthetic structure and spectra: diffraction intensity, selected progress traces, generic Raman bands and known spectral components; not experimental results" width="780"></a>

[Data and model notes](assets/github-showcase/README.md#structure-and-spectra) · [Plotting source](examples/github_showcase/render.py) · [More examples](https://dazi.gsarrizabalaga.xyz/gallery.html). Click the image for its original size.

<details>
<summary>More examples: EIS, a mechanism illustration and a multi-panel figure</summary>

**EIS · Synthetic circuit data, not an experimental fit.**

<a href="assets/github-showcase/eis-cpe-warburg.png"><img src="assets/github-showcase/eis-cpe-warburg.png" alt="Synthetic EIS: Nyquist, magnitude and phase from the same complex impedance data" width="650"></a>

[Data, code and model basis](assets/github-showcase/README.md#impedance-spectroscopy)

**Lithium-metal interphase · Original conceptual illustration, not experimental validation.**

<a href="assets/mechanism-showcase/desolvation.svg"><img src="assets/mechanism-showcase/desolvation.svg" alt="Lithium-metal interphase concept: coordination, desolvation and transport through the SEI" width="650"></a>

[SVG, source code and scientific references](skills/voltpeer-mechanism/SKILL.md) · [Synthetic multi-panel figure](docs/assets/cycling-rule-v1.2.0/showcase/integrated_study/figure.png) · [Its source and data package](docs/assets/cycling-rule-v1.2.0/split-demos/integrated_study/integrated_study-source.zip)

</details>

## Get started

For your first attempt, follow the **DeepSeek Harness desktop** route. Already using an AI application? See [other installation routes](docs/COMPATIBILITY.md#其他已有软件).

**Codex users can continue using Codex.** Its entry is currently hidden on the website for certain reasons. The Skills retain support for both Codex and DeepSeek Harness (DSH), and the same plotting Starter provides installation routes for both. Follow the [Codex installation notes](docs/COMPATIBILITY.md#其他已有软件) with your existing assistant.

1. **Prepare the application and your project folder.** Follow the [getting started guide](docs/GETTING_STARTED.md#english) to configure the application and model, then open your research project. Check that a conversation works; use the settings checks if the model cannot connect.
2. **Extract the complete Starter and ask your assistant to install it.** Put the `plot_starter` folder in your project. Ask the assistant to read `AGENT_GUIDE.md`, check the environment and install the Skill. Start a new session and confirm that it can locate and read the installed `voltpeer-plot/SKILL.md`. If it cannot, use the [installation checks](docs/GETTING_STARTED.md#english).
3. **Run the example, then use your own data.** Use the bundled program to run a synthetic demo. Open `demo-result/index.html` and inspect PNG, SVG and PDF files in `demo-result/results/`. Repeated runs preserve earlier results in separate versioned folders. Resolve the actual error if files are missing.

The Starter contains **one plotting Skill, a fixed Python program and demos**. It needs Python ≥3.10 and the bundled requirements. Setup downloads dependencies into an isolated environment; no Python interpreter is included.

Once installation is confirmed, copy this to run the demo:

> Read plot_starter/AGENT_GUIDE.md. Check that this session can read the installed plotting Skill and that Python and its dependencies can run. Use the bundled program to run the synthetic demo into demo-result under my project. Check the actual files, then return preview and figure links. If anything fails, explain what is missing instead of reporting completion.

To use your own data:

> Use this example to plot the same type of figure from my data. Confirm the plot type, columns, units and required test conditions first. Use the supplied fixed program and preserve the original data. Ask me about missing information before proceeding.

Confirm a method for unsupported plot types; do not fill gaps with demo parameters or freely rewrite scientific processing logic. You can also describe your request in your own words.

## What you can do

| Your task | What to provide | What you receive |
| --- | --- | --- |
| [Scientific plotting](skills/voltpeer-plot/SKILL.md) | Data, units and test conditions | Supported figures, code and draft captions |
| [Figure assembly](skills/voltpeer-assemble/SKILL.md) | Existing panels, order and target size | An aligned Figure, labels and layout files |
| [Data import](skills/voltpeer-data/SKILL.md) | Original files and field meanings | Prepared tables and mappings; rendering also needs the plotting Skill |
| [Mechanism illustration](skills/voltpeer-mechanism/SKILL.md) | Material system, processes and supporting evidence | Original diagrams, editable SVG and source code |
| [Paper writing](skills/voltpeer-write/SKILL.md) | Author results or verifiable literature | Draft text, evidence links and missing information |
| [Arguments and outlines](skills/voltpeer-plan/SKILL.md) | A research question and existing material | An argument, section structure and evidence gaps |
| [Paper polishing](skills/voltpeer-polish/SKILL.md) | Existing text, purpose and revision needs | Revised, translated or shortened text that preserves scientific meaning |

<details>
<summary>All 16 Skills and their technical IDs</summary>

| Skill | Task |
| --- | --- |
| [`voltpeer-data`](skills/voltpeer-data/SKILL.md) | Prepare data |
| [`voltpeer-plot`](skills/voltpeer-plot/SKILL.md) | Plots, captions and scientific checks |
| [`voltpeer-assemble`](skills/voltpeer-assemble/SKILL.md) | Assemble supplied panels |
| [`voltpeer-mechanism`](skills/voltpeer-mechanism/SKILL.md) | Original mechanism diagrams and editable SVG |
| [`voltpeer-experiment-plan`](skills/voltpeer-experiment-plan/SKILL.md) | Plan experiments and controls |
| [`voltpeer-literature`](skills/voltpeer-literature/SKILL.md) | Search, screen and map literature |
| [`voltpeer-claim-check`](skills/voltpeer-claim-check/SKILL.md) | Check claims against sources |
| [`voltpeer-metrics`](skills/voltpeer-metrics/SKILL.md) | Audit metric comparability |
| [`voltpeer-plan`](skills/voltpeer-plan/SKILL.md) | Plan a Review |
| [`voltpeer-write`](skills/voltpeer-write/SKILL.md) | Write from inspected evidence |
| [`voltpeer-polish`](skills/voltpeer-polish/SKILL.md) | Polish, translate and shorten |
| [`voltpeer-review-audit`](skills/voltpeer-review-audit/SKILL.md) | Audit a manuscript before submission |
| [`voltpeer-submission`](skills/voltpeer-submission/SKILL.md) | Prepare submission materials |
| [`voltpeer-response`](skills/voltpeer-response/SKILL.md) | Prepare revision responses |
| [`voltpeer-reviewer`](skills/voltpeer-reviewer/SKILL.md) | Provide an independent referee-style review |
| [`voltpeer-workflow`](skills/voltpeer-workflow/SKILL.md) | Coordinate a multi-stage project |

</details>

## Common questions

**Do I need to write Python?** You can ask the assistant to call the program using its guide. The application must be able to run tools, and your computer still needs a working Python environment and dependencies.

**Is it free?** VoltPeer is free and open source. Your AI application or model service may charge separately; check its actual terms.

**Do I upload data to the website?** VoltPeer does not require research files to be uploaded to its website. Your application and settings determine what the model provider receives. Check its privacy policy before using unpublished material, and keep API keys in the application's settings.

**Can I submit the output to a journal?** Authors must check original data, units, conditions, citations, the journal's figure requirements and sharing rights. Demo data are not experimental results.

## Current version and documentation

The current source is **0.12.0 Beta, with 16 Skills**. The primary download is the **plotting Starter**. The [full 16-Skill package](docs/downloads/v0.12.0-cycling-rule-v1.2.1/VoltPeer-v0.12.0.zip) and [individual Skill packages and checksums](docs/downloads/v0.12.0-cycling-rule-v1.2.1/download-index.json) are available for installation as needed.

These Beta packages are public in the repository. The latest full stable GitHub Release remains **v0.9.2**, separate from current development. The download index preserves its build-time status; see [version notes and historical downloads](docs/RELEASE_v0.12.0.md) for the current status.

**Installation through figure delivery has not been tested in every client, and full model validation for this version is incomplete.** Run an example first and consult [compatibility](docs/COMPATIBILITY.md) for the actual scope.

[Plotting inputs](skills/voltpeer-plot/references/UPLOADED_DATA.md) · [Figure assembly](skills/voltpeer-assemble/references/COMPOSITION.md) · [Validation records](docs/EVAL.md) · [Maintainer guide](docs/MAINTAINER_GUIDE.md) · [Historical technical reference](docs/TECHNICAL_REFERENCE_v0.10.1.md)

## Authors and licensing

Shuo Guo (郭硕) and Jinlong Jiang (姜金龙), Institute of Energy Materials Science, University of Shanghai for Science and Technology. Affiliations identify the authors and do not imply institutional endorsement.

Repository code and documentation use the [MIT license](LICENSE). Original examples state their licenses in their own notes. Check third-party material, published figures and user data separately for provenance and reuse rights.

[Authors](AUTHORS.md) · [Cite](CITATION.cff) · [Contribute](CONTRIBUTING.md) · [Support](SUPPORT.md) · [Security](SECURITY.md)
