#!/bin/sh
# Install standalone skills from an extracted release ZIP into a supported host.
set -eu

overwrite=0
agent=codex
while [ "$#" -gt 0 ]; do
    case "$1" in
        --overwrite) overwrite=1; shift ;;
        --agent)
            [ "$#" -ge 2 ] || { echo 'Missing value for --agent.' >&2; exit 2; }
            agent=$2; shift 2 ;;
        *) echo "Usage: sh install.sh [--agent codex|kimi|dsh] [--overwrite]" >&2; exit 2 ;;
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
[ ! -d "$backup_root" ] || echo "Previous skills preserved at $backup_root. Keep until the new version is checked."
echo 'Only copied is checked. Check discovery, dependencies and PNG/SVG export next.'
