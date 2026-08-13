#!/usr/bin/env python3
"""Regression tests for parser-level viewer export sanitization."""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "assets" / "source-template.html"
EXPORT = ROOT / "scripts" / "export_viewer.py"
CHECK = ROOT / "scripts" / "check.sh"

FORBIDDEN = [
    "data-editable",
    "data-layer-id",
    "data-layer-name",
    "data-edit-locked",
    "data-studio-",
    "data-qe-",
    "__studio__",
    "__HTML_DECK_STUDIO_LOCAL__",
    "quick-edit.js",
    "contenteditable",
    "spellcheck",
    "saveCurrentHtml",
    "downloadCurrentHtml",
    "快速修改",
    "打开工作台",
]


def run(command: list[str]) -> None:
    subprocess.run(command, cwd=str(ROOT), check=True)


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="html-deck-studio-v2-export-") as tmp:
        source = Path(tmp) / "dirty.source.html"
        viewer = Path(tmp) / "deck.html"
        shutil.copyfile(TEMPLATE, source)
        text = source.read_text(encoding="utf-8")
        text = text.replace(
            "</body>",
            """
<div id="html-deck-studio-local-actions" data-qe-selected="true">快速修改 打开工作台</div>
<div id="html-deck-studio-edit-toolbar"><button id="saveCurrentHtml">save</button><button id="downloadCurrentHtml">download</button></div>
<script id="html-deck-studio-local-runtime">window.__HTML_DECK_STUDIO_LOCAL__={workbenchPath:"/__studio__/workbench"}</script>
<script id="html-deck-studio-quick-edit-loader" src="/__studio__/quick-edit.js"></script>
</body>
""",
        )
        text = text.replace('data-layer-id="p2-title"', 'data-layer-id="p2-title" contenteditable="true" spellcheck="false" data-qe-selected="true"', 1)
        source.write_text(text, encoding="utf-8")

        run(["python3", str(EXPORT), str(source), str(viewer)])
        run([str(CHECK), str(viewer), "viewer"])
        exported = viewer.read_text(encoding="utf-8")
        leaked = [token for token in FORBIDDEN if token in exported]
        if leaked:
            raise SystemExit("viewer leaked forbidden tokens: " + ", ".join(leaked))
    print("viewer export sanitization ok")


if __name__ == "__main__":
    main()
