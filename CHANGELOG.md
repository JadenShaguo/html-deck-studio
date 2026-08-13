# Changelog / 变更记录

## 0.4.1 - 2026-08-13

- Added lightweight dual-state editing: directly opened HTML stays in viewer mode, while the local preview server injects the edit runtime flag.
  新增轻量双态编辑：直接打开 HTML 保持播放态，本地预览服务运行时注入编辑运行态标记。
- Replaced the keyboard edit shortcut with a local-only "修改" button in the upper-right controls.
  将键盘编辑入口改为仅本地运行态显示的右上角“修改”按钮。
- Prevented the injected local edit flag from being written back into saved source HTML.
  保存源码时清理本地运行态标记，避免污染分享用 HTML。
- Added viewer-only export and dual-state end-to-end test scripts.
  新增公开纯播放版导出脚本和双态编辑端到端测试脚本。

## 0.4.0 - 2026-08-12

- Added editor v2 with explicit layer metadata, layer tree selection, a lightweight inspector, lock/reset controls, save-service status, and HTML download fallback.
  新增编辑系统 v2：显式图层元数据、图层树选择、轻量属性面板、锁定/重置控制、保存服务状态与 HTML 下载兜底。
- Added a local save-service status endpoint for detecting whether source-file save is available.
  新增本地保存服务状态接口，用于判断当前环境是否可写回源码文件。
- Extended static validation with layer-id, editable-type, v2 editor UI, and legacy edit-unit checks.
  扩展静态检查，覆盖图层 ID、可编辑类型、v2 编辑器 UI 与旧 edit-unit 兼容提示。

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
