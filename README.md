# HTML Deck Studio

**English:** A Codex Skill and product line for turning topics, notes, screenshots, documents, and code repositories into editable, verifiable, self-contained 16:9 HTML presentations.

**简体中文：** 一个 Codex Skill 与产品演进项目，用来把主题、资料、截图、文档或代码仓库加工成可播放、可编辑、可保存、可验证、可公开交付的 16:9 HTML 演示稿。

## Versions / 版本演进

This repository keeps both generations instead of replacing V1 with V2.

这个仓库采用迭代方式保留两个版本，而不是用 V2 覆盖 V1。

| Version | Product | Positioning | Path |
|---|---|---|---|
| V1 | HTML Deck Studio | Lightweight dual-state HTML deck editor | repository root |
| V2 | DeckForge Studio / DeckForge 演示工作室 | Three-mode deck production studio with Viewer / Quick Edit / Studio | [`v2/`](./v2/) |

V1 proves the lightweight HTML deck workflow: directly opened HTML is viewer-like, while the local preview service enables editing and saving.

V2, now named **DeckForge Studio / DeckForge 演示工作室**, keeps the V1 generation methodology and adds source/viewer delivery boundaries, Quick Edit, a local Studio workbench, parser-level viewer export, and regression tests.

## Documentation / 文档

- [English README](./README.en.md)
- [中文说明](./README.zh-CN.md)
- [V2 / DeckForge Studio](./v2/)
- [Changelog / 变更记录](./CHANGELOG.md)

## Quick Start / 快速开始

```bash
cp assets/html-ppt-template.html deck.html
./scripts/check.sh deck.html
./scripts/preview.sh deck.html
./scripts/export_viewer.py deck.html deck.viewer.html
```

Open / 打开：

```text
http://127.0.0.1:4173/deck.html
```

## What Is Included / 项目内容

- `SKILL.md`: Codex Skill workflow.
- `assets/html-ppt-template.html`: lightweight dual-state HTML presentation template. It opens as a normal viewer by default and enables editing only when served by the local preview server.
- `references/`: story, design, engineering, archetype, and QA guides.
- `scripts/`: static checker and local editable preview server.

## Requirements / 运行要求

Only Python 3 is required. The scripts use the Python standard library only.

只需要 Python 3。脚本只使用 Python 标准库。
