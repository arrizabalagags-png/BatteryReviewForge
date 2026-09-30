#!/bin/sh
# Install standalone skills from an extracted release ZIP into a supported host.
set -eu

overwrite=0
agent=dsh
workspace=''
explicit_target=''
while [ "$#" -gt 0 ]; do
    case "$1" in
        --overwrite) overwrite=1; shift ;;
        --agent)
            [ "$#" -ge 2 ] || { echo 'Missing value for --agent.' >&2; exit 2; }
            agent=$2; shift 2 ;;
        --workspace)
            [ "$#" -ge 2 ] || { echo 'Missing value for --workspace.' >&2; exit 2; }
            workspace=$2; shift 2 ;;
        --target-root)
            [ "$#" -ge 2 ] || { echo 'Missing value for --target-root.' >&2; exit 2; }
            explicit_target=$2; shift 2 ;;
        --help|-h) echo 'Usage: sh install.sh --workspace "/path/to/research project" [--overwrite]'; echo 'Advanced: --agent codex|kimi|dsh --target-root "/explicit/skills"'; exit 0 ;;
        *) echo "Usage: sh install.sh --workspace \"research folder\" [--overwrite] [--agent codex|kimi|dsh] [--target-root PATH]" >&2; exit 2 ;;
    esac
done

package_root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
source_root="$package_root/skills"
case "$agent" in
    codex) target_root="${CODEX_HOME:-$HOME/.codex}/skills" ;;
    kimi) target_root="${KIMI_CODE_HOME:-$HOME/.kimi-code}/skills" ;;
    dsh) target_root="${DSH_HOME:-$HOME/.dsh}/skills" ;;
    *) echo "Unknown agent: $agent. Choose codex, kimi, or dsh." >&2; exit 2 ;;
esac
if [ -n "$workspace" ]; then
    [ "$agent" = dsh ] || { echo '--workspace requires --agent dsh.' >&2; exit 2; }
    [ -z "$explicit_target" ] || { echo 'Choose --workspace or --target-root, not both.' >&2; exit 2; }
    [ -d "$workspace" ] && [ ! -L "$workspace" ] || { echo 'Choose an existing real research workspace folder.' >&2; exit 2; }
    workspace=$(CDPATH= cd -- "$workspace" && pwd -P)
    [ ! -L "$workspace/.dsh" ] || { echo 'The workspace .dsh directory is a symbolic link; choose a real project installation.' >&2; exit 2; }
    target_root="$workspace/.dsh/skills"
elif [ -n "$explicit_target" ]; then
    target_root=$explicit_target
elif [ "$agent" = dsh ]; then
    echo 'For DeepSeek Harness desktop, pass --workspace "your research folder". A global CLI profile does not prove desktop discovery.' >&2
    exit 2
fi
if [ ! -d "$source_root" ]; then
    echo "The skills folder is missing. Extract the complete release ZIP first." >&2
    exit 1
fi

count=0
for skill_path in "$source_root"/*; do
    [ -d "$skill_path" ] || continue
    count=$((count + 1))
    skill_name=${skill_path##*/}
    case "$skill_name" in battery-*) ;; *) echo "Unexpected skill name: $skill_name" >&2; exit 1 ;; esac
    [ -f "$skill_path/SKILL.md" ] || { echo "Missing SKILL.md: $skill_path" >&2; exit 1; }
    [ ! -L "$skill_path" ] || { echo "Source skill is a link: $skill_path" >&2; exit 1; }
    if [ "$agent" = codex ] && [ -e "$HOME/.agents/skills/$skill_name/SKILL.md" ]; then
        echo "Same-name skill exists: $HOME/.agents/skills/$skill_name. Check discovery and update that installation instead of adding a duplicate." >&2
        exit 1
    fi
    [ ! -L "$target_root/$skill_name" ] || { echo "Existing skill is a link: $target_root/$skill_name" >&2; exit 1; }
    if [ -e "$target_root/$skill_name" ] && [ "$overwrite" -ne 1 ]; then
        echo "Skill $target_root/$skill_name already exists. Review it first, then rerun with --overwrite." >&2
        exit 1
    fi
done
if [ "$count" -eq 0 ]; then
    echo "No skill folders were found in this package." >&2
    exit 1
fi

mkdir -p "$target_root"
[ ! -L "$target_root" ] || { echo 'Target is a symbolic link; review it manually.' >&2; exit 1; }
backup_root="$(dirname "$target_root")/.brf-install-backups/$(date +%Y%m%d-%H%M%S)-$$"
for skill_path in "$source_root"/*; do
    [ -d "$skill_path" ] || continue
    skill_name=${skill_path##*/}
    case "$skill_name" in battery-*) ;; *) echo 'Unexpected skill name.' >&2; exit 1 ;; esac
    [ ! -L "$target_root/$skill_name" ] || { echo 'Existing skill is a symbolic link; review it manually.' >&2; exit 1; }
    if [ -e "$target_root/$skill_name" ]; then
        mkdir -p "$backup_root"
        mv "$target_root/$skill_name" "$backup_root/$skill_name"
    fi
    cp -R "$skill_path" "$target_root/"
done
echo "Copied $count BatteryReviewForge skills for $agent to $target_root. Start a new agent task and check that the skills appear."
[ -z "$workspace" ] || echo "Open workspace $workspace in DeepSeek Harness desktop and ask a new conversation to locate both figure skills."
[ ! -d "$backup_root" ] || echo "Previous skills preserved at $backup_root. Keep until the new version is checked."
echo 'Only copied is checked. Check discovery, dependencies and PNG/SVG export next.'
