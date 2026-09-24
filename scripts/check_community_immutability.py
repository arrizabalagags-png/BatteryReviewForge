"""Reject edits to an already published Battery Commons id@version on a pull request."""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
base = os.environ.get("BRF_BASE_SHA", "").strip()
if not base:
    print("No PR base SHA supplied; immutability check skipped")
    raise SystemExit(0)

paths = subprocess.run(["git", "ls-tree", "-r", "--name-only", base, "--", "community/styles", "community/layouts"],
                       cwd=ROOT, check=True, capture_output=True, text=True).stdout.splitlines()
changed = []
for relative in paths:
    if not relative.endswith(".json"):
        continue
    prior = subprocess.run(["git", "show", f"{base}:{relative}"], cwd=ROOT, check=True, capture_output=True).stdout
    current = ROOT / relative
    if not current.is_file() or current.read_bytes() != prior:
        changed.append(relative)
if changed:
    print("Published id@version assets are immutable. Submit a new version instead:\n" + "\n".join(changed), file=sys.stderr)
    raise SystemExit(1)
print(f"Checked {len(paths)} existing community paths; no published asset changed")
