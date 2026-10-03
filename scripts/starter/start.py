"""One local launcher around the shipped scientific batteryplot runtime."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
SKILL_ID = "voltpeer-plot"
SKILL = ROOT / "skills" / SKILL_ID
HOST_PATHS = {"dsh": ".dsh/skills", "codex": ".agents/skills"}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(value):
    print(json.dumps(value, ensure_ascii=False))


def package_check():
    manifest = json.loads((ROOT / "PACKAGE_MANIFEST.json").read_text(encoding="utf-8-sig"))
    if manifest.get("resource_id") != "plot_starter" or manifest.get("scientific_runtime") != "batteryplot":
        raise ValueError("Wrong Starter manifest; extract the complete download again.")
    names = set()
    for item in manifest["files"]:
        relative = Path(item["path"])
        path = (ROOT / relative).resolve()
        if relative.is_absolute() or not path.is_relative_to(ROOT) or item["path"] in names:
            raise ValueError("Invalid or duplicate Starter manifest path.")
        names.add(item["path"])
        if not path.is_file() or digest(path) != item["sha256"]:
            raise ValueError("Starter file missing or changed: " + item["path"])
    if not {"start.py", "skills/" + SKILL_ID + "/SKILL.md", "DEMO_INDEX.json"} <= names:
        raise ValueError("Starter manifest lacks required entrypoints.")
    return manifest


def venv_python() -> Path:
    return ROOT / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def runtime_python() -> str:
    python = venv_python()
    if python.is_file():
        return str(python)
    if (ROOT / ".venv").exists():
        raise ValueError("Starter .venv is incomplete; setup was not completed. Use a fresh extracted folder.")
    return sys.executable


def call(args, *, python=None):
    env = {**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8", "MPLBACKEND": "Agg"}
    completed = subprocess.run([python or runtime_python(), *map(str, args)], cwd=ROOT,
                               env=env, capture_output=True, text=True, encoding="utf-8")
    if completed.returncode:
        error = completed.stderr.strip() or completed.stdout.strip()
        if "ModuleNotFoundError" in error:
            error = "Plotting dependencies are not ready. Run python start.py setup in this folder."
        raise ValueError(error or "The local command failed; no successful result was recorded.")
    return completed.stdout.strip()


def setup(args):
    target = ROOT / ".venv"
    no_links(target)
    marker = target / "voltpeer-starter.json"
    if target.exists() and (target.is_symlink() or not marker.is_file()):
        raise ValueError("Existing .venv is not owned by this Starter; choose a fresh extracted folder.")
    if not target.exists():
        if sys.version_info < (3, 10):
            raise ValueError("Python 3.10 or newer is needed; Python 3.12 is the tested Windows route.")
        call(["-m", "venv", target], python=sys.executable)
        marker.write_text(json.dumps({"resource_id": "plot_starter", "schema_version": 1}) + "\n", encoding="utf-8")
    owned = json.loads(marker.read_text(encoding="utf-8"))
    if owned.get("resource_id") != "plot_starter":
        raise ValueError("The existing environment belongs to another project.")
    if not venv_python().is_file():
        raise ValueError("The Starter environment is incomplete; use a fresh extracted folder.")
    if args.create_only:
        dump({"status": "environment_created", "dependencies": "NOT_INSTALLED", "python": str(venv_python())})
        return
    result = subprocess.run([str(venv_python()), "-m", "pip", "install", "--disable-pip-version-check",
                             "-r", str(SKILL / "requirements.txt")], cwd=ROOT, capture_output=True)
    if result.returncode:
        raise ValueError("Dependency installation failed. Check network/Python, then rerun setup; runtime_ready was not set.")
    check = call(["-c", "import matplotlib,numpy,openpyxl,pptx,pymupdf,PIL,pypdf; import sys; "
                  "assert sys.prefix != sys.base_prefix; print('runtime_ready')"])
    dump({"status": check, "python": str(venv_python()), "api_key": "NOT_REQUIRED"})


def no_links(path: Path):
    for ancestor in [path, *path.parents]:
        if ancestor.is_symlink() or (hasattr(ancestor, "is_junction") and ancestor.is_junction()):
            raise ValueError("Choose a real folder, not a link/junction: " + str(ancestor))


def install(args):
    workspace = args.workspace.absolute()
    if not workspace.is_dir():
        raise ValueError("Create/open your project folder first, then pass --workspace.")
    no_links(workspace)
    workspace = workspace.resolve()
    if args.host == "dsh":
        project = next((p for p in [workspace, *workspace.parents] if (p / ".git").exists()), workspace)
        if project != workspace:
            raise ValueError("DSH uses the nearest Git project root. Open/pass that root explicitly: " + str(project))
    target_root = workspace / HOST_PATHS[args.host]
    destination = target_root / SKILL_ID
    no_links(destination)
    # DSH also scans .agents; avoid installing a second project copy under the other adapter.
    alternate = workspace / HOST_PATHS["codex" if args.host == "dsh" else "dsh"] / SKILL_ID
    legacy_id = "battery-review-figure"
    legacy_paths = [workspace / adapter / legacy_id for adapter in HOST_PATHS.values()]
    if any(path.exists() for path in legacy_paths):
        raise ValueError("Legacy plotting Skill exists. Use the full VoltPeer package's explicit migration; the Starter preserves it and refuses a duplicate.")
    if destination.exists() or alternate.exists():
        raise ValueError("A same-name project Skill exists. Preserve/review it first or choose a fresh project folder.")
    target_root.mkdir(parents=True, exist_ok=True)
    shutil.copytree(SKILL, destination)
    dump({"status": "copied", "host": args.host, "skill": str(destination / "SKILL.md"),
          "discovered": "NOT_TESTED", "next": "Open this project in the host; start a new conversation and locate the actual SKILL.md."})


def deliver(data, metadata, out, args, *, demo=False):
    data, metadata = Path(data).resolve(), Path(metadata).resolve()
    if not data.is_file() or not metadata.is_file():
        raise ValueError("Both --data and --metadata must be actual files.")
    if not demo and (data.is_relative_to(ROOT / "demo") or metadata.is_relative_to(ROOT / "demo")):
        raise ValueError("Bundled synthetic input belongs to the demo command. plot requires your separately reviewed input and mapping.")
    before = [digest(data), digest(metadata)]
    command = [SKILL / "scripts/deliver.py", "--data", data, "--metadata", metadata,
               "--out", out, "--dpi", args.dpi, "--formats", *args.formats]
    if args.style is not None:
        command.extend(["--style",args.style])
    # The scientific runtime validates mappings, NA/NR/NV, units and conditions.
    # This launcher never supplies demo metadata, evidence_state, smoothing or inferred units.
    result = json.loads(call(command))
    if before != [digest(data), digest(metadata)]:
        raise ValueError("Input changed during plotting; stop and recheck the source.")
    dump({"result_folder": result["result_folder"], "preview": result["preview"],
          "data_status": "synthetic_demo" if demo else "author_supplied_not_independently_authenticated",
          "review": "Check scientific anomalies, units, conditions and final-size readability."})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    env_cmd = sub.add_parser("setup", help="Install requirements inside this Starter's isolated .venv; no API key")
    env_cmd.add_argument("--create-only", action="store_true", help="Create the isolated environment without installing dependencies")
    host_cmd = sub.add_parser("install", help="Copy the same Skill to a host's project directory; does not verify discovery")
    host_cmd.add_argument("--host", choices=HOST_PATHS, default="dsh")
    host_cmd.add_argument("--workspace", type=Path, required=True)
    sub.add_parser("styles", help="List available palettes; do not reselect an author-chosen palette")
    inspect = sub.add_parser("inspect", help="Read headers and candidates; empty candidates do not mean unsupported")
    inspect.add_argument("--data", type=Path, required=True)
    inspect.add_argument("--sheet")
    demo_cmd = sub.add_parser("demo", help="Run explicitly synthetic bundled input")
    demo_cmd.add_argument("--kind", default="coulombic_efficiency")
    plot = sub.add_parser("plot", help="Use your data and author-reviewed mapping; no demo scientific defaults")
    plot.add_argument("--data", type=Path, required=True)
    plot.add_argument("--metadata", type=Path, required=True)
    for command in (demo_cmd, plot):
        command.add_argument("--out", type=Path, required=True, help="Working folder; reruns preserve previous versions")
        command.add_argument("--dpi", type=int, default=300, help="Requested preview resolution, not journal approval")
        command.add_argument("--style", help="Explicitly selected palette; omitted keeps mapping style. Changes are recorded; input JSON is unchanged.")
        command.add_argument("--formats", nargs="+", choices=("pdf", "svg", "png", "tiff"), default=["pdf", "svg", "png"])
    check = sub.add_parser("check", help="Verify package files or Working bundle hashes, not scientific truth")
    check.add_argument("--working", type=Path)
    args = parser.parse_args()
    try:
        manifest = package_check()
        if args.command == "setup":
            setup(args)
        elif args.command == "install":
            install(args)
        elif args.command in {"styles", "inspect"}:
            command = [SKILL / "scripts/plot_uploaded.py", args.command]
            if args.command == "inspect":
                command.extend(["--data", args.data.resolve()])
                if args.sheet:
                    command.extend(["--sheet", args.sheet])
            print(call(command))
        elif args.command == "demo":
            demos = json.loads((ROOT / "DEMO_INDEX.json").read_text(encoding="utf-8-sig"))
            if args.kind not in demos:
                raise ValueError("Unknown demo kind; choose one of: " + ", ".join(demos))
            deliver(ROOT / demos[args.kind]["data"], ROOT / demos[args.kind]["metadata"], args.out, args, demo=True)
        elif args.command == "plot":
            deliver(args.data, args.metadata, args.out, args)
        elif args.working:
            sys.path.insert(0, str(SKILL / "scripts"))
            from delivery_contract import check_working_bundle
            errors = check_working_bundle(args.working.resolve())
            if errors:
                raise ValueError("; ".join(errors))
            dump({"file_integrity": "PASS", "scientific_and_visual_review": "NOT_PERFORMED"})
        else:
            dump({"package_integrity": "PASS", "version": manifest["version"], "native_host_discovery": "NOT_TESTED"})
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(2, str(error) + "\n")


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="strict")
    main()
