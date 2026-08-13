#!/usr/bin/env python3
"""Test the local Quick Edit save path without requiring a browser."""

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


def free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def get(url: str) -> str:
    with urllib.request.urlopen(url, timeout=5) as response:
        return response.read().decode("utf-8")


def post_json(url: str, payload: dict, origin: str) -> dict:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
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
    with tempfile.TemporaryDirectory(prefix="html-deck-studio-v2-quick-edit-") as tmp:
        deck = Path(tmp) / "deck.source.html"
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
            served = get(base + "/deck.source.html")
            assert "html-deck-studio-local-runtime" in served

            clean = deck.read_text(encoding="utf-8")
            changed = clean.replace("[填写本页唯一主标题]", "Quick Edit 保存测试", 1)
            result = post_json(base + "/__studio__/save", {"html": changed}, base)
            assert result["ok"] is True
            saved = deck.read_text(encoding="utf-8")
            assert "Quick Edit 保存测试" in saved
            assert "html-deck-studio-local-runtime" not in saved
            assert "__studio__" not in saved
            assert "quick-edit.js" not in saved
        finally:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=5)
    print("quick edit save path ok")


if __name__ == "__main__":
    main()
