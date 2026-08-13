[English](README.en.md) | **中文**

# DeckForge Studio / DeckForge 演示工作室

DeckForge Studio（DeckForge 演示工作室）是 HTML Deck Studio V2 的产品化升级版。它继承 V1 的“先核验事实、再建立叙事、再施工 HTML、最后验收交付”的主干方法论，并把编辑体系升级为 **Viewer / Quick Edit / Studio** 三态架构。

**Slogan：** Story first. Edit locally. Ship viewer-only.（先建立叙事，本地编辑，公开只交付播放版）

**理念：** 不把“做 PPT”当成套模板，而是当成一条完整生产线：先做事实与主线，再生成结构化 HTML Deck；本地运行时可以快速修改或进入工作台深度编辑；公开发布时只交付不可编辑的 viewer HTML。

## 迭代演进

DeckForge 演示工作室不是另起炉灶的新项目，而是从 HTML Deck Studio 演进出来的第二代产品。V1 证明了“HTML 演示稿可以轻量编辑和本地保存”，V2 则进一步解决复杂页面里的图层选择、编辑边界和公开交付安全问题。

| 版本 | 产品名 | 核心定位 | 适合场景 |
|---|---|---|---|
| V1 | HTML Deck Studio | 轻量双态 HTML Deck 工具 | 快速生成、播放、本地修改和保存 |
| V2 | DeckForge Studio / DeckForge 演示工作室 | 三态演示稿生产工作室 | 生成、快速修改、图层工作台编辑、viewer-only 公开交付 |

这次改名的原因是：V2 已经不只是“HTML Deck”模板工具，而是包含 source/viewer 交付边界、Quick Edit、本地 Studio 工作台、图层树、保存服务、导出检查和 Codex Skill 方法论的完整演示稿生产系统。

## 你会得到什么

使用 DeckForge 演示工作室，你可以得到一套更清晰的演示稿生产和交付能力：

- 一个 Codex Skill 工作流：从资料研究、叙事设计、页面实现到验收交付
- 一个 source/viewer 双文件模型：`*.source.html` 用于本地生产，`*.html` 用于公开展示
- 一个三态产品架构：Viewer Mode、Quick Edit Mode、Studio Mode
- 一个固定 16:9 画布：默认 `1600 x 900`，自动等比缩放适配浏览器窗口
- 一套播放能力：时间线、上一页/下一页、键盘翻页、全屏、哈希路由和演讲者备注
- 一个本地 Quick Edit 入口：运行 preview 服务后，source 页面右上角显示“快速修改”
- 一个 Studio 工作台：图层树、父子级选择、拖拽、X/Y/W/H、锁定、重置、保存和导出 viewer
- 一个本地保存服务：浏览器编辑后，通过 Python 服务原子写回 source HTML
- 一个公开导出器：生成不含编辑入口、保存接口和图层元数据的 viewer-only HTML
- 一套静态与回归测试：检查 source/viewer 边界、三态入口、保存链路和 viewer 泄漏

## 快速开始

复制 source 模板作为新演示稿：

```bash
cp assets/source-template.html deck.source.html
```

运行 source 静态检查：

```bash
./scripts/check.sh deck.source.html source
```

启动本地 preview 服务：

```bash
./scripts/preview.sh deck.source.html
```

服务启动后会在终端输出 source 页面地址，例如：

```text
http://127.0.0.1:4173/deck.source.html
```

只有通过本地服务打开 source 页面时，右上角才会显示：

```text
[快速修改] [打开工作台]
```

如果端口被占用，可以指定其他端口：

```bash
./scripts/preview.sh deck.source.html 4180
```

导出公开展示版：

```bash
./scripts/export_viewer.py deck.source.html deck.html
```

检查公开 viewer：

```bash
./scripts/check.sh deck.html viewer
```

## 三种状态

### Viewer Mode：公开展示态

触发条件：

- 打开 `deck.html`
- 部署到 GitHub Pages 或其他静态站点
- 把 viewer HTML 分享给外部观看者

能力边界：

- 可以浏览、翻页、全屏、播放媒体、查看演讲者备注
- 不显示“快速修改”
- 不显示“打开工作台”
- 不包含保存接口
- 不包含下载源码按钮
- 不包含 `data-editable`、`data-layer-id`、`data-layer-name`

### Quick Edit Mode：本地快速修改态

触发条件：

- 运行 `./scripts/preview.sh deck.source.html`
- 打开 source 页面
- 点击右上角“快速修改”

适用场景：

- 快速改一句文案
- 微调图片、卡片或按钮位置
- 用方向键做小幅移动
- 不进入完整工作台也能保存 source

能力边界：

- 支持文本直接编辑
- 支持拖拽非锁定图层
- 支持方向键微调，Shift 加速
- 支持保存回 `deck.source.html`
- 不承担复杂图层树、z-index、批量对齐、成组/解组

### Studio Mode：本地工作台编辑态

触发条件：

- 运行 `./scripts/preview.sh deck.source.html`
- 点击 source 页面右上角“打开工作台”

工作台能力：

- iframe 加载当前 source 页面
- 展示当前页图层树
- 支持点击图层选中画布元素
- 支持拖拽、X/Y/W/H 数值编辑、锁定/解锁和重置
- 支持文本编辑
- 支持保存 source
- 支持从工作台导出 viewer

## 常用工作流

### 新建一份演示稿

1. 复制 `assets/source-template.html` 为 `deck.source.html`。
2. 按 `references/story-and-content.md` 先整理逐页叙事。
3. 按 `references/design-system.md` 设计页面层级、字号、色彩和图形。
4. 在 source HTML 中实现页面，并为重要元素保留稳定的 `data-layer-id`。
5. 运行 `./scripts/check.sh deck.source.html source` 做静态验收。
6. 运行 preview 服务，通过 Quick Edit 或 Studio 做本地修改。
7. 导出 `deck.html`，再运行 viewer 检查。

### 本地快速修改

1. 运行 `./scripts/preview.sh deck.source.html`。
2. 打开终端输出的 source 页面地址。
3. 点击右上角“快速修改”。
4. 直接编辑文本，或拖拽非锁定图层。
5. 点击“保存”，把当前修改写回 source 文件。

### 使用 Studio 工作台编辑

1. 运行 `./scripts/preview.sh deck.source.html`。
2. 打开 source 页面后点击“打开工作台”。
3. 在图层树中选择具体图层，或点击画布元素。
4. 使用 Inspector 修改 X / Y / W / H，或锁定、解锁、重置图层。
5. 点击“保存到源码”写回 `deck.source.html`。
6. 点击“导出 viewer”生成公开展示版。

### 公开分享或部署

公开分享只发布 `deck.html`：

```bash
./scripts/export_viewer.py deck.source.html deck.html
./scripts/check.sh deck.html viewer
```

不要把 `deck.source.html` 当作公开交付物。source 文件用于本地生产，viewer 文件用于外部展示。

## 自定义叙事与设计规则

DeckForge 演示工作室的核心规则写在 `references/` 中，方便 Codex 在生成演示稿前读取：

- `references/story-and-content.md` — 如何建立主线、页面任务、转场和演讲备注
- `references/design-system.md` — 固定画布、安全区、字体、配色、卡片、图形和截图规范
- `references/html-engineering.md` — source/viewer、缩放、导航、编辑、保存和导出规则
- `references/qa-checklist.md` — source 检查、viewer 检查、交互检查和交付验收清单
- `references/presentation-archetypes.md` — 常见汇报、产品、技术和案例型演示骨架

如果你希望改变默认风格，优先修改这些参考文档，而不是只改模板里的某一页。

## 默认模板能力

`assets/source-template.html` 默认包含：

- 封面页、内容页、图示页和致谢页
- 固定 `1600 x 900` 设计画布
- 页面标题提示与底部时间线
- 鼠标点击和键盘翻页
- 全屏播放
- 演讲者备注面板
- 稳定图层元数据：`data-editable`、`data-layer-id`、`data-layer-name`
- 可被 Quick Edit 和 Studio 识别的图层结构
- 公开 viewer 导出兼容结构

模板中的占位符用于生成新演示稿时替换，因此静态检查会提示占位符 warning，这是模板文件的预期状态。

## 目录结构

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

## 安装与使用

### 作为普通项目使用

```bash
git clone https://github.com/JadenShaguo/html-deck-studio.git
cd html-deck-studio/v2
cp assets/source-template.html deck.source.html
./scripts/preview.sh deck.source.html
```

### 作为 Codex Skill 使用

把项目放到 Codex 可读取的 skill 目录后，可以作为 DeckForge Studio 使用。当前 Skill 元数据仍可通过 `html-deck-studio-v2` 识别；如果安装时改用新别名，建议使用 `deckforge-studio`。生成演示稿时，Codex 应先读取 `SKILL.md` 和 `references/` 下的参考文档，再基于 source 模板施工 HTML。

## 系统要求

- Python 3
- 一个现代浏览器
- Codex 或类似可读取 Skill 的 AI coding agent

不需要 Node.js、Vite、React、数据库、CDN 或任何远端运行时。脚本只使用 Python 标准库。

## 工作原理

1. Codex 读取 `SKILL.md` 和 `references/`，先建立事实底座和逐页叙事。
2. 新演示稿从 `assets/source-template.html` 复制开始，不从空白重建运行系统。
3. source HTML 使用固定 16:9 画布，浏览器中按可视区自动缩放。
4. 直接打开 source 或 viewer 文件时，不显示本地编辑入口。
5. `preview.sh` 启动本地 Python 服务。
6. 普通 source 请求会临时注入 Quick Edit runtime，并显示“快速修改 / 打开工作台”。
7. Studio 工作台 iframe 使用 `?embed=studio` 加载 source，避免画布里出现 Quick Edit 浮层。
8. Quick Edit 或 Studio 点击保存后，浏览器把清理后的 HTML 发送给本地服务。
9. 服务端使用临时文件 + `os.replace` 原子覆盖 source 文件。
10. `export_viewer.py` 使用 parser 级清理，从 source 生成不含编辑能力的公开 viewer。
11. 测试脚本验证三态入口、保存清理、viewer 导出和 SKILL 方法论结构。

## 公开边界

- 直接打开或部署 `deck.html` 时，不显示任何编辑入口。
- 本地编辑能力只在 `preview.sh` 运行状态下启用。
- 保存接口只接受本地服务允许的来源。
- `export_viewer.py` 会移除 Quick Edit 入口、Studio 入口、保存按钮、下载按钮、图层元数据和本地服务标记。
- 该项目不能阻止浏览器开发者工具层面的复制行为；它解决的是“分享页面不提供编辑入口和保存能力”的产品边界。

## 质量检查

常用检查命令：

```bash
./scripts/check.sh assets/source-template.html source
./scripts/test_three_modes.py
./scripts/test_skill_workflow.py
./scripts/test_quick_edit.py
./scripts/test_studio_mode.py
./scripts/test_export_viewer.py
python3 -m py_compile scripts/*.py
```

导出 viewer 后可额外检查：

```bash
./scripts/export_viewer.py assets/source-template.html /tmp/deck.html
./scripts/check.sh /tmp/deck.html viewer
```

## 许可证

请以仓库中的实际 LICENSE 文件为准；如果准备公开发布，建议补充明确的开源许可证。
