# HTML Deck Studio

HTML Deck Studio is a Codex Skill for turning topics, notes, screenshots, documents, and code repositories into editable, verifiable, self-contained 16:9 HTML presentations.

## Highlights

- Self-contained HTML output: no CDN, remote fonts, external images, or build step.
- Editable in the browser: text editing, draggable layout units, resize handles, keyboard navigation, speaker notes, and fullscreen mode.
- Local save workflow: run a tiny Python server and save edits back to the source HTML atomically.
- Static QA checks: verify structure, required controls, external assets, SVG `viewBox`, placeholders, and presentation metadata.
- Presentation-first workflow: narrative, visual system, implementation, and verification are documented separately.

## What This Is

This repository is not a PowerPoint plugin, a SaaS product, or a Node.js application. It is a portable presentation-production kit for Codex:

- a `SKILL.md` workflow,
- a self-contained editable HTML template,
- reference guides for story, design, engineering, and QA,
- zero-dependency Python scripts for checking and local editing.

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
└── scripts/
    ├── check.sh
    ├── check_presentation.py
    ├── preview.sh
    └── serve_editable_ppt.py
```

## Requirements

Only Python 3 is required. The scripts use the Python standard library only.

```bash
python3 --version
```

## Quick Start

Create a new deck from the template:

```bash
cp assets/html-ppt-template.html deck.html
```

Run static checks:

```bash
./scripts/check.sh deck.html
```

Start local preview and editable save service:

```bash
./scripts/preview.sh deck.html
```

Open:

```text
http://127.0.0.1:4173/deck.html
```

Use another port if needed:

```bash
./scripts/preview.sh deck.html 4180
```

## Workflow

1. Define the topic, audience, occasion, duration, and one-sentence thesis.
2. Build the story with `references/story-and-content.md`.
3. Design on a fixed `1600 x 900` canvas with `references/design-system.md`.
4. Start from `assets/html-ppt-template.html`; keep navigation, notes, editing, and save behavior.
5. Run `scripts/check_presentation.py` or `./scripts/check.sh`.
6. When browser automation is available, verify layout and interactions with screenshots.

## Output Standard

- The final deck is a single self-contained HTML file.
- Every slide has `data-title` and `data-note`.
- Navigation, timeline, fullscreen, speaker notes, and edit mode remain available.
- The local save service can write browser edits back to the source HTML.
- Static checks pass before delivery.

## Optional Integrations

HTML Deck Studio does not require any private runtime service, company-specific platform, or private API. Optional integrations such as document connectors or static-site deployment tools can be used when your local Codex environment provides them.
