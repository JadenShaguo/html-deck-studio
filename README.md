# HTML Deck Studio

**English:** A Codex Skill for turning topics, notes, screenshots, documents, and code repositories into editable, verifiable, self-contained 16:9 HTML presentations.

**简体中文：** 一个 Codex Skill 项目，用来把主题、资料、截图、文档或代码仓库加工成可播放、可编辑、可保存、可验证的 16:9 单文件 HTML PPT。

## Documentation / 文档

- [English README](./README.en.md)
- [中文说明](./README.zh-CN.md)
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
