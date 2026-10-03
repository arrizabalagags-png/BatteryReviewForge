#!/bin/sh
# Install canonical VoltPeer Skills; preserve prior trees outside discovery.
set -eu
agent=dsh
overwrite=0
migrate=0
check_only=0
cr=$(printf '\r')
workspace=''
explicit_target=''
while [ "$#" -gt 0 ]; do
    case "$1" in
        --overwrite) overwrite=1; shift ;;
        --migrate-legacy) migrate=1; shift ;;
        --check-only) check_only=1; shift ;;
        --agent|--workspace|--target-root)
            [ "$#" -ge 2 ] || { echo "Missing value for $1." >&2; exit 2; }
            case "$1" in --agent) agent=$2 ;; --workspace) workspace=$2 ;; --target-root) explicit_target=$2 ;; esac
            shift 2 ;;
        --help|-h) echo 'sh install.sh --workspace "research folder" [--check-only] [--migrate-legacy] [--overwrite]'; exit 0 ;;
        *) echo "Unknown option: $1" >&2; exit 2 ;;
    esac
done
normalise() {
    if command -v cygpath >/dev/null 2>&1; then cygpath -u "$1"; else printf '%s\n' "$1"; fi
}
real_ancestors() {
    cursor=$1
    while [ -n "$cursor" ]; do
        [ ! -L "$cursor" ] || { echo "Path uses a symbolic link: $cursor" >&2; exit 2; }
        parent=${cursor%/*}
        [ "$parent" != "$cursor" ] || break
        cursor=$parent
    done
}
child() {
    [ "${2%/*}" = "$1" ] || { echo 'A file operation is outside its verified directory.' >&2; exit 2; }
}
package_root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P)
source_root="$package_root/skills"
[ -f "$package_root/skill-migration.tsv" ] || { echo 'Migration map missing. Extract the complete VoltPeer package; no installation was changed.' >&2; exit 2; }
profile_root=$(normalise "$HOME")
codex_home=$(printenv CODEX_HOME || true)
kimi_home=$(printenv KIMI_CODE_HOME || true)
dsh_home=$(printenv DSH_HOME || true)
[ -n "$codex_home" ] || codex_home="$profile_root/.codex"
[ -n "$kimi_home" ] || kimi_home="$profile_root/.kimi-code"
[ -n "$dsh_home" ] || dsh_home="$profile_root/.dsh"
codex_home=$(normalise "$codex_home")
kimi_home=$(normalise "$kimi_home")
dsh_home=$(normalise "$dsh_home")
case "$agent" in
    codex) target_root="$codex_home/skills" ;;
    kimi) target_root="$kimi_home/skills" ;;
    dsh) target_root="$dsh_home/skills" ;;
    *) echo 'Choose --agent codex, kimi or dsh.' >&2; exit 2 ;;
esac
if [ -n "$workspace" ]; then
    [ "$agent" = dsh ] && [ -z "$explicit_target" ] || { echo '--workspace requires dsh and no --target-root.' >&2; exit 2; }
    workspace=$(normalise "$workspace")
    [ -d "$workspace" ] || { echo 'Choose an existing research workspace.' >&2; exit 2; }
    real_ancestors "$workspace"
    workspace=$(CDPATH= cd -- "$workspace" && pwd -P)
    target_root="$workspace/.dsh/skills"
elif [ -n "$explicit_target" ]; then
    target_root=$(normalise "$explicit_target")
elif [ "$agent" = dsh ]; then
    echo 'Use --workspace for desktop installation; a global CLI profile does not prove discovery.' >&2
    exit 2
fi
case "$target_root" in /*) ;; *) target_root="$(pwd -P)/$target_root" ;; esac
real_ancestors "$target_root"
[ ! -e "$target_root" ] || [ -d "$target_root" ] || { echo 'Target must be a directory.' >&2; exit 2; }
legacy_for() {
    if [ -f "$package_root/skill-migration.tsv" ]; then
        while read -r alias_old alias_new; do
            alias_new=${alias_new%"$cr"}
            if [ "$alias_new" = "$1" ]; then printf '%s\n' "$alias_old"; return; fi
        done < "$package_root/skill-migration.tsv"
    fi
}
count=0
legacy_count=0
existing_count=0
[ -d "$source_root" ] || { echo 'Extract the complete VoltPeer package first.' >&2; exit 2; }
for source in "$source_root"/*; do
    [ -d "$source" ] || continue
    name=${source##*/}
    case "$name" in voltpeer-*) ;; *) echo "Noncanonical Skill: $name" >&2; exit 2 ;; esac
    case "$name" in *[!a-z0-9-]*) echo 'Invalid Skill slug.' >&2; exit 2 ;; esac
    [ -f "$source/SKILL.md" ] || { echo "Missing SKILL.md: $name" >&2; exit 2; }
    real_ancestors "$source"
    [ -z "$(find "$source" -type l -print)" ] || { echo "Source contains a link: $name" >&2; exit 2; }
    old=$(legacy_for "$name")
    [ -n "$old" ] || { echo "Skill missing from migration map: $name" >&2; exit 2; }
    if [ -n "$old" ]; then
        case "$old" in battery-*) ;; *) echo 'Invalid migration alias.' >&2; exit 2 ;; esac
        case "$old" in *[!a-z0-9-]*) echo 'Invalid migration alias.' >&2; exit 2 ;; esac
    fi
    if [ "$agent" = codex ]; then
        for other in "$profile_root/.agents/skills" "$codex_home/skills"; do
            [ "$other" != "$target_root" ] || continue
            for candidate in "$name" "$old"; do
                [ -z "$candidate" ] || [ ! -e "$other/$candidate" ] || { echo "Skill exists in another discovery root: $other/$candidate. Review and migrate that root first." >&2; exit 2; }
            done
        done
    fi
    real_ancestors "$target_root/$name"
    if [ -n "$old" ]; then real_ancestors "$target_root/$old"; fi
    if [ -e "$target_root/$name" ]; then existing_count=$((existing_count+1)); fi
    if [ -n "$old" ] && [ -e "$target_root/$old" ]; then
        [ ! -e "$target_root/$name" ] || { echo "Both $old and $name exist; resolve the conflict first. Neither was changed." >&2; exit 2; }
        legacy_count=$((legacy_count+1))
    fi
    count=$((count+1))
done
[ "$count" -gt 0 ] || { echo 'No Skill folders were found.' >&2; exit 2; }
if [ "$check_only" -eq 1 ]; then
    echo "VoltPeer check only: canonical=$count legacy=$legacy_count existing=$existing_count written=false host_discovery=NOT_TESTED"
    exit 0
fi
[ "$legacy_count" -eq 0 ] || [ "$migrate" -eq 1 ] || { echo 'Legacy Skills detected. Review --check-only and docs/NAMING_MIGRATION.md, then explicitly choose --migrate-legacy. No duplicates installed.' >&2; exit 2; }
[ "$existing_count" -eq 0 ] || [ "$overwrite" -eq 1 ] || { echo 'Canonical Skills exist. Review before explicitly choosing --overwrite; backups preserve old trees.' >&2; exit 2; }
mkdir -p "$target_root"
target_root=$(CDPATH= cd -- "$target_root" && pwd -P)
real_ancestors "$target_root"
stamp="$(date +%Y%m%d-%H%M%S)-$$"
stage_base="$(dirname "$target_root")/.voltpeer-install-staging"
backup_root="$(dirname "$target_root")/.voltpeer-install-backups/$stamp"
stage_root="$stage_base/$stamp"
real_ancestors "$stage_root"
real_ancestors "$backup_root"
mkdir -p "$stage_base"
mkdir "$stage_root"
installed=''
rollback() {
    for name in $installed; do child "$target_root" "$target_root/$name"; rm -rf -- "$target_root/$name"; done
    for source in "$source_root"/*; do
        [ -d "$source" ] || continue
        name=${source##*/}; old=$(legacy_for "$name")
        for kind in canonical legacy; do
            candidate=$name
            [ "$kind" != legacy ] || candidate=$old
            [ -n "$candidate" ] || continue
            saved="$backup_root/$kind/$candidate"
            if [ -e "$saved" ]; then
                child "$target_root" "$target_root/$candidate"
                child "$backup_root/$kind" "$saved"
                mv -- "$saved" "$target_root/$candidate"
            fi
        done
    done
    child "$stage_base" "$stage_root"
    [ ! -d "$stage_root" ] || rm -rf -- "$stage_root"
}
trap 'rollback' 0 1 2 3 15
# Stage every complete Skill before moving any existing installation.
for source in "$source_root"/*; do
    [ -d "$source" ] || continue
    cp -R -- "$source" "$stage_root/"
done
for source in "$source_root"/*; do
    [ -d "$source" ] || continue
    name=${source##*/}; old=$(legacy_for "$name")
    for candidate in "$name" "$old"; do
        [ -n "$candidate" ] || continue
        if [ -e "$target_root/$candidate" ]; then
            kind=canonical
            [ "$candidate" = "$name" ] || kind=legacy
            mkdir -p "$backup_root/$kind"
            child "$target_root" "$target_root/$candidate"
            child "$backup_root/$kind" "$backup_root/$kind/$candidate"
            mv -- "$target_root/$candidate" "$backup_root/$kind/$candidate"
        fi
    done
    child "$target_root" "$target_root/$name"
    child "$stage_root" "$stage_root/$name"
    mv -- "$stage_root/$name" "$target_root/$name"
    installed="$installed $name"
done
trap - 0 1 2 3 15
rmdir "$stage_root"
echo "Installed $count canonical VoltPeer Skills in $target_root."
[ ! -d "$backup_root" ] || echo "Old trees/customisations preserved outside discovery: $backup_root. Review wanted changes manually and keep backups until checked."
echo 'File installation only; host discovery, dependencies and an actual export remain to be checked.'
