#!/usr/bin/env python3
"""Serve the V2.0 local Studio workbench and atomically save one source deck."""

from __future__ import annotations

import argparse
import json
import os
import socket
import tempfile
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

from export_viewer import export_viewer


STATUS_PATH = "/__studio__/status"
SAVE_PATH = "/__studio__/save"
EXPORT_PATH = "/__studio__/export"
WORKBENCH_PATH = "/__studio__/workbench"
QUICK_EDIT_PATH = "/__studio__/quick-edit.js"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Serve HTML Deck Studio V2.0.")
    parser.add_argument("file", type=Path, help="Source HTML deck to edit")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=4173, type=int)
    parser.add_argument("--max-mb", default=100, type=int)
    return parser.parse_args()


def build_handler(project_dir: Path, target: Path, host: str, port: int, max_body_bytes: int):
    root = target.parent
    workbench = project_dir / "studio" / "workbench.html"
    quick_edit = project_dir / "studio" / "quick-edit.js"
    allowed_origins = {
        f"http://{host}:{port}",
        f"http://127.0.0.1:{port}",
        f"http://localhost:{port}",
    }

    class StudioHandler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(root), **kwargs)

        def end_headers(self) -> None:
            self.send_header("Cache-Control", "no-store")
            super().end_headers()

        def _send_json(self, status: int, payload: dict) -> None:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _send_file(self, path: Path, content_type: str) -> None:
            body = path.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _send_source(self, *, include_quick_edit: bool) -> None:
            html = target.read_text(encoding="utf-8")
            if include_quick_edit:
                runtime = (
                    "\n<script id=\"html-deck-studio-local-runtime\">"
                    "window.__HTML_DECK_STUDIO_LOCAL__="
                    + json.dumps(
                        {
                            "file": target.name,
                            "savePath": SAVE_PATH,
                            "workbenchPath": WORKBENCH_PATH,
                            "quickEditPath": QUICK_EDIT_PATH,
                        },
                        ensure_ascii=False,
                    )
                    + ";</script>\n"
                    f"<script id=\"html-deck-studio-quick-edit-loader\" src=\"{QUICK_EDIT_PATH}\"></script>\n"
                )
                if "</body>" in html:
                    html = html.replace("</body>", runtime + "</body>", 1)
                else:
                    html += runtime
            body = html.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self) -> None:
            parsed = urlparse(self.path)
            path = unquote(parsed.path)
            query = parse_qs(parsed.query)
            if path == STATUS_PATH:
                self._send_json(
                    200,
                    {
                        "ok": True,
                        "file": str(target),
                        "fileName": target.name,
                        "maxBytes": max_body_bytes,
                        "modes": ["viewer", "quick-edit", "studio"],
                        "exportPath": str(default_viewer_path(target)),
                    },
                )
                return
            if path == WORKBENCH_PATH:
                self._send_file(workbench, "text/html; charset=utf-8")
                return
            if path == QUICK_EDIT_PATH:
                self._send_file(quick_edit, "application/javascript; charset=utf-8")
                return
            if path == "/":
                self.send_response(302)
                self.send_header("Location", f"/{target.name}")
                self.end_headers()
                return
            if path == f"/{target.name}":
                self._send_source(include_quick_edit=query.get("embed") != ["studio"])
                return
            super().do_GET()

        def do_POST(self) -> None:
            if urlparse(self.path).path != SAVE_PATH:
                if urlparse(self.path).path == EXPORT_PATH:
                    self._handle_export()
                    return
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
                    or "data-layer-id" not in html
                    or "__studio__" in html
                ):
                    raise ValueError("payload is not a clean V2.0 source deck")
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
            self._send_json(200, {"ok": True, "path": str(target), "bytes": len(html.encode("utf-8"))})

        def _handle_export(self) -> None:
            origin = self.headers.get("Origin", "")
            if origin not in allowed_origins:
                self._send_json(403, {"ok": False, "error": "origin not allowed"})
                return
            try:
                output = default_viewer_path(target)
                export_viewer(target, output)
            except Exception as error:
                self._send_json(400, {"ok": False, "error": str(error)})
                return
            self._send_json(200, {"ok": True, "path": str(output), "file": output.name})

    return StudioHandler


def default_viewer_path(source: Path) -> Path:
    name = source.name
    if name.endswith(".source.html"):
        return source.with_name(name[: -len(".source.html")] + ".html")
    if name.endswith(".source.htm"):
        return source.with_name(name[: -len(".source.htm")] + ".htm")
    return source.with_name(source.stem + ".viewer" + source.suffix)


def main() -> None:
    args = parse_args()
    project_dir = Path(__file__).resolve().parents[1]
    target = args.file.expanduser().resolve()
    if not target.is_file():
        raise SystemExit(f"HTML file does not exist: {target}")
    if target.suffix.lower() not in {".html", ".htm"}:
        raise SystemExit(f"Target is not HTML: {target}")
    if not (1 <= args.port <= 65535):
        raise SystemExit(f"Invalid port: {args.port}")

    handler = build_handler(project_dir, target, args.host, args.port, args.max_mb * 1024 * 1024)
    try:
        server = ThreadingHTTPServer((args.host, args.port), handler)
    except OSError as error:
        if isinstance(error, OSError) and error.errno in {48, 98}:
            raise SystemExit(f"Port {args.port} is already in use. Try: ./scripts/preview.sh {target} {args.port + 1}") from error
        if isinstance(error, socket.error):
            raise SystemExit(f"Could not start local Studio server: {error}") from error
        raise
    print(f"Source preview: http://{args.host}:{args.port}/{target.name}", flush=True)
    print(f"Studio workbench: http://{args.host}:{args.port}{WORKBENCH_PATH}?file={target.name}", flush=True)
    print(f"Source file: {target}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
