#!/usr/bin/env python3
"""Static checks for HTML Deck Studio V2.0 source and viewer decks."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse


VALID_EDITABLE_TYPES = {"text", "image", "video", "button", "card", "group", "svg"}
VIEWER_REQUIRED_IDS = {"deck", "timeline", "prev", "next", "fullscreen", "speakerNotes"}
SOURCE_FORBIDDEN_IDS = {"editToggle", "editToolbar", "saveCurrentHtml", "downloadCurrentHtml", "layerPanel", "layerTree", "inspectorPanel"}
VIEWER_FORBIDDEN_TOKENS = {
    "data-editable",
    "data-layer-id",
    "data-layer-name",
    "data-edit-locked",
    "data-studio-",
    "data-qe-",
    "__studio__",
    "__HTML_DECK_STUDIO_LOCAL__",
    "contenteditable",
    "spellcheck",
    "saveCurrentHtml",
    "downloadCurrentHtml",
    "quick-edit.js",
    "快速修改",
    "打开工作台",
}
PLACEHOLDER_PATTERN = re.compile(r"\[[^\]\n]{0,80}[\u4e00-\u9fff][^\]\n]{0,80}\]")
TODO_PATTERN = re.compile(r"\b(TODO|TBD|FIXME)\b|待补|待定|占位", re.IGNORECASE)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check a V2.0 HTML deck.")
    parser.add_argument("html", type=Path)
    parser.add_argument("--mode", choices=("auto", "source", "viewer"), default="auto")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def attr_map(attrs: list[tuple[str, str | None]]) -> dict[str, str]:
    return {key.lower(): value or "" for key, value in attrs}


def class_tokens(value: str) -> set[str]:
    return {item for item in value.split() if item}


def is_external(value: str) -> bool:
    lowered = value.strip().lower()
    if not lowered or lowered.startswith(("data:", "#", "about:blank")):
        return False
    if lowered.startswith(("http://", "https://", "//", "file://")):
        return True
    parsed = urlparse(lowered)
    return bool(parsed.scheme or lowered.startswith("/"))


class DeckParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: list[str] = []
        self.slides: list[dict[str, str]] = []
        self.title_cover_slides = 0
        self.svg_total = 0
        self.svg_without_viewbox = 0
        self.external_assets: list[str] = []
        self.editable_layers: list[dict[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = attr_map(attrs)
        if values.get("id"):
            self.ids.append(values["id"])
        classes = class_tokens(values.get("class", ""))
        if tag == "section" and "slide" in classes:
            self.slides.append(values)
            if "title-cover" in classes:
                self.title_cover_slides += 1
        if tag == "svg":
            self.svg_total += 1
            if not values.get("viewbox"):
                self.svg_without_viewbox += 1
        if values.get("data-editable"):
            self.editable_layers.append(values)

        candidates: list[str] = []
        if tag in {"img", "script", "source", "video", "audio"}:
            candidates.append(values.get("src", ""))
        if tag == "link":
            candidates.append(values.get("href", ""))
        if tag == "image":
            candidates.extend([values.get("href", ""), values.get("xlink:href", "")])
        for value in candidates:
            if value and is_external(value):
                self.external_assets.append(value)


def detect_mode(path: Path, text: str, requested: str) -> str:
    if requested != "auto":
        return requested
    if path.name.endswith(".source.html") or "data-editable" in text:
        return "source"
    return "viewer"


def run_checks(path: Path, requested_mode: str = "auto") -> dict:
    text = path.read_text(encoding="utf-8")
    parser = DeckParser()
    parser.feed(text)
    mode = detect_mode(path, text, requested_mode)
    errors: list[str] = []
    warnings: list[str] = []

    if not re.match(r"\s*<!doctype\s+html", text, re.IGNORECASE):
        errors.append("缺少 <!doctype html>。")
    if not parser.slides:
        errors.append("没有找到 section.slide。")
    for index, slide in enumerate(parser.slides, 1):
        if not slide.get("data-title", "").strip():
            errors.append(f"第 {index} 页缺少 data-title。")
        if not slide.get("data-note", "").strip():
            warnings.append(f"第 {index} 页缺少 data-note。")
    if parser.slides and parser.title_cover_slides < 2:
        warnings.append("少于 2 个 title-cover 页面；通常应包含封面和致谢页。")

    duplicates = sorted(key for key, count in Counter(parser.ids).items() if count > 1)
    if duplicates:
        errors.append("存在重复 ID：" + ", ".join(duplicates))
    missing_viewer_ids = sorted(VIEWER_REQUIRED_IDS - set(parser.ids))
    if missing_viewer_ids:
        errors.append("缺少 viewer 必要控件 ID：" + ", ".join(missing_viewer_ids))

    compact_css = re.sub(r"\s+", "", text.lower())
    if "width:1600px" not in compact_css or "height:900px" not in compact_css:
        errors.append("未找到 1600×900 固定画布声明。")
    for token in ("--deck-scale", "Math.min", "location.hash", "requestFullscreen", "speakerNotes"):
        if token not in text:
            errors.append(f"缺少 viewer runtime 能力：{token}")

    if mode == "source":
        forbidden_ids = sorted(SOURCE_FORBIDDEN_IDS & set(parser.ids))
        if forbidden_ids:
            errors.append("source 文件不应包含编辑器 UI ID：" + ", ".join(forbidden_ids))
        if "__studio__" in text or "downloadCurrentHtml" in text:
            errors.append("source 文件不应包含 Studio 或下载 HTML 逻辑。")
        if not parser.editable_layers:
            errors.append("source 文件缺少 data-editable 图层。")
        layer_ids = [layer.get("data-layer-id", "").strip() for layer in parser.editable_layers if layer.get("data-layer-id", "").strip()]
        missing_layer_ids = sum(1 for layer in parser.editable_layers if not layer.get("data-layer-id", "").strip())
        duplicate_layer_ids = sorted(key for key, count in Counter(layer_ids).items() if count > 1)
        invalid_types = sorted({layer.get("data-editable", "") for layer in parser.editable_layers if layer.get("data-editable", "") not in VALID_EDITABLE_TYPES})
        if missing_layer_ids:
            errors.append(f"有 {missing_layer_ids} 个 data-editable 图层缺少 data-layer-id。")
        if duplicate_layer_ids:
            errors.append("存在重复 data-layer-id：" + ", ".join(duplicate_layer_ids))
        if invalid_types:
            errors.append("存在非法 data-editable 类型：" + ", ".join(invalid_types))
    else:
        forbidden = sorted(token for token in VIEWER_FORBIDDEN_TOKENS if token in text)
        if forbidden:
            errors.append("viewer 文件包含编辑器或图层元数据：" + ", ".join(forbidden))

    if parser.svg_without_viewbox:
        errors.append(f"有 {parser.svg_without_viewbox} 个 SVG 缺少 viewBox。")
    if parser.external_assets:
        errors.append("发现外部或本机资源引用：" + ", ".join(parser.external_assets[:5]))

    placeholders = sorted(set(match.group(0) for match in PLACEHOLDER_PATTERN.finditer(text)))
    if placeholders:
        warnings.append(f"发现 {len(placeholders)} 类未替换占位符：" + ", ".join(placeholders[:5]))
    todo_matches = sorted(set(match.group(0) for match in TODO_PATTERN.finditer(text)))
    if todo_matches:
        warnings.append("发现待办或占位提示：" + ", ".join(todo_matches[:5]))

    return {"ok": not errors, "mode": mode, "file": str(path), "slides": len(parser.slides), "svg": parser.svg_total, "errors": errors, "warnings": warnings}


def main() -> None:
    args = parse_args()
    path = args.html.expanduser().resolve()
    if not path.is_file():
        raise SystemExit(f"HTML file does not exist: {path}")
    result = run_checks(path, args.mode)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        status = "PASS" if result["ok"] else "FAIL"
        print(f"[{status}] {result['file']} | mode={result['mode']} slides={result['slides']} svg={result['svg']}")
        for message in result["errors"]:
            print(f"ERROR: {message}")
        for message in result["warnings"]:
            print(f"WARN: {message}")
    raise SystemExit(0 if result["ok"] else 1)


if __name__ == "__main__":
    main()
