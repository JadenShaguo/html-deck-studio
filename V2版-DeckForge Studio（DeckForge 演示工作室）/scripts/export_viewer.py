#!/usr/bin/env python3
"""Export a V2 source deck into a public viewer-only HTML deck."""

from __future__ import annotations

import argparse
import html
from html.parser import HTMLParser
from pathlib import Path


EDIT_ATTR_PREFIXES = ("data-studio-", "data-qe-")
EDIT_ATTRS = {
    "data-editable",
    "data-layer-id",
    "data-layer-name",
    "data-edit-locked",
    "contenteditable",
    "spellcheck",
}
DROP_IDS = {
    "html-deck-studio-local-actions",
    "html-deck-studio-edit-toolbar",
    "html-deck-studio-quick-edit-style",
    "html-deck-studio-local-runtime",
    "html-deck-studio-quick-edit-loader",
    "html-deck-studio-workbench-style",
    "editToggle",
    "editToolbar",
    "saveCurrentHtml",
    "downloadCurrentHtml",
    "layerPanel",
    "layerTree",
    "inspectorPanel",
}
DROP_SCRIPT_MARKERS = (
    "__HTML_DECK_STUDIO_LOCAL__",
    "__studio__",
    "quick-edit.js",
    "saveCurrentHtml",
    "downloadCurrentHtml",
)
FORBIDDEN_VIEWER_TOKENS = (
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
    "quick-edit.js",
    "saveCurrentHtml",
    "downloadCurrentHtml",
)
VOID_TAGS = {
    "area",
    "base",
    "br",
    "col",
    "embed",
    "hr",
    "img",
    "input",
    "link",
    "meta",
    "param",
    "source",
    "track",
    "wbr",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export source deck to viewer-only HTML.")
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    return parser.parse_args()


def should_drop_attr(name: str) -> bool:
    lowered = name.lower()
    return lowered in EDIT_ATTRS or any(lowered.startswith(prefix) for prefix in EDIT_ATTR_PREFIXES)


def clean_class(value: str) -> str:
    tokens = [
        item
        for item in value.split()
        if item
        and item
        not in {
            "html-deck-studio-quick-editing",
            "local-edit-available",
            "editing",
            "is-editing",
            "selected",
            "studio-selected",
        }
    ]
    return " ".join(tokens)


def serialize_attrs(attrs: list[tuple[str, str | None]]) -> str:
    rendered: list[str] = []
    for name, value in attrs:
        if should_drop_attr(name):
            continue
        if name.lower() == "class" and value is not None:
            value = clean_class(value)
            if not value:
                continue
        if name.lower() == "style" and value is not None and not value.strip():
            continue
        if value is None:
            rendered.append(name)
        else:
            rendered.append(f'{name}="{html.escape(value, quote=True)}"')
    return (" " + " ".join(rendered)) if rendered else ""


def attrs_to_map(attrs: list[tuple[str, str | None]]) -> dict[str, str]:
    return {name.lower(): value or "" for name, value in attrs}


class ViewerSanitizer(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=False)
        self.out: list[str] = []
        self.drop_stack: list[str] = []
        self.raw_stack: list[str] = []

    def dropping(self) -> bool:
        return bool(self.drop_stack)

    def should_drop_element(self, tag: str, attrs: list[tuple[str, str | None]]) -> bool:
        values = attrs_to_map(attrs)
        node_id = values.get("id", "")
        if node_id in DROP_IDS:
            return True
        if tag.lower() == "script":
            src = values.get("src", "")
            if any(marker in src for marker in DROP_SCRIPT_MARKERS):
                return True
            inline = values.get("id", "")
            if inline in DROP_IDS:
                return True
        return False

    def handle_decl(self, decl: str) -> None:
        if not self.dropping():
            self.out.append(f"<!{decl}>")

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        lowered = tag.lower()
        if self.dropping():
            self.drop_stack.append(lowered)
            return
        if self.should_drop_element(lowered, attrs):
            self.drop_stack.append(lowered)
            return
        if lowered in {"script", "style"}:
            self.raw_stack.append(lowered)
        self.out.append(f"<{tag}{serialize_attrs(attrs)}>")

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        lowered = tag.lower()
        if self.dropping() or self.should_drop_element(lowered, attrs):
            return
        self.out.append(f"<{tag}{serialize_attrs(attrs)} />")

    def handle_endtag(self, tag: str) -> None:
        lowered = tag.lower()
        if self.dropping():
            if self.drop_stack and self.drop_stack[-1] == lowered:
                self.drop_stack.pop()
            return
        if self.raw_stack and self.raw_stack[-1] == lowered:
            self.raw_stack.pop()
        if lowered not in VOID_TAGS:
            self.out.append(f"</{tag}>")

    def handle_data(self, data: str) -> None:
        if self.dropping():
            return
        if self.raw_stack:
            self.out.append(data)
        else:
            self.out.append(html.escape(data, quote=False))

    def handle_entityref(self, name: str) -> None:
        if not self.dropping():
            self.out.append(f"&{name};")

    def handle_charref(self, name: str) -> None:
        if not self.dropping():
            self.out.append(f"&#{name};")

    def handle_comment(self, data: str) -> None:
        if not self.dropping():
            self.out.append(f"<!--{data}-->")

    def result(self) -> str:
        return "".join(self.out)


def export_viewer(source: Path, output: Path) -> None:
    html_text = source.read_text(encoding="utf-8")
    if "data-editable" not in html_text or "data-layer-id" not in html_text:
        raise SystemExit("Source deck must contain data-editable and data-layer-id metadata.")

    sanitizer = ViewerSanitizer()
    sanitizer.feed(html_text)
    viewer = sanitizer.result()

    for marker in DROP_SCRIPT_MARKERS:
        if marker in viewer:
            raise SystemExit(f"Viewer export still contains local runtime marker: {marker}")
    for token in FORBIDDEN_VIEWER_TOKENS:
        if token in viewer:
            raise SystemExit(f"Viewer export still contains forbidden token: {token}")

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(viewer, encoding="utf-8")


def main() -> None:
    args = parse_args()
    source = args.source.expanduser().resolve()
    output = args.output.expanduser().resolve()
    if not source.is_file():
        raise SystemExit(f"Source HTML does not exist: {source}")
    export_viewer(source, output)
    print(f"Exported viewer HTML: {output}")


if __name__ == "__main__":
    main()
