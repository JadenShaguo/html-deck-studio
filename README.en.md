**English** | [中文](README.zh-CN.md)

# HTML Deck Studio

HTML Deck Studio is a Codex Skill and lightweight HTML presentation-production kit. It turns topics, notes, screenshots, documents, and code repositories into structured, readable, editable, savable, verifiable, and publishable 16:9 single-file HTML decks.

**Slogan:** Story first. Ship as HTML.

**Principle:** Treat “making slides” as a complete production line: verify the facts, build the narrative, design the page system, implement a self-contained HTML deck, then close the loop with local editing, static QA, and viewer-only export.

## Product Evolution

This repository keeps both generations instead of replacing V1 with V2.

| Version | Product Name | Core Positioning | Path |
|---|---|---|---|
| V1 | HTML Deck Studio | Lightweight dual-state HTML deck editor | repository root |
| V2 | DeckForge Studio | Three-mode deck production studio with Viewer / Quick Edit / Studio | [`v2/`](./v2/) |

V1 proves the lightweight HTML deck workflow: directly opened HTML is viewer-like, while the local preview service enables editing and saving.

V2, now named **DeckForge Studio / DeckForge 演示工作室**, keeps the V1 generation methodology and adds source/viewer delivery boundaries, Quick Edit, a local Studio workbench, parser-level viewer export, and regression tests.

## What You Get

HTML Deck Studio gives you a compact but end-to-end deck workflow:

- A Codex Skill workflow from research and story design to implementation and delivery
- A self-contained HTML template with CSS, JS, SVG, and runtime logic in one file
- A fixed 16:9 canvas: `1600 x 900` by default, scaled responsively in the browser
- Presentation controls: timeline, previous/next, keyboard navigation, fullscreen, hash routing, and speaker notes
- Lightweight dual-state editing: directly opened HTML is viewer-only; the local preview server enables the edit entry
- Layer-level editing: layer tree, parent/child selection, drag, resize, lock/unlock, and reset
- Local save: browser edits are atomically written back to the source HTML through a tiny Python service
- Public publishing: export a viewer-only HTML file with no editor capability
- Static QA: checks for structure, controls, assets, SVG `viewBox`, placeholders, and dual-state behavior

## Quick Start

Create a new deck from the template:

```bash
cp assets/html-ppt-template.html deck.html
```

Run static checks:

```bash
./scripts/check.sh deck.html
```

Start the local preview and save service:

```bash
./scripts/preview.sh deck.html
```

Open in your browser:

```text
http://127.0.0.1:4173/deck.html
```

The **Modify** button appears only when the deck is opened through the local service. If you open the same HTML file directly, it behaves like a normal viewer and does not expose the edit entry.

Use another port if needed:

```bash
./scripts/preview.sh deck.html 4180
```

Export a public viewer-only deck:

```bash
./scripts/export_viewer.py deck.html deck.viewer.html
```

Run the dual-state editing end-to-end test:

```bash
./scripts/test_dual_state.py
```

## Common Workflows

### Create A New Deck

1. Copy `assets/html-ppt-template.html` to your target HTML file.
2. Use `references/story-and-content.md` to define the slide-by-slide narrative.
3. Use `references/design-system.md` to design hierarchy, type scale, color, layout, diagrams, and screenshots.
4. Implement the pages in HTML and keep stable `data-layer-id` values for important elements.
5. Run `./scripts/check.sh deck.html` before delivery.

### Edit An Existing HTML Deck Locally

1. Run `./scripts/preview.sh deck.html`.
2. Click **Modify** in the upper-right corner.
3. Select a layer from the right-side layer tree or click an element on the slide.
4. Drag the selection box to move the element, or use resize handles to adjust its size.
5. Use the Inspector to edit X / Y / W / H, lock, unlock, or reset a layer.
6. Click “Save to source” to write the current browser state back to the HTML file.

### Share Or Deploy

There are two paths:

- Lightweight sharing: share `deck.html` directly. Without the local service flag, it will not show the edit entry.
- Cleaner public release: run `./scripts/export_viewer.py deck.html deck.viewer.html` to generate a viewer-only file without editor UI, save endpoints, or layer metadata.

For public publishing, the second path is recommended.

## Customizing Story And Design Rules

HTML Deck Studio keeps its production rules in `references/`, so Codex can read them before generating a deck:

- `references/story-and-content.md` — thesis, slide tasks, transitions, and speaker notes
- `references/design-system.md` — fixed canvas, safe areas, typography, color, cards, diagrams, and screenshots
- `references/html-engineering.md` — self-contained HTML, scaling, navigation, editing, saving, and export rules
- `references/qa-checklist.md` — static checks, browser checks, interaction checks, and delivery QA
- `references/presentation-archetypes.md` — common structures for product, technical, case-study, and report-style decks

If you want to change the default style, update these reference documents first instead of patching one slide at a time.

## Default Template Capabilities

`assets/html-ppt-template.html` includes:

- Cover, content, diagram, and closing slides
- A fixed `1600 x 900` design canvas
- Slide title label and bottom timeline
- Mouse and keyboard navigation
- Fullscreen mode
- Speaker notes panel
- Lightweight dual-state edit entry
- Layer tree and Inspector panel
- Local save-service status detection
- Viewer-only export-compatible structure

The template intentionally contains placeholders for future decks, so placeholder warnings from the static checker are expected when checking the template itself.

## Repository Structure

```text
.
├── README.md
├── README.en.md
├── README.zh-CN.md
├── CHANGELOG.md
├── SKILL.md
├── agents/
│   └── openai.yaml
├── assets/
│   └── html-ppt-template.html
├── references/
│   ├── design-system.md
│   ├── html-engineering.md
│   ├── presentation-archetypes.md
│   ├── qa-checklist.md
│   └── story-and-content.md
├── scripts/
│   ├── check.sh
│   ├── check_presentation.py
│   ├── export_viewer.py
│   ├── preview.sh
│   ├── serve_editable_ppt.py
│   └── test_dual_state.py
└── v2/
    └── DeckForge Studio
```

## Installation And Use

### Use As A Normal Project

```bash
git clone https://github.com/JadenShaguo/html-deck-studio.git
cd html-deck-studio
cp assets/html-ppt-template.html deck.html
./scripts/preview.sh deck.html
```

### Use As A Codex Skill

Place this project in a skill directory that Codex can read, then invoke `html-deck-studio` in your task. When generating a deck, Codex should read `SKILL.md` and the relevant files under `references/` before editing the HTML template.

## Requirements

- Python 3
- A modern browser
- Codex or another AI coding agent that can read Skill-style instructions

No Node.js, Vite, React, database, CDN, or remote runtime is required. The scripts use only the Python standard library.

## How It Works

1. Codex reads `SKILL.md` and `references/` to build a fact base and slide-by-slide narrative.
2. New decks start by copying `assets/html-ppt-template.html`, rather than rebuilding the runtime from scratch.
3. The HTML deck uses a fixed 16:9 canvas and scales to the browser viewport.
4. When opened directly, the deck stays in viewer mode and does not expose the edit entry.
5. `preview.sh` starts a local Python service that injects `window.__HTML_DECK_STUDIO_LOCAL__=true` at request time.
6. The page detects the local runtime flag and then shows the **Modify** button, layer tree, Inspector, and save workflow.
7. “Save to source” sends the current HTML to the local service, which atomically replaces the source file via a temporary file and `os.replace`.
8. `export_viewer.py` generates a public viewer-only HTML file with no editor capability.
9. `test_dual_state.py` verifies local runtime injection, save cleanup, and viewer-only export.

## Public Boundary

- Directly opened or statically hosted `deck.html` does not show the edit entry.
- Local editing is enabled only while `preview.sh` is running.
- The save endpoint accepts only allowed local origins.
- `export_viewer.py` removes editor UI, save/download buttons, layer metadata, local runtime markers, and edit-cache logic.
- This project does not try to prevent copying via browser developer tools; it defines a product boundary where shared pages do not provide editing or save capabilities.

## Quality Checks

Common checks:

```bash
./scripts/check.sh assets/html-ppt-template.html
./scripts/test_dual_state.py
python3 -m py_compile scripts/*.py
```

After exporting a viewer:

```bash
./scripts/export_viewer.py deck.html deck.viewer.html
./scripts/check.sh deck.viewer.html
```

## License

Refer to the actual LICENSE file in the repository. If you plan to publish this project publicly, add an explicit open-source license.
