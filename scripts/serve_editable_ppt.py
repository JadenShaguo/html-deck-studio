#!/usr/bin/env python3
"""Serve one HTML presentation and atomically save editor changes to its source."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse


SAVE_PATH = "/__ppt_editor_save__"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Serve an editable HTML PPT and save changes back to the same file."
    )
    parser.add_argument("--file", required=True, type=Path, help="HTML file to serve")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=4173, type=int)
    parser.add_argument("--max-mb", default=100, type=int)
    return parser.parse_args()


def build_handler(target: Path, host: str, port: int, max_body_bytes: int):
    root = target.parent
    allowed_origins = {
        f"http://{host}:{port}",
        f"http://127.0.0.1:{port}",
        f"http://localhost:{port}",
    }

    class EditablePPTHandler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(root), **kwargs)

        def end_headers(self):
            self.send_header("Cache-Control", "no-store")
            super().end_headers()

        def _send_json(self, status: int, payload: dict) -> None:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            path = unquote(urlparse(self.path).path)
            if path == "/":
                self.send_response(302)
                self.send_header("Location", f"/{target.name}")
                self.end_headers()
                return
            super().do_GET()

        def do_POST(self):
            if urlparse(self.path).path != SAVE_PATH:
                self._send_json(404, {"ok": False, "error": "unknown endpoint"})
                return

            origin = self.headers.get("Origin", "")
            if origin not in allowed_origins:
                self._send_json(403, {"ok": False, "error": "origin not allowed"})
                return

            try:
                length = int(self.headers.get("Content-Length", "0"))
            except ValueError:
                length = 0
            if length <= 0 or length > max_body_bytes:
                self._send_json(413, {"ok": False, "error": "invalid payload size"})
                return

            temp_path: Path | None = None
            try:
                payload = json.loads(self.rfile.read(length).decode("utf-8"))
                html = payload.get("html", "")
                lowered = html.lower() if isinstance(html, str) else ""
                if (
                    not isinstance(html, str)
                    or "<!doctype html>" not in lowered
                    or 'id="deck"' not in html
                    or 'id="saveCurrentHtml"' not in html
                ):
                    raise ValueError("payload is not an editable HTML PPT")

                existing_mode = target.stat().st_mode
                with tempfile.NamedTemporaryFile(
                    "w",
                    encoding="utf-8",
                    dir=str(target.parent),
                    prefix=f".{target.name}.",
                    suffix=".tmp",
                    delete=False,
                ) as output:
                    temp_path = Path(output.name)
                    output.write(html)
                    output.flush()
                    os.fsync(output.fileno())
                os.chmod(temp_path, existing_mode)
                os.replace(temp_path, target)
            except Exception as error:
                if temp_path and temp_path.exists():
                    temp_path.unlink()
                self._send_json(400, {"ok": False, "error": str(error)})
                return

            self._send_json(
                200,
                {
                    "ok": True,
                    "path": str(target),
                    "bytes": len(html.encode("utf-8")),
                },
            )

    return EditablePPTHandler


def main() -> None:
    args = parse_args()
    target = args.file.expanduser().resolve()
    if not target.is_file():
        raise SystemExit(f"HTML file does not exist: {target}")
    if target.suffix.lower() not in {".html", ".htm"}:
        raise SystemExit(f"Target is not HTML: {target}")
    if not (1 <= args.port <= 65535):
        raise SystemExit(f"Invalid port: {args.port}")

    handler = build_handler(
        target=target,
        host=args.host,
        port=args.port,
        max_body_bytes=args.max_mb * 1024 * 1024,
    )
    server = ThreadingHTTPServer((args.host, args.port), handler)
    print(f"Serving {target} at http://{args.host}:{args.port}/{target.name}", flush=True)
    print(f"Saving edits atomically to {target}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
