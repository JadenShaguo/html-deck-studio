#!/usr/bin/env python3
"""Smoke-test Viewer, Quick Edit entry injection, and Studio entry for V2."""

from __future__ import annotations

import shutil
import socket
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "assets" / "source-template.html"
SERVER = ROOT / "scripts" / "serve_studio.py"


def free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def get(url: str) -> str:
    with urllib.request.urlopen(url, timeout=5) as response:
        return response.read().decode("utf-8")


def wait_for(url: str) -> None:
    last_error: Exception | None = None
    for _ in range(40):
        try:
            get(url)
            return
        except (urllib.error.URLError, TimeoutError) as error:
            last_error = error
            time.sleep(0.1)
    raise RuntimeError(f"server did not become ready: {last_error}")


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="html-deck-studio-v2-three-modes-") as tmp:
        deck = Path(tmp) / "deck.source.html"
        shutil.copyfile(TEMPLATE, deck)
        direct = deck.read_text(encoding="utf-8")
        assert "html-deck-studio-local-runtime" not in direct
        assert "快速修改" not in direct

        port = free_port()
        proc = subprocess.Popen(
            ["python3", str(SERVER), str(deck), "--port", str(port)],
            cwd=str(ROOT),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        try:
            base = f"http://127.0.0.1:{port}"
            wait_for(base + "/__studio__/status")
            source = get(base + "/deck.source.html")
            assert "html-deck-studio-local-runtime" in source
            assert "html-deck-studio-quick-edit-loader" in source
            assert "quick-edit.js" in source
            studio_embed_source = get(base + "/deck.source.html?embed=studio")
            assert "html-deck-studio-local-runtime" not in studio_embed_source
            assert "html-deck-studio-quick-edit-loader" not in studio_embed_source
            assert "quick-edit.js" not in studio_embed_source
            quick_edit = get(base + "/__studio__/quick-edit.js")
            assert "快速修改" in quick_edit
            assert "打开工作台" in quick_edit
            workbench = get(base + "/__studio__/workbench?file=deck.source.html")
            assert "HTML Deck Studio" in workbench
            assert "deckFrame" in workbench
            assert "?embed=studio" in workbench
        finally:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=5)
    print("three-mode entry smoke test ok")


if __name__ == "__main__":
    main()
