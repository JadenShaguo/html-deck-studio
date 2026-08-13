#!/usr/bin/env python3
"""Ensure SKILL.md keeps both V1 generation workflow and V2 mode boundaries."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "SKILL.md"

REQUIRED_PHRASES = [
    "Viewer Mode",
    "Quick Edit Mode",
    "Studio Mode",
    "先做叙事，再做页面",
    "建立事实底座",
    "设计页面系统",
    "实现 source HTML",
    "逐轮修改时保护结构",
    "Viewer 导出",
    "分级验收",
    "data-editable",
    "data-layer-id",
    "export_viewer.py",
]


def main() -> None:
    text = SKILL.read_text(encoding="utf-8")
    missing = [phrase for phrase in REQUIRED_PHRASES if phrase not in text]
    if missing:
        raise SystemExit("SKILL.md missing required workflow phrases: " + ", ".join(missing))
    print("skill workflow structure ok")


if __name__ == "__main__":
    main()
