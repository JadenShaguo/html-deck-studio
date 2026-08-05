# HTML Deck Studio

HTML Deck Studio 是一个 Codex Skill 项目，用来把主题、资料、截图、文档或代码仓库加工成可播放、可编辑、可保存、可验证的 16:9 单文件 HTML PPT。

## 特性

- 单文件 HTML 交付：不依赖 CDN、远端字体、外部图片或构建流程。
- 浏览器内可编辑：支持文字编辑、模块拖拽、尺寸调整、键盘翻页、演讲者备注和全屏。
- 本地保存流程：启动轻量 Python 服务后，可把页面编辑结果原子写回源 HTML。
- 静态质量检查：检查结构、必要控件、外部资源、SVG `viewBox`、占位符和页面元数据。
- 演示生产工作流：叙事、视觉系统、工程实现和验收规则分开维护。

## 项目定位

这个项目不是 PowerPoint 插件、SaaS 产品，也不是 Node.js 应用。它是一套给 Codex 使用的便携式 HTML 演示稿生产工具包：

- 一个 `SKILL.md` 工作流；
- 一个自包含、可编辑的 HTML 模板；
- 一组叙事、设计、工程和验收参考文档；
- 两个零第三方依赖的 Python 工具脚本。

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
└── scripts/
    ├── check.sh
    ├── check_presentation.py
    ├── preview.sh
    └── serve_editable_ppt.py
```

## 运行要求

只需要 Python 3。脚本只使用 Python 标准库。

```bash
python3 --version
```

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

打开：

```text
http://127.0.0.1:4173/deck.html
```

如果端口被占用，可以指定其他端口：

```bash
./scripts/preview.sh deck.html 4180
```

## 制作流程

1. 明确主题、受众、场合、演讲时长和一句话主线。
2. 按 `references/story-and-content.md` 组织叙事。
3. 按 `references/design-system.md` 在固定 `1600 x 900` 画布中设计。
4. 从 `assets/html-ppt-template.html` 开始制作，保留导航、备注、编辑和保存能力。
5. 运行 `scripts/check_presentation.py` 或 `./scripts/check.sh`。
6. 有浏览器自动化能力时，再用截图验证布局和交互。

## 交付标准

- 最终演示稿是一个自包含 HTML 文件。
- 每页都有 `data-title` 和 `data-note`。
- 保留导航、时间线、全屏、演讲者备注和编辑模式。
- 本地保存服务可以把浏览器编辑结果写回源 HTML。
- 交付前静态检查通过。

## 可选集成

HTML Deck Studio 不依赖私有运行时服务、公司专用平台或私有 API。若你的 Codex 环境提供在线文档连接器、静态站点部署工具等能力，可以在具体任务中按需使用。
