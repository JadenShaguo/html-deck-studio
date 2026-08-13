#!/usr/bin/env python3
"""Portable static checks for a self-contained editable HTML presentation."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse


BASE_REQUIRED_IDS = {
    "deck",
    "timeline",
    "prev",
    "next",
    "fullscreen",
    "speakerNotes",
}
EDITOR_REQUIRED_IDS = {
    "editToggle",
    "editToolbar",
    "resetSlide",
    "saveCurrentHtml",
    "editSelection",
}
RECOMMENDED_V2_IDS = {
    "layerPanel",
    "layerTree",
    "layerCount",
    "inspectorPanel",
    "inspectorLayerName",
    "downloadCurrentHtml",
    "saveStatus",
}
VALID_EDITABLE_TYPES = {"text", "image", "video", "button", "card", "group", "svg"}

PLACEHOLDER_PATTERN = re.compile(r"\[[^\]\n]{0,80}[\u4e00-\u9fff][^\]\n]{0,80}\]")
TODO_PATTERN = re.compile(r"\b(TODO|TBD|FIXME)\b|待补|待定|占位", re.IGNORECASE)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check the structure and portability of an HTML PPT."
    )
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


class PresentationParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: list[str] = []
        self.slides: list[dict[str, str]] = []
        self.title_cover_slides = 0
        self.svg_total = 0
        self.svg_without_viewbox = 0
        self.external_assets: list[dict[str, str]] = []
        self.direct_raster_images: list[str] = []
        self.editable_layers: list[dict[str, str]] = []
        self.edit_units_without_layer = 0

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        values = attr_map(attrs)
        if values.get("id"):
            self.ids.append(values["id"])
        classes = class_tokens(values.get("class", ""))

        if values.get("data-editable"):
            self.editable_layers.append(values)
        if "edit-unit" in classes and not values.get("data-layer-id"):
            self.edit_units_without_layer += 1

        if tag == "section" and "slide" in classes:
            self.slides.append(values)
            if "title-cover" in classes:
                self.title_cover_slides += 1

        if tag == "svg":
            self.svg_total += 1
            if not values.get("viewbox"):
                self.svg_without_viewbox += 1

        candidates: list[tuple[str, str]] = []
        if tag in {"img", "script", "source", "video", "audio"}:
            candidates.append(("src", values.get("src", "")))
        if tag == "link":
            candidates.append(("href", values.get("href", "")))
        if tag == "image":
            candidates.append(("href", values.get("href", "")))
            candidates.append(("xlink:href", values.get("xlink:href", "")))

        for attribute, value in candidates:
            if value and is_external(value):
                self.external_assets.append(
                    {"tag": tag, "attribute": attribute, "value": value}
                )

        if tag == "img":
            source = values.get("src", "").lower()
            if source.startswith(("data:image/png", "data:image/jpeg", "data:image/jpg")):
                self.direct_raster_images.append(source[:32])


def detect_mode(path: Path, text: str, requested: str) -> str:
    if requested != "auto":
        return requested
    if "editToggle" in text or "data-editable" in text or "__HTML_DECK_STUDIO_LOCAL__" in text:
        return "source"
    return "viewer"


def run_checks(path: Path, requested_mode: str = "auto") -> dict:
    text = path.read_text(encoding="utf-8")
    parser = PresentationParser()
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
        if len(slide.get("data-title", "")) > 36:
            warnings.append(f"第 {index} 页 data-title 过长，时间线提示可能不易读。")

    if parser.slides:
        first_classes = class_tokens(parser.slides[0].get("class", ""))
        if "title-cover" not in first_classes:
            warnings.append("首页不是 title-cover 样式，请确认封面视觉是否符合规范。")
        if parser.title_cover_slides < 2:
            warnings.append("少于 2 个 title-cover 页面；通常应包含封面和致谢页。")
        slide_titles = [slide.get("data-title", "") for slide in parser.slides]
        if not any("致谢" in title or "谢谢" in title for title in slide_titles):
            warnings.append("没有识别到致谢/谢谢页标题，请确认尾页是否完整。")

    id_counts = Counter(parser.ids)
    duplicates = sorted(key for key, count in id_counts.items() if count > 1)
    if duplicates:
        errors.append("存在重复 ID：" + ", ".join(duplicates))

    required_ids = set(BASE_REQUIRED_IDS)
    if mode == "source":
        required_ids |= EDITOR_REQUIRED_IDS
    missing_ids = sorted(required_ids - set(parser.ids))
    if missing_ids:
        errors.append("缺少必要控件 ID：" + ", ".join(missing_ids))

    if mode == "source":
        missing_v2_ids = sorted(RECOMMENDED_V2_IDS - set(parser.ids))
        if missing_v2_ids:
            warnings.append("缺少编辑系统 v2 推荐控件 ID：" + ", ".join(missing_v2_ids))

    if mode == "source" and not parser.editable_layers:
        warnings.append("没有发现 data-editable 图层；编辑系统将退回粗粒度旧模式。")
    else:
        layer_ids = [
            layer.get("data-layer-id", "").strip()
            for layer in parser.editable_layers
            if layer.get("data-layer-id", "").strip()
        ]
        missing_layer_ids = sum(
            1 for layer in parser.editable_layers if not layer.get("data-layer-id", "").strip()
        )
        duplicate_layer_ids = sorted(
            key for key, count in Counter(layer_ids).items() if count > 1
        )
        invalid_types = sorted(
            set(
                layer.get("data-editable", "")
                for layer in parser.editable_layers
                if layer.get("data-editable", "") not in VALID_EDITABLE_TYPES
            )
        )
        if missing_layer_ids:
            warnings.append(f"有 {missing_layer_ids} 个 data-editable 图层缺少 data-layer-id。")
        if duplicate_layer_ids:
            errors.append("存在重复 data-layer-id：" + ", ".join(duplicate_layer_ids))
        if invalid_types:
            errors.append("存在非法 data-editable 类型：" + ", ".join(invalid_types))
    if mode == "source" and parser.edit_units_without_layer:
        warnings.append(
            f"有 {parser.edit_units_without_layer} 个 edit-unit 缺少 data-layer-id，建议升级为显式图层。"
        )

    compact_css = re.sub(r"\s+", "", text.lower())
    if "width:1600px" not in compact_css or "height:900px" not in compact_css:
        errors.append("未找到 1600×900 固定画布声明。")
    if "--deck-scale" not in text or "Math.min" not in text:
        errors.append("未找到整页等比缩放逻辑。")

    required_code = {
        "全屏逻辑": "requestFullscreen",
        "哈希导航": "location.hash",
        "演讲者备注": "speakerNotes",
    }
    if mode == "source":
        required_code.update(
            {
                "本地编辑门禁": "__HTML_DECK_STUDIO_LOCAL__",
                "本地编辑缓存": "localStorage",
                "保存端点": "/__ppt_editor_save__",
                "可编辑文本": "contenteditable",
                "编辑模式状态": "edit-mode",
            }
        )
    for label, token in required_code.items():
        if token not in text:
            errors.append(f"缺少{label}：{token}")

    if mode == "viewer":
        forbidden = sorted(
            token
            for token in (
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
            if token in text
        )
        if forbidden:
            errors.append("viewer 文件包含编辑器能力或图层元数据：" + ", ".join(forbidden))

    if parser.svg_without_viewbox:
        errors.append(f"有 {parser.svg_without_viewbox} 个 SVG 缺少 viewBox。")
    if parser.external_assets:
        examples = ", ".join(
            item["value"][:90] for item in parser.external_assets[:5]
        )
        errors.append(f"发现外部或本机资源引用：{examples}")
    if parser.direct_raster_images:
        warnings.append(
            f"发现 {len(parser.direct_raster_images)} 个直接栅格 img；建议放入 SVG 容器。"
        )

    placeholders = sorted(set(match.group(0) for match in PLACEHOLDER_PATTERN.finditer(text)))
    if placeholders:
        examples = ", ".join(placeholders[:5])
        warnings.append(f"发现 {len(placeholders)} 类未替换占位符：{examples}")

    todo_matches = sorted(set(match.group(0) for match in TODO_PATTERN.finditer(text)))
    if todo_matches:
        warnings.append("发现待办或占位提示：" + ", ".join(todo_matches[:5]))

    return {
        "ok": not errors,
        "mode": mode,
        "file": str(path),
        "slides": len(parser.slides),
        "title_cover_slides": parser.title_cover_slides,
        "svg": parser.svg_total,
        "errors": errors,
        "warnings": warnings,
    }


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
        print(
            f"[{status}] {result['file']} | "
            f"mode={result['mode']} slides={result['slides']} svg={result['svg']}"
        )
        for message in result["errors"]:
            print(f"ERROR: {message}")
        for message in result["warnings"]:
            print(f"WARN: {message}")
    raise SystemExit(0 if result["ok"] else 1)


if __name__ == "__main__":
    main()
