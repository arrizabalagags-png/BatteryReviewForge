"""Serve the product pages with temporary 0/1/10/50-item catalog fixtures for UI review.

Run from the repository root with:
    python tests/fixtures/community_catalog_server.py --port 8766
Then open /community.html?fixture=0, 1, 10, 50, xss, long, malformed, history, or fail.
"""
from __future__ import annotations

import argparse
import json
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs"


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DOCS), **kwargs)

    def do_GET(self):
        route = urlparse(self.path)
        if route.path.startswith("/commons/styles/") and "fixture=history" in self.headers.get("Referer", ""):
            filename = Path(route.path).name
            if filename in {"qa-version@1.0.0.json", "qa-version@2.0.0.json"}:
                base = json.loads((DOCS / "commons" / "styles" / "ocean-electrolyte@1.0.0.json").read_text(encoding="utf-8"))
                base["id"] = "qa-version"
                base["version"] = filename.split("@", 1)[1].removesuffix(".json")
                self.send_json(base)
                return
        if route.path != "/commons/catalog.json":
            return super().do_GET()
        referer = urlparse(self.headers.get("Referer", ""))
        fixture = parse_qs(referer.query).get("fixture", [""])[0]
        if fixture == "fail":
            self.send_error(503, "Intentional UI QA catalog failure")
            return
        if fixture == "malformed":
            self.send_json({"schema_version":"1.0", "assets":{"not":"a list"}})
            return
        if fixture in {"xss", "long"}:
            count = 1
        elif fixture == "history":
            count = 2
        else:
            try:
                count = int(fixture)
            except ValueError:
                return super().do_GET()
        if count not in {0, 1, 2, 10, 50}:
            self.send_error(400, "Use a 0, 1, 2, 10, 50, xss, long or history fixture")
            return
        real = json.loads((DOCS / "commons" / "catalog.json").read_text(encoding="utf-8"))
        templates = real["assets"]
        entries = []
        for index in range(count):
            entry = dict(templates[index % len(templates)])
            entry["id"] = f"qa-resource-{index + 1:02d}"
            entry["version"] = "1.0.0"
            entry["name"] = f"QA resource {index + 1:02d}"
            entry["author"] = "Local UI fixture"
            entry["description_zh"] = "临时界面检查数据，不会写入正式目录。"
            entry["updated_at"] = f"2026-09-{(index % 24) + 1:02d}"
            entry["tags"] = ["qa-fixture"]
            if fixture == "xss":
                entry["id"] = "qa-xss"
                entry["name"] = "<img src=x onerror=alert(1)>"
                entry["author"] = "<script>alert(2)</script>"
                entry["description_zh"] = "<svg onload=alert(3)>safe text</svg>"
                entry["tags"] = ["<script>", "long-check"]
                entry["preview_url"] = "https://example.invalid/untrusted.svg"
            if fixture == "long":
                entry["id"] = "qa-long"
                entry["name"] = "N" * 80
                entry["author"] = "A" * 120
                entry["description_zh"] = "D" * 400
                entry["tags"] = ["t" * 40]
            entries.append(entry)
        if fixture == "history":
            entries = []
            for version in ("1.0.0", "2.0.0"):
                entry = dict(templates[0])
                entry.update({"id":"qa-version","version":version,"name":"QA version history","author":"Local UI fixture","source_url":f"commons/styles/qa-version@{version}.json","preview_url":"commons/styles/ocean-electrolyte@1.0.0.svg"})
                entries.append(entry)
        body = (json.dumps({**real, "assets": entries}, ensure_ascii=False) + "\n").encode("utf-8")
        self.send_json(body, already_encoded=True)

    def send_json(self, data, already_encoded=False):
        body = data if already_encoded else (json.dumps(data, ensure_ascii=False) + "\n").encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8766)
    args = parser.parse_args()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"Community fixture server at http://127.0.0.1:{args.port}/community.html?fixture=2")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
