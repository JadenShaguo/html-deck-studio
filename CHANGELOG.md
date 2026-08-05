# Changelog / 变更记录

## 0.3.1 - 2026-08-05

- Simplified the root `README.md` into a lightweight bilingual entry page.
  将根 `README.md` 精简为轻量双语入口页。
- Removed redundant manual table-of-contents blocks from short reference documents.
  删除短参考文档中重复维护的手写目录。
- Added `.gitignore` for Python caches, macOS metadata, local decks, and temporary files.
  新增 `.gitignore`，忽略 Python 缓存、macOS 元数据、本地演示稿和临时文件。

## 0.3.0 - 2026-08-05

- Added bilingual GitHub-facing documentation in `README.md`, plus `README.en.md` and `README.zh-CN.md`.
  新增面向 GitHub 的双语文档，并补充英文版与中文版入口。
- Reworded environment-specific references as generic document connectors and static-site deployment tools.
  将环境特定表达调整为通用在线文档连接器和静态站点部署工具。
- Added public notes that the project has no private runtime, platform, or API dependency.
  补充公开说明：项目不依赖私有运行时、专用平台或私有 API。

## 0.2.0 - 2026-08-05

- Renamed the Skill from `build-html-presentation` to `html-deck-studio`.
  将 Skill 从 `build-html-presentation` 更名为 `html-deck-studio`。
- Added initial README, `scripts/check.sh`, and `scripts/preview.sh`.
  新增初版 README、静态检查快捷入口和本地预览快捷入口。
- Enhanced static checks for placeholders, TODO markers, cover/closing slide structure, and long slide titles.
  增强静态检查：提示占位符、待办标记、封面/致谢页结构和过长页面标题。
