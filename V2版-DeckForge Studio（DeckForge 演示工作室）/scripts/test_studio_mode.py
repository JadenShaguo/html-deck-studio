#!/usr/bin/env python3
"""Test Studio service save and export endpoints."""

from __future__ import annotations

import json
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
CHECK = ROOT / "scripts" / "check.sh"


def free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def get(url: str) -> str:
    with urllib.request.urlopen(url, timeout=5) as response:
        return response.read().decode("utf-8")


def post(url: str, origin: str) -> dict:
    request = urllib.request.Request(
        url,
        data=b"{}",
        headers={"Content-Type": "application/json", "Origin": origin},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=5) as response:
        return json.loads(response.read().decode("utf-8"))


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
    with tempfile.TemporaryDirectory(prefix="html-deck-studio-v2-studio-") as tmp:
        deck = Path(tmp) / "deck.source.html"
        viewer = Path(tmp) / "deck.html"
        shutil.copyfile(TEMPLATE, deck)
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
            workbench = get(base + "/__studio__/workbench?file=deck.source.html&page=2")
            assert "exportButton" in workbench
            result = post(base + "/__studio__/export", base)
            assert result["ok"] is True
            assert viewer.exists()
            subprocess.run([str(CHECK), str(viewer), "viewer"], cwd=str(ROOT), check=True)
            exported = viewer.read_text(encoding="utf-8")
            assert "data-editable" not in exported
            assert "__studio__" not in exported
        finally:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=5)
    print("studio mode export endpoint ok")


if __name__ == "__main__":
    main()
