#!/usr/bin/env python3
"""End-to-end checks for lightweight dual-state editing."""

from __future__ import annotations

import json
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]
TEMPLATE = PROJECT_DIR / "assets" / "html-ppt-template.html"
SERVE = PROJECT_DIR / "scripts" / "serve_editable_ppt.py"
EXPORT = PROJECT_DIR / "scripts" / "export_viewer.py"
CHECK = PROJECT_DIR / "scripts" / "check.sh"

FORBIDDEN_VIEWER_TOKENS = (
    "data-editable",
    "data-layer-id",
    "editToggle",
    "editToolbar",
    "saveCurrentHtml",
    "downloadCurrentHtml",
    "layerPanel",
    "inspectorPanel",
    "__HTML_DECK_STUDIO_LOCAL__",
    "htmlDeckStudioLocalFlag",
    "contenteditable",
    "localStorage",
    "__ppt_editor",
)


def free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def read_url(url: str) -> str:
    return urllib.request.urlopen(url, timeout=5).read().decode("utf-8")


def post_json(url: str, payload: dict, origin: str) -> dict:
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        headers={"Origin": origin, "Content-Type": "application/json"},
        method="POST",
    )
    return json.loads(urllib.request.urlopen(request, timeout=5).read().decode("utf-8"))


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="html-deck-studio-dual-state-") as tmp:
        tmp_dir = Path(tmp)
        source = tmp_dir / "deck.html"
        viewer = tmp_dir / "deck.viewer.html"
        source.write_text(TEMPLATE.read_text(encoding="utf-8"), encoding="utf-8")
        port = free_port()
        origin = f"http://127.0.0.1:{port}"
        process = subprocess.Popen(
            [sys.executable, str(SERVE), "--file", str(source), "--port", str(port)],
            cwd=str(PROJECT_DIR),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        try:
            deadline = time.time() + 5
            while time.time() < deadline:
                try:
                    status = json.loads(read_url(f"{origin}/__ppt_editor_status__"))
                    if status.get("ok"):
                        break
                except Exception:
                    time.sleep(0.1)
            else:
                output = process.stdout.read() if process.stdout else ""
                raise AssertionError("server did not become ready\n" + output)

            served = read_url(f"{origin}/{source.name}")
            assert_true(
                '<script id="htmlDeckStudioLocalFlag">' in served,
                "served HTML should include local edit runtime flag",
            )
            assert_true(
                '<script id="htmlDeckStudioLocalFlag">' not in source.read_text(encoding="utf-8"),
                "source file should not contain injected local flag",
            )
            assert_true("修改" in served and "saveCurrentHtml" in served, "served HTML should expose local edit UI")

            save_result = post_json(f"{origin}/__ppt_editor_save__", {"html": served}, origin)
            assert_true(save_result.get("ok") is True, "save endpoint should accept served HTML")
            saved = source.read_text(encoding="utf-8")
            assert_true(
                '<script id="htmlDeckStudioLocalFlag">' not in saved,
                "saved source should strip local edit runtime flag",
            )

            subprocess.run([str(CHECK), str(source)], cwd=str(PROJECT_DIR), check=True)
            subprocess.run([sys.executable, str(EXPORT), str(source), str(viewer)], cwd=str(PROJECT_DIR), check=True)
            viewer_html = viewer.read_text(encoding="utf-8")
            remaining = [token for token in FORBIDDEN_VIEWER_TOKENS if token in viewer_html]
            assert_true(not remaining, "viewer export contains editor token(s): " + ", ".join(remaining))
        finally:
            process.terminate()
            try:
                process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=3)

    print("dual-state e2e ok")


if __name__ == "__main__":
    main()
