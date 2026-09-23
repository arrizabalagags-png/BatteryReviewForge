# Agent compatibility and account setup

Use this reference only when a user asks where or how to install BatteryReviewForge in a particular agent. Check the agent's exact product and version before giving a path. A shared `SKILL.md` format does not imply identical commands, tool permissions, Python environments, or tested behavior.

| Host | Native discovery or import | Project status |
| --- | --- | --- |
| Codex | Repository plugin marketplace; standalone `~/.codex/skills/<name>/SKILL.md` | Plugin and standalone installation tested locally |
| Kimi Code CLI | `~/.kimi-code/skills/<name>/SKILL.md` or `~/.agents/skills/`; `/skill:<name>` | Official format and path confirmed; BatteryReviewForge end-to-end run pending |
| DeepSeek Harness | `$DSH_HOME/skills/<name>/SKILL.md` (default `~/.dsh/skills/`) or `~/.agents/skills/`; also project `.dsh/skills/` and `.agents/skills/` | Official filesystem provider confirmed; BatteryReviewForge end-to-end run pending |
| WorkBuddy | Its Skills UI imports a local skill package; its open platform specifies one `{skill-name}/SKILL.md` bundle and extra frontmatter | Import format confirmed; use a WorkBuddy-specific package; actual client import pending |
| 豆包桌面工作任务 | Product description says it can use Skills | Public third-party `SKILL.md` import contract not established; do not give an invented filesystem path |

For Codex use the [plugin or standalone install instructions](https://github.com/arrizabalagags-png/BatteryReviewForge#install-locally). For Kimi Code and DeepSeek Harness use the extracted repository's `skills/` folders and the matching `install.ps1 -Agent KimiCode` / `install.ps1 -Agent DeepSeekHarness` on Windows, or `sh install.sh --agent kimi` / `sh install.sh --agent dsh` on macOS/Linux. The script copies files; it cannot install the host program or test its model provider. For WorkBuddy, use the separately generated per-skill ZIPs, not the full repository ZIP. Keep the original `SKILL.md` and scripts together.

## Login and API key: two different things

BatteryReviewForge itself has no hosted API, account, subscription, or secret to configure. The **agent host** needs its own model access:

- **Codex:** follow its sign-in flow in the app or CLI. The BatteryReviewForge skill does not require an OpenAI API key; an unrelated OpenAI API application may.
- **Kimi Code CLI:** on first launch use `/login`; official choices include Kimi Code OAuth and a Kimi Platform API key. The latter belongs in Kimi's own login flow, not in this repository or a chat prompt.
- **DeepSeek Harness:** open **Settings → Models** and save the provider key in the host UI. Its documentation says the key is stored in its local credential file and only a redacted descriptor returns to the page.
- **WorkBuddy:** sign in to WorkBuddy. If adding a separate model provider such as Tencent TokenHub, follow WorkBuddy's own provider setup. That provider key is unrelated to the skill package.
- **豆包:** use its official account and built-in capability. Do not claim this repository installs into it until a public import route and a real run have been verified.

Never ask a user to paste a real API key into the BatteryReviewForge website, a chat, a mapping CSV, or a GitHub issue. A static website may link to the host's official instructions but must not accept credentials. Native login is preferable for beginners where available. Python plotting uses local Matplotlib and does not make model API calls by itself; the host model may process prompts and files according to that host's own terms.

## How to report compatibility

Use four distinct terms: **locally verified**, **official format confirmed**, **import route confirmed but untested with this package**, and **unconfirmed**. Never turn a file-format match into a claim that scripts, fonts, journal figures, or all 13 skills work in that host. If a user supplies a version or screenshot, inspect it and update the path only from current product documentation. If a host cannot execute local Python, offer figure planning/audit text and export a runnable script for an environment that can.

## Primary product documentation (checked 2026-09-23)

- [Codex plugin packaging and marketplace](https://developers.openai.com/plugins/build/plugins)
- [Kimi Code CLI Skills](https://www.kimi.com/code/docs/en/kimi-code-cli/customization/skills.html) and [first login](https://www.kimi.com/code/docs/en/kimi-code-cli/guides/getting-started)
- [DeepSeek Harness filesystem Skills](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/skill/skill-filesystem/README.md) and [model provider setup](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/user/guide/providers.md)
- [WorkBuddy open-platform Skill structure](https://open.workbuddy.cn/en/docs/skill), [desktop skill upload](https://free-plat-test.qcloudcdn.com/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Skills-Market), and [optional Tencent provider setup](https://cloud.tencent.com/document/product/1823/131902)
- [豆包 desktop download](https://www.doubao.com/download/desktop); the product's Skills claim does not document a third-party import path.
