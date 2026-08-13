# Changelog

## 2.1.0 - 2026-08-13

- Reframed V2 around Viewer / Quick Edit / Studio three-mode architecture.
- Added runtime-injected local Quick Edit entry; direct file open remains viewer-like.
- Added one-service flow: source preview, Quick Edit, Studio workbench, save, and viewer export.
- Restored the V1 SKILL.md generation workflow as the V2 product backbone.
- Rewrote viewer export as parser-level sanitization and added leakage regression tests.
- Added Quick Edit save, Studio export, three-mode entry, and SKILL workflow tests.
- Added `.gitignore` and refreshed README guidance.

## 2.0.0 - 2026-08-13

- Created a standalone V2.0 project in `html-deck-studio.V2.0`.
- Split editable source decks from public viewer-only exports.
- Added local Studio workbench with layer tree, inspector, drag, text editing, lock, reset, and atomic save.
- Added `export_viewer.py` to strip editing metadata before public release.
- Added source/viewer aware static checks.
