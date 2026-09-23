"""Serve docs locally with Clipboard API writes disabled for manual UI QA."""

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


DOCS = Path(__file__).resolve().parents[1] / "docs"


class DeniedClipboardHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/search-index.json":
            self.server.search_requests += 1
            if self.server.search_requests == 1:
                self.send_error(503, "Intentional search failure for UI QA")
                return
        super().do_GET()

    def end_headers(self):
        self.send_header("Permissions-Policy", "clipboard-write=()")
        super().end_headers()


if __name__ == "__main__":
    handler = partial(DeniedClipboardHandler, directory=str(DOCS))
    server = ThreadingHTTPServer(("127.0.0.1", 8766), handler)
    server.search_requests = 0
    server.serve_forever()
