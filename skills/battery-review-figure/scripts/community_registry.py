"""Resolve an explicitly selected, version-pinned JSON asset; never execute remote code."""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import urlopen

PUBLIC_CATALOG = "https://arrizabalagags-png.github.io/BatteryReviewForge/commons/catalog.json"
ALLOWED_HOST = "arrizabalagags-png.github.io"


def read_bytes(value: str, *, allow_network: bool) -> bytes:
    local = Path(value)
    if local.is_file():
        return local.read_bytes()
    parsed = urlparse(value)
    if parsed.scheme:
        if not allow_network or parsed.scheme != "https" or parsed.hostname != ALLOWED_HOST:
            raise ValueError("Network access needs --allow-network and the official Battery Commons HTTPS host")
        with urlopen(value, timeout=15) as response:
            raw = response.read(2_000_001)
        if len(raw) > 2_000_000:
            raise ValueError("Community JSON is larger than 2 MB")
        return raw
    return local.read_bytes()


def resolve(catalog_location: str, pin: str, output: Path, *, allow_network: bool) -> dict:
    if not pin.startswith("community:") or "@" not in pin:
        raise ValueError("Select an exact version like community:ocean-electrolyte@1.0.0")
    asset_id, version = pin.removeprefix("community:").rsplit("@", 1)
    catalog = json.loads(read_bytes(catalog_location, allow_network=allow_network))
    match = next((item for item in catalog["assets"] if item["id"] == asset_id and item["version"] == version), None)
    if match is None:
        raise ValueError(f"Pinned asset {pin!r} was not found")
    if match["category"] not in {"style", "layout"} or match["status"] not in {"community", "reviewed", "verified", "core"}:
        raise ValueError("Unrecognized asset type or review status")
    source_url = match["source_url"]
    data = read_bytes(source_url, allow_network=allow_network)
    digest = hashlib.sha256(data).hexdigest()
    if digest != match["sha256"]:
        raise ValueError("Community asset hash differs from the catalog; stop and review the source")
    payload = json.loads(data)
    if payload["id"] != asset_id or payload["version"] != version or payload["category"] != match["category"]:
        raise ValueError("Community asset identity differs from the selected pin")
    output.mkdir(parents=True, exist_ok=True)
    asset_file = output / f"{asset_id}@{version}.json"
    asset_file.write_bytes(data)
    lock = {"style_id" if payload["category"] == "style" else "layout_id": pin,
            "asset_id": asset_id, "asset_version": version, "source_url": source_url,
            "sha256": digest, "retrieved_at": datetime.now(timezone.utc).isoformat(),
            "review_status": match["status"], "asset_file": asset_file.name}
    lock_file = output / f"{asset_id}@{version}.lock.json"
    lock_file.write_text(json.dumps(lock, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"asset": str(asset_file), "lock": str(lock_file), "review_status": match["status"]}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pin", help="Exact id and version, e.g. community:ocean-electrolyte@1.0.0")
    parser.add_argument("--catalog", default=PUBLIC_CATALOG)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--allow-network", action="store_true", help="Fetch only from the official HTTPS registry")
    args = parser.parse_args()
    try:
        print(json.dumps(resolve(args.catalog, args.pin, args.out, allow_network=args.allow_network), ensure_ascii=False, indent=2))
    except (ValueError, KeyError, OSError, json.JSONDecodeError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
