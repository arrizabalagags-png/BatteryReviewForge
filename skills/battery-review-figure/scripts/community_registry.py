"""Resolve an explicitly selected, version-pinned JSON asset; never execute remote code."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import build_opener, HTTPRedirectHandler

PUBLIC_CATALOG = "https://arrizabalagags-png.github.io/BatteryReviewForge/commons/catalog.json"
ALLOWED_HOST = "arrizabalagags-png.github.io"
ALLOWED_PATH_PREFIX = "/BatteryReviewForge/commons/"
ALLOWED_RESOURCE_PATH = re.compile(
    r"^/BatteryReviewForge/commons/(?:catalog\.json|(?:styles|layouts)/[a-z][a-z0-9]*(?:-[a-z0-9]+)*@[0-9]+\.[0-9]+\.[0-9]+\.json)$"
)


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError('Community redirects are not permitted; check the exact official URL')


def read_bytes(value: str, *, allow_network: bool, local_root: Path | None = None) -> bytes:
    local = Path(value)
    if local.is_file():
        if local_root is not None and not local.resolve().is_relative_to(local_root.resolve()):
            raise ValueError('Community file is outside the explicitly authorized local directory')
        if local.stat().st_size > 2_000_000:
            raise ValueError('Community JSON is larger than 2 MB')
        return local.read_bytes()
    parsed = urlparse(value)
    if parsed.scheme:
        if (not allow_network or parsed.scheme != "https" or parsed.hostname != ALLOWED_HOST
                or parsed.port not in {None, 443} or parsed.username or parsed.password or parsed.query or parsed.fragment
                or not parsed.path.startswith(ALLOWED_PATH_PREFIX)
                or not ALLOWED_RESOURCE_PATH.fullmatch(parsed.path)):
            raise ValueError("Network access needs --allow-network and a URL under the official Battery Commons path")
        with build_opener(NoRedirect()).open(value, timeout=15) as response:
            raw = response.read(2_000_001)
        if len(raw) > 2_000_000:
            raise ValueError("Community JSON is larger than 2 MB")
        return raw
    return local.read_bytes()


def resolve(catalog_location: str, pin: str, output: Path, *, allow_network: bool, local_root: Path | None = None) -> dict:
    if not pin.startswith("community:") or "@" not in pin:
        raise ValueError("Select an exact version like community:ocean-electrolyte@1.0.0")
    asset_id, version = pin.removeprefix("community:").rsplit("@", 1)
    if not re_full_slug(asset_id) or not re_full_version(version):
        raise ValueError("Community IDs and versions must use a safe exact id@semantic-version pin")
    catalog = json.loads(read_bytes(catalog_location, allow_network=allow_network))
    matches = [item for item in catalog["assets"] if item["id"] == asset_id and item["version"] == version]
    if not matches:
        raise ValueError(f"Pinned asset {pin!r} was not found")
    if len(matches) != 1:
        raise ValueError('Duplicate exact version in catalog')
    match = matches[0]
    if match.get('lifecycle', 'active') not in {'active', 'deprecated'}:
        raise ValueError('This exact resource version was withdrawn or its lifecycle is invalid; do not substitute another version')
    if match["category"] not in {"style", "layout"} or match["status"] not in {"community", "reviewed", "verified", "core"}:
        raise ValueError("Unrecognized asset type or review status")
    source_url = match["source_url"]
    if urlparse(source_url).scheme in {"http", "https"}:
        folder = "styles" if match["category"] == "style" else "layouts"
        expected_url = f"https://{ALLOWED_HOST}/BatteryReviewForge/commons/{folder}/{asset_id}@{version}.json"
        if source_url != expected_url:
            raise ValueError("Pinned asset URL does not match its exact ID, version, and category")
    if not urlparse(source_url).scheme in {'http', 'https'}:
        if not Path(catalog_location).is_file():
            raise ValueError('Remote catalog cannot select a local file')
        authorized = (local_root or Path(catalog_location).resolve().parent).resolve()
        source_path = Path(source_url)
        if not source_path.is_absolute():
            source_url = str(Path(catalog_location).resolve().parent / source_path)
    else:
        authorized = None
    data = read_bytes(source_url, allow_network=allow_network, local_root=authorized)
    digest = hashlib.sha256(data).hexdigest()
    if digest != match["sha256"]:
        raise ValueError("Community asset hash differs from the catalog; stop and review the source")
    payload = json.loads(data)
    if payload["id"] != asset_id or payload["version"] != version or payload["category"] != match["category"]:
        raise ValueError("Community asset identity differs from the selected pin")
    permissions = payload.get("permissions", {})
    if not isinstance(permissions, dict) or any(permissions.get(key) is not True for key in ("public_display", "registry", "automated_testing")) or not isinstance(permissions.get("model_training"), bool):
        raise ValueError("Community asset does not contain all required separate permission records")
    output.mkdir(parents=True, exist_ok=True)
    asset_file = output / f"{asset_id}@{version}.json"
    if asset_file.exists() and asset_file.read_bytes() != data:
        raise ValueError('Existing pinned asset differs; preserve it and use a new output directory')
    asset_file.write_bytes(data)
    lock = {"style_id" if payload["category"] == "style" else "layout_id": pin,
            "asset_id": asset_id, "asset_version": version, "source_url": source_url,
            "sha256": digest, "retrieved_at": datetime.now(timezone.utc).isoformat(),
            "review_status": match["status"], "asset_file": asset_file.name}
    lock_file = output / f"{asset_id}@{version}.lock.json"
    lock_file.write_text(json.dumps(lock, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"asset": str(asset_file), "lock": str(lock_file), "review_status": match["status"]}


def re_full_slug(value: str) -> bool:
    return re.fullmatch(r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*", value) is not None


def re_full_version(value: str) -> bool:
    return re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", value) is not None


def browse(catalog_location: str, *, allow_network: bool, category: str = "all", status: str = "all",
           tags: list[str] | None = None, query: str = "", series_count: int | None = None,
           panel_count: int | None = None, limit: int = 10, search: bool = False) -> list[dict]:
    if category not in {"all", "style", "layout"}:
        raise ValueError("category must be all, style or layout")
    if status not in {"all", "community", "reviewed", "verified", "core"}:
        raise ValueError("status must be all, community, reviewed, verified or core")
    if not 1 <= limit <= 50:
        raise ValueError("limit must be between 1 and 50")
    if len(query) > 120 or any(len(tag) > 40 for tag in (tags or [])):
        raise ValueError("search text is limited to 120 characters and tags to 40 characters")
    if series_count is not None and not 1 <= series_count <= 8:
        raise ValueError("series-count must be from 1 to 8")
    if panel_count is not None and not 2 <= panel_count <= 10:
        raise ValueError("panel-count must be from 2 to 10")
    catalog = json.loads(read_bytes(catalog_location, allow_network=allow_network))
    if not isinstance(catalog, dict) or not isinstance(catalog.get("assets"), list):
        raise ValueError("Invalid community catalog")
    needle = query.casefold().strip()
    terms = re.findall(r"[a-z0-9]+|[^\W_]+", needle, flags=re.UNICODE)
    expanded_terms = []
    for term in terms:
        expanded_terms.append(term)
        if re.fullmatch(r"[\u3400-\u9fff]+", term) and len(term) >= 3:
            expanded_terms.extend(term[index:index + 2] for index in range(len(term) - 1))
    terms = list(dict.fromkeys(expanded_terms))
    wanted_tags = {tag.casefold() for tag in (tags or [])}
    rows = []
    for item in catalog["assets"]:
        if not isinstance(item, dict):
            continue
        if item.get('lifecycle', 'active') not in {'active', 'deprecated'}:
            continue
        if category != "all" and item.get("category") != category:
            continue
        if status != "all" and item.get("status") != status:
            continue
        item_tags = {tag.casefold() for tag in item.get("tags", []) if isinstance(tag, str)}
        if wanted_tags and not wanted_tags.issubset(item_tags):
            continue
        if series_count is not None and (item.get("category") != "style" or not isinstance(item.get("recommended_series_count"), int) or item["recommended_series_count"] < series_count):
            continue
        if panel_count is not None and (item.get("category") != "layout" or item.get("panel_count") != panel_count):
            continue
        searchable = " ".join(str(item.get(key, "")) for key in ("id", "name", "author", "description", "description_zh", "tags", "search_terms")).casefold()
        title = str(item.get("name", "")).casefold()
        matched = sum(1 for term in terms if term in searchable)
        score = matched * 3 + (8 if needle and needle in title else 0)
        if needle and not matched:
            continue
        row = {key: item.get(key) for key in ("id", "version", "name", "author", "license", "category", "status", "lifecycle", "review", "description_zh", "tags", "preview_url", "sha256", "recommended_series_count", "panel_count") if key in item}
        row["pin"] = "community:" + str(item.get("id", "")) + "@" + str(item.get("version", ""))
        row["score"] = score
        rows.append(row)
    rows.sort(key=lambda row: (-row["score"] if search else 0, row.get("name", "").casefold(), row.get("id", ""), row.get("version", "")))
    return rows[:limit]


def main() -> None:
    argv = sys.argv[1:]
    if argv and argv[0].startswith("community:"):
        argv = ["resolve", *argv]
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("list", "search"):
        sub = subparsers.add_parser(command, help="Browse the versioned Battery Commons catalog")
        if command == "search":
            sub.add_argument("query", help="Words to match against names, descriptions, IDs and tags")
        sub.add_argument("--catalog", default=PUBLIC_CATALOG)
        sub.add_argument("--category", choices=("all", "style", "layout"), default="all")
        sub.add_argument("--status", choices=("all", "community", "reviewed", "verified", "core"), default="all")
        sub.add_argument("--tag", action="append", default=[], help="Require a tag; may be repeated")
        sub.add_argument("--series-count", type=int, help="Style needs at least this many series colors")
        sub.add_argument("--panel-count", type=int, help="Layout must have this many panels")
        sub.add_argument("--limit", type=int, default=10)
        sub.add_argument("--allow-network", action="store_true", help="Fetch only from the official HTTPS registry")
    resolve_parser = subparsers.add_parser("resolve", help="Download one exact, hash-checked version")
    resolve_parser.add_argument("pin", help="Exact version, e.g. community:ocean-electrolyte@1.0.0")
    resolve_parser.add_argument("--catalog", default=PUBLIC_CATALOG)
    resolve_parser.add_argument("--out", type=Path, required=True)
    resolve_parser.add_argument("--allow-network", action="store_true", help="Fetch only from the official HTTPS registry")
    resolve_parser.add_argument("--local-root", type=Path, help="Explicitly authorized directory for local asset files; defaults to the catalog directory")
    args = parser.parse_args(argv)
    try:
        if args.command == "resolve":
            result = resolve(args.catalog, args.pin, args.out, allow_network=args.allow_network, local_root=args.local_root)
        else:
            query = args.query if args.command == "search" else ""
            result = browse(args.catalog, allow_network=args.allow_network, category=args.category, status=args.status,
                            tags=args.tag, query=query, series_count=args.series_count, panel_count=args.panel_count,
                            limit=args.limit, search=args.command == "search")
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (ValueError, KeyError, OSError, json.JSONDecodeError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    from cli_runtime import configure_utf8
    configure_utf8()
    main()
