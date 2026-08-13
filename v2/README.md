**English** | [中文](README.zh-CN.md)

# DeckForge Studio

DeckForge Studio is the productized V2 evolution of HTML Deck Studio. It keeps the V1 backbone of verifying facts, building the narrative, implementing HTML, and validating delivery, while upgrading the editing model into a **Viewer / Quick Edit / Studio** three-mode architecture.

**Slogan:** Story first. Edit locally. Ship viewer-only.

**Principle:** Treat “making slides” as a complete production line: verify the facts and thesis first, generate a structured HTML deck, edit locally through either Quick Edit or Studio, and publish only a non-editable viewer HTML.

## Product Evolution

DeckForge Studio is not a separate restart. It is the second-generation product evolved from HTML Deck Studio. V1 proved that HTML decks could be lightweight, editable, and locally savable. V2 focuses on the harder problems: reliable layer selection, clear editing boundaries, and safe public delivery.

| Version | Product Name | Core Positioning | Best For |
|---|---|---|---|
| V1 | HTML Deck Studio | Lightweight dual-state HTML deck tool | Generate, present, locally edit, and save HTML decks |
| V2 | DeckForge Studio | Three-mode deck production studio | Generate, quick-edit, workbench-edit, and publish viewer-only decks |

The rename reflects the product shift: V2 is no longer just an “HTML Deck” template. It now includes source/viewer delivery boundaries, Quick Edit, a local Studio workbench, layer trees, local save service, export checks, and a Codex Skill methodology.

## What You Get

DeckForge Studio gives you a clearer production and delivery workflow:

- A Codex Skill workflow from research and story design to implementation and delivery
- A source/viewer file model: `*.source.html` for local production, `*.html` for public viewing
- A three-mode product architecture: Viewer Mode, Quick Edit Mode, and Studio Mode
- A fixed 16:9 canvas: `1600 x 900` by default, scaled responsively in the browser
- Presentation controls: timeline, previous/next, keyboard navigation, fullscreen, hash routing, and speaker notes
- A local Quick Edit entry: when served through preview, the source page shows `快速修改`
- A Studio workbench: layer tree, parent/child selection, drag, X/Y/W/H editing, lock, reset, save, and viewer export
- A local save service: browser edits are atomically written back to the source HTML through a Python service
- A public exporter: generates viewer-only HTML without edit entries, save endpoints, or layer metadata
- Static and regression tests for source/viewer boundaries, three-mode entries, save flows, and viewer leakage

## Quick Start

Create a source deck from the template:

```bash
cp assets/source-template.html deck.source.html
```

Run source static checks:

```bash
./scripts/check.sh deck.source.html source
```

Start the local preview service:

```bash
./scripts/preview.sh deck.source.html
```

The service prints the source page URL, for example:

```text
http://127.0.0.1:4173/deck.source.html
```

Only when the source deck is opened through the local service will the upper-right corner show:

```text
[快速修改] [打开工作台]
```

Use another port if needed:

```bash
./scripts/preview.sh deck.source.html 4180
```

Export a public viewer-only deck:

```bash
./scripts/export_viewer.py deck.source.html deck.html
```

Check the exported viewer:

```bash
./scripts/check.sh deck.html viewer
```

## Three Modes

### Viewer Mode

Triggered by:

- Opening `deck.html`
- Deploying to GitHub Pages or another static host
- Sharing the viewer HTML with external audiences

Boundaries:

- Supports viewing, navigation, fullscreen, media playback, and speaker notes
- Does not show `快速修改`
- Does not show `打开工作台`
- Does not include save endpoints
- Does not include source download buttons
- Does not include `data-editable`, `data-layer-id`, or `data-layer-name`

### Quick Edit Mode

Triggered by:

- Running `./scripts/preview.sh deck.source.html`
- Opening the source page
- Clicking `快速修改`

Best for:

- Editing one sentence
- Slightly moving images, cards, or buttons
- Nudging positions with arrow keys
- Saving source changes without opening the full workbench

Boundaries:

- Supports direct text editing
- Supports dragging unlocked layers
- Supports arrow-key nudging, with Shift for larger steps
- Saves back to `deck.source.html`
- Does not handle complex layer trees, z-index, batch alignment, grouping, or ungrouping

### Studio Mode

Triggered by:

- Running `./scripts/preview.sh deck.source.html`
- Clicking `打开工作台` on the source page

Workbench capabilities:

- Loads the current source deck in an iframe
- Displays the current slide’s layer tree
- Selects canvas elements from the layer tree
- Supports drag, X/Y/W/H editing, lock/unlock, and reset
- Supports text editing
- Saves the source deck
- Exports the public viewer

## Common Workflows

### Create A New Deck

1. Copy `assets/source-template.html` to `deck.source.html`.
2. Use `references/story-and-content.md` to define the slide-by-slide narrative.
3. Use `references/design-system.md` to design hierarchy, type scale, color, layout, and diagrams.
4. Implement pages in the source HTML and keep stable `data-layer-id` values for important elements.
5. Run `./scripts/check.sh deck.source.html source` for static validation.
6. Start the preview service and edit locally through Quick Edit or Studio.
7. Export `deck.html` and run viewer checks.

### Make Quick Local Edits

1. Run `./scripts/preview.sh deck.source.html`.
2. Open the source page URL printed by the service.
3. Click `快速修改`.
4. Edit text directly or drag unlocked layers.
5. Click save to write changes back to the source file.

### Edit In Studio Workbench

1. Run `./scripts/preview.sh deck.source.html`.
2. Open the source page and click `打开工作台`.
3. Select layers from the layer tree or click elements on the canvas.
4. Use the Inspector to edit X / Y / W / H, lock, unlock, or reset a layer.
5. Click “Save to source” to write back to `deck.source.html`.
6. Click “Export viewer” to generate the public deck.

### Share Or Deploy

Publish only `deck.html`:

```bash
./scripts/export_viewer.py deck.source.html deck.html
./scripts/check.sh deck.html viewer
```

Do not use `deck.source.html` as the public deliverable. The source file is for local production; the viewer file is for external presentation.

## Customizing Story And Design Rules

DeckForge Studio keeps its production rules in `references/`, so Codex can read them before generating a deck:

- `references/story-and-content.md` — thesis, slide tasks, transitions, and speaker notes
- `references/design-system.md` — fixed canvas, safe areas, typography, color, cards, diagrams, and screenshots
- `references/html-engineering.md` — source/viewer, scaling, navigation, editing, saving, and export rules
- `references/qa-checklist.md` — source checks, viewer checks, interaction checks, and delivery QA
- `references/presentation-archetypes.md` — common structures for product, technical, case-study, and report-style decks

If you want to change the default style, update these reference documents first instead of patching one slide at a time.

## Default Template Capabilities

`assets/source-template.html` includes:

- Cover, content, diagram, and closing slides
- A fixed `1600 x 900` design canvas
- Slide title label and bottom timeline
- Mouse and keyboard navigation
- Fullscreen mode
- Speaker notes panel
- Stable layer metadata: `data-editable`, `data-layer-id`, and `data-layer-name`
- A layer structure readable by Quick Edit and Studio
- A viewer-export-compatible structure

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
│   └── source-template.html
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
│   ├── serve_studio.py
│   ├── test_export_viewer.py
│   ├── test_quick_edit.py
│   ├── test_skill_workflow.py
│   ├── test_studio_mode.py
│   └── test_three_modes.py
└── studio/
    ├── quick-edit.js
    └── workbench.html
```

## Installation And Use

### Use As A Normal Project

```bash
git clone https://github.com/JadenShaguo/html-deck-studio.git
cd html-deck-studio/v2
cp assets/source-template.html deck.source.html
./scripts/preview.sh deck.source.html
```

### Use As A Codex Skill

Place this project in a skill directory that Codex can read, then use it as DeckForge Studio. The current Skill metadata can still be recognized as `html-deck-studio-v2`; if you install it with a new alias, `deckforge-studio` is the recommended name. When generating a deck, Codex should read `SKILL.md` and the relevant files under `references/` before editing the source template.

## Requirements

- Python 3
- A modern browser
- Codex or another AI coding agent that can read Skill-style instructions

No Node.js, Vite, React, database, CDN, or remote runtime is required. The scripts use only the Python standard library.

## How It Works

1. Codex reads `SKILL.md` and `references/` to build a fact base and slide-by-slide narrative.
2. New decks start by copying `assets/source-template.html`, rather than rebuilding the runtime from scratch.
3. The source HTML deck uses a fixed 16:9 canvas and scales to the browser viewport.
4. When opened directly, source and viewer files do not expose local edit entries.
5. `preview.sh` starts a local Python service.
6. A normal source request is injected with the Quick Edit runtime and shows `快速修改 / 打开工作台`.
7. The Studio iframe loads source with `?embed=studio`, preventing Quick Edit controls from appearing inside the workbench canvas.
8. Quick Edit or Studio save sends cleaned HTML back to the local service.
9. The service atomically replaces the source file via a temporary file and `os.replace`.
10. `export_viewer.py` performs parser-level cleanup to generate a public viewer with no editor capability.
11. Test scripts verify three-mode entry, save cleanup, viewer export, and SKILL workflow structure.

## Public Boundary

- Directly opened or statically hosted `deck.html` does not show any edit entry.
- Local editing is enabled only while `preview.sh` is running.
- The save endpoint accepts only allowed local origins.
- `export_viewer.py` removes Quick Edit entries, Studio entries, save buttons, download buttons, layer metadata, and local runtime markers.
- This project does not try to prevent copying via browser developer tools; it defines a product boundary where shared pages do not provide editing or save capabilities.

## Quality Checks

Common checks:

```bash
./scripts/check.sh assets/source-template.html source
./scripts/test_three_modes.py
./scripts/test_skill_workflow.py
./scripts/test_quick_edit.py
./scripts/test_studio_mode.py
./scripts/test_export_viewer.py
python3 -m py_compile scripts/*.py
```

After exporting a viewer:

```bash
./scripts/export_viewer.py assets/source-template.html /tmp/deck.html
./scripts/check.sh /tmp/deck.html viewer
```

## License

Refer to the actual LICENSE file in the repository. If you plan to publish this project publicly, add an explicit open-source license.
