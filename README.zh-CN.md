[English](README.en.md) | **中文**

# HTML Deck Studio

HTML Deck Studio 是一套面向 Codex 的 HTML 演示稿生产工具包。它把主题、资料、截图、文档或代码仓库加工成结构完整、视觉清晰、可播放、可编辑、可保存、可验证、可公开发布的 16:9 单文件 HTML PPT。

**Slogan：** Story first. Ship as HTML.（先建立叙事，再交付 HTML）

**理念：** 不把“做 PPT”当成套模板，而是当成一条完整生产线：先核验事实与主线，再设计页面系统，最后用自包含 HTML 交付，并通过本地编辑、静态检查和公开 viewer 导出完成闭环。

## 版本演进

这个仓库采用迭代方式保留两个版本，而不是用 V2 覆盖 V1。

| 版本 | 产品名 | 核心定位 | 路径 |
|---|---|---|---|
| V1 | HTML Deck Studio | 轻量双态 HTML Deck 编辑器 | 仓库根目录 |
| V2 | DeckForge Studio / DeckForge 演示工作室 | Viewer / Quick Edit / Studio 三态演示稿生产工作室 | [`V2版-DeckForge Studio（DeckForge 演示工作室）/`](./V2%E7%89%88-DeckForge%20Studio%EF%BC%88DeckForge%20%E6%BC%94%E7%A4%BA%E5%B7%A5%E4%BD%9C%E5%AE%A4%EF%BC%89/) |

V1 证明了轻量 HTML 演示稿工作流：直接打开 HTML 是展示态，本地 preview 服务运行时才启用编辑和保存。

V2 命名为 **DeckForge Studio / DeckForge 演示工作室**，继承 V1 的生成方法论，并新增 source/viewer 交付边界、Quick Edit、本地 Studio 工作台、parser 级 viewer 导出和回归测试。

## 你会得到什么

使用 HTML Deck Studio，你可以得到一套轻量但完整的演示稿生产能力：

- 一个 Codex Skill 工作流：从资料研究、叙事设计、页面实现到验收交付
- 一个自包含 HTML 模板：CSS、JS、SVG 和页面运行逻辑都在单文件内
- 固定 16:9 画布：默认 `1600 x 900`，自动等比缩放适配不同浏览器窗口
- 播放能力：时间线、上一页/下一页、键盘翻页、全屏、哈希路由和演讲者备注
- 轻量双态编辑：直接打开 HTML 是普通播放页；本地服务运行时右上角才显示“修改”按钮
- 图层级编辑：支持图层树、父子级选择、拖拽、尺寸调整、锁定/解锁和重置
- 本地保存：浏览器内编辑后，通过 Python 本地服务原子写回源 HTML
- 公开发布：可导出不含编辑器能力的 viewer-only HTML
- 静态验收：检查页面结构、控件、资源、SVG `viewBox`、占位符和双态编辑能力

## 快速开始

复制模板作为新演示稿：

```bash
cp assets/html-ppt-template.html deck.html
```

运行静态检查：

```bash
./scripts/check.sh deck.html
```

启动本地预览和编辑保存服务：

```bash
./scripts/preview.sh deck.html
```

打开浏览器访问：

```text
http://127.0.0.1:4173/deck.html
```

只有通过本地服务打开时，页面右上角才会显示 **“修改”** 按钮。直接双击打开同一个 HTML 文件时，它只是普通播放页，不显示编辑入口。

如果端口被占用，可以指定其他端口：

```bash
./scripts/preview.sh deck.html 4180
```

导出公开纯播放版：

```bash
./scripts/export_viewer.py deck.html deck.viewer.html
```

运行双态编辑端到端测试：

```bash
./scripts/test_dual_state.py
```

## 常用工作流

### 新建一份演示稿

1. 复制 `assets/html-ppt-template.html` 为你的目标文件。
2. 按 `references/story-and-content.md` 先整理逐页叙事。
3. 按 `references/design-system.md` 设计页面层级、字号、色彩和图形。
4. 在 HTML 中实现页面，并为重要元素保留稳定的 `data-layer-id`。
5. 运行 `./scripts/check.sh deck.html` 做静态验收。

### 本地编辑已有 HTML

1. 运行 `./scripts/preview.sh deck.html`。
2. 在浏览器中点击右上角 **“修改”**。
3. 从右侧图层树选择具体图层，或直接点击页面元素。
4. 拖拽选中框移动元素，用尺寸手柄调整宽高。
5. 使用 Inspector 修改 X / Y / W / H，或锁定、解锁、重置图层。
6. 点击“保存到源码”，把当前编辑结果写回原 HTML。

### 公开分享或部署

有两种方式：

- 轻量分享：直接分享 `deck.html`。由于没有本地服务注入标记，页面不会显示编辑入口。
- 更干净的公开版：运行 `./scripts/export_viewer.py deck.html deck.viewer.html`，生成不包含编辑器 UI、保存接口和图层元数据的纯播放版。

公开发布建议使用第二种方式。

## 自定义叙事与设计规则

HTML Deck Studio 的核心规则都写在 `references/` 中，方便 Codex 在生成演示稿前读取：

- `references/story-and-content.md` — 如何建立主线、页面任务、转场和演讲备注
- `references/design-system.md` — 固定画布、安全区、字体、配色、卡片、图形和截图规范
- `references/html-engineering.md` — 自包含 HTML、缩放、导航、编辑、保存和导出规则
- `references/qa-checklist.md` — 静态检查、浏览器检查、交互检查和交付验收清单
- `references/presentation-archetypes.md` — 常见汇报、产品、技术和案例型演示骨架

如果你希望改变默认风格，优先修改这些参考文档，而不是只改模板里的某一页。

## 默认模板能力

`assets/html-ppt-template.html` 默认包含：

- 封面页、内容页、图示页和致谢页
- 固定 `1600 x 900` 设计画布
- 页面标题提示与底部时间线
- 鼠标点击和键盘翻页
- 全屏播放
- 演讲者备注面板
- 轻量双态编辑入口
- 图层树和 Inspector 属性面板
- 本地保存服务状态检测
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
└── V2版-DeckForge Studio（DeckForge 演示工作室）/
```

## 安装与使用

### 作为普通项目使用

```bash
git clone https://github.com/JadenShaguo/html-deck-studio.git
cd html-deck-studio
cp assets/html-ppt-template.html deck.html
./scripts/preview.sh deck.html
```

### 作为 Codex Skill 使用

把项目放到 Codex 可读取的 skill 目录后，在任务中调用 `html-deck-studio`。生成演示稿时，Codex 应先读取 `SKILL.md` 和 `references/` 下的参考文档，再基于模板施工 HTML。

## 系统要求

- Python 3
- 一个现代浏览器
- Codex 或类似可读取 Skill 的 AI coding agent

不需要 Node.js、Vite、React、数据库、CDN 或任何远端运行时。脚本只使用 Python 标准库。

## 工作原理

1. Codex 读取 `SKILL.md` 和 `references/`，先建立事实底座和逐页叙事。
2. 新演示稿从 `assets/html-ppt-template.html` 复制开始，不从空白重建运行系统。
3. HTML 使用固定 16:9 画布，浏览器中按可视区自动缩放。
4. 直接打开 HTML 时，页面只进入播放态，不显示“修改”入口。
5. `preview.sh` 启动本地 Python 服务，服务端临时注入 `window.__HTML_DECK_STUDIO_LOCAL__=true`。
6. 页面检测到本地运行态后，显示“修改”按钮、图层树、Inspector 和保存能力。
7. 点击“保存到源码”后，浏览器把当前 HTML 发送给本地服务，服务端用临时文件 + `os.replace` 原子覆盖源文件。
8. `export_viewer.py` 可从源 HTML 生成不含编辑能力的公开 viewer 文件。
9. `test_dual_state.py` 自动验证本地运行态、保存清理和公开 viewer 导出是否正常。

## 公开边界

- 直接打开或部署 `deck.html` 时，不显示编辑入口，也没有键盘编辑入口。
- 本地编辑能力只在 `preview.sh` 运行状态下启用。
- 保存接口只接受本地服务允许的来源。
- `export_viewer.py` 会移除编辑器 UI、保存/下载按钮、图层元数据、本地服务标记和编辑缓存逻辑。
- 该项目不能阻止浏览器开发者工具层面的复制行为；它解决的是“分享页面不提供编辑入口和保存能力”的产品边界。

## 质量检查

常用检查命令：

```bash
./scripts/check.sh assets/html-ppt-template.html
./scripts/test_dual_state.py
python3 -m py_compile scripts/*.py
```

导出 viewer 后可额外检查：

```bash
./scripts/export_viewer.py deck.html deck.viewer.html
./scripts/check.sh deck.viewer.html
```

## 许可证

请以仓库中的实际 LICENSE 文件为准；如果准备公开发布，建议补充明确的开源许可证。
