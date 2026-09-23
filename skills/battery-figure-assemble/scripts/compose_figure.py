"""Inspect sources and assemble a reproducible battery manuscript composite."""

from __future__ import annotations

import argparse
import json

from batterycompose import ComposeError, compose, load_manifest
from batterycompose.inventory import inventory


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    scan = sub.add_parser("inventory", help="Create an asset list and visual contact sheets")
    scan.add_argument("--input", required=True)
    scan.add_argument("--output", required=True)
    make = sub.add_parser("compose", help="Assemble an explicit panel manifest")
    make.add_argument("--manifest", required=True)
    make.add_argument("--out", required=True, help="Extensionless output stem")
    make.add_argument("--strict", action="store_true", help="Block output on every QA warning")
    args = parser.parse_args()
    try:
        if args.command == "inventory":
            result = inventory(args.input, args.output)
            print(json.dumps({"count": result["count"], "contact_sheets": result["contact_sheets"]}, ensure_ascii=False))
        else:
            result = compose(load_manifest(args.manifest), args.out, strict=args.strict)
            print(json.dumps({"status": result["status"], "warnings": result["warnings"],
                              "outputs": result["outputs"]}, ensure_ascii=False))
    except ComposeError as exc:
        parser.exit(2, f"assembly error: {exc}\n")


if __name__ == "__main__":
    main()
