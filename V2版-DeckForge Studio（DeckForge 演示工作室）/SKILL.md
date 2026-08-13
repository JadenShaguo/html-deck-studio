---
name: html-deck-studio-v2
description: 将主题、资料、截图、文档或代码仓库制作成结构完整、视觉清晰、可本地编辑、可验证并可公开交付的 16:9 HTML 演示稿。V2 使用 Viewer / Quick Edit / Studio 三态产品架构：公开 viewer 只展示，本地 source 可快速修改，也可进入 Studio 工作台做图层级编辑。
---

# HTML Deck Studio V2

HTML Deck Studio V2 不是单纯的网页编辑器。它是一套从资料输入、叙事设计、HTML 生成、本地编辑、静态检查到公开交付的完整演示稿生产工具链。

核心原则：

- **先做叙事，再做页面。** 不从套版和排版开始。
- **source 用于生产，viewer 用于公开。** 公开 HTML 必须不可编辑。
- **一个 preview 服务，两个本地编辑入口。** 本地运行后可以快速修改，也可以打开 Studio 工作台。
- **生成工作流继承 V1 主干，编辑架构升级为 V2 三态。**

## 必读路由

开始前按任务读取对应参考，且必须完整读取所选文件：

- 所有任务：读 `references/story-and-content.md`、`references/design-system.md`、`references/html-engineering.md`、`references/qa-checklist.md`。
- 根据主题类型额外读 `references/presentation-archetypes.md`，选择匹配的叙事骨架。
- 新建演示稿：复制 `assets/source-template.html` 为 `deck.source.html`。
- 本地预览和编辑：运行 `scripts/preview.sh deck.source.html`。
- 公开交付：运行 `scripts/export_viewer.py deck.source.html deck.html`，再检查 viewer。

## 三态产品架构

### Viewer Mode：公开展示态

触发条件：

- 打开 `deck.html`。
- 访问 GitHub Pages 或其他静态部署地址。
- 双击导出的 viewer 文件。

能力边界：

- 可以翻页、全屏、播放媒体、查看演讲者备注。
- 不显示 `快速修改`。
- 不显示 `打开工作台`。
- 不包含保存接口、下载源码按钮、编辑工具栏、图层树或 Studio 脚本。
- 不包含 `data-editable`、`data-layer-id`、`data-layer-name` 等编辑元数据。

### Quick Edit Mode：本地快速修改态

触发条件：

- 运行 `./scripts/preview.sh deck.source.html`。
- 打开 source 页面后点击右上角 `快速修改`。

适用场景：

- 改一句文案。
- 微调图片、卡片或按钮位置。
- 临时修补页面里的小问题。

能力边界：

- 支持文本直接编辑。
- 支持拖拽非锁定图层。
- 支持方向键微调，Shift 加速。
- 支持保存回 `deck.source.html`。
- 不承担复杂父子级管理、z-index、批量对齐、成组/解组等任务。

### Studio Mode：本地工作台编辑态

触发条件：

- 运行 `./scripts/preview.sh deck.source.html`。
- 在 source 页面点击 `打开工作台`，或直接访问 `/__studio__/workbench?file=deck.source.html`。

适用场景：

- 图层选不中。
- 拖动一个元素时误带动父容器。
- 需要看父子级关系。
- 需要数值化修改 X/Y/W/H。
- 需要锁定 group、保存 source、导出 viewer。

能力边界：

- iframe 加载 source 页面。
- 图层树展示当前页 `data-editable` 图层。
- 点击图层选中画布元素，点击画布反向选中图层。
- 属性面板至少支持 X、Y、W、H、锁定、重置。
- 保存写回 source 文件。
- 导出 viewer 时必须清理所有编辑能力。

## 强制工作流

### 1. 明确交付约束

提取或确认：

- 主题、受众、场合、演讲时长、核心结论。
- 参考资料、在线文档链接、截图、代码仓库与可信数据源。
- 是否需要先交大纲、是否要写入外部文档、HTML 输出路径、是否需要部署。
- 视觉参考 URL 与用户明确的字体、色彩、布局偏好。

已给出的信息不要重复追问。优先读取资料和仓库；只有缺失信息会显著改变叙事或外部操作时才询问。

### 2. 建立事实底座

- 查看用户提供的每一张图片；不要只读文字描述。
- 遇到在线文档链接时，优先使用当前环境可用的文档连接器读取正文、画板、附件和表格。
- 用户说“仓库是最新实现”时，以仓库为实现事实源；检查架构、目录、协议、流程、提交和可验证数据。
- 统计代码行、需求数、变更数或比例时，记录口径、范围、时间点和公式。
- 区分投入规模和管理杠杆，不把两类数字混为一谈。
- 不把无法核验的数字、宣传语或主办方建议直接当成结论。
- 需要最新网页资料或精确引用时浏览并保留来源。

### 3. 先做叙事，再做页面

除非用户明确要求直接施工，否则先提交逐页大纲供确认。每页必须定义：

1. 页序与预计时长。
2. 本页在故事中的任务。
3. 唯一主标题。
4. 屏幕上实际展示的文本。
5. 应使用的图：流程图、架构图、对比图、数据图或产品截图。
6. 演讲者备注与转场句。
7. 事实来源或需要核验的假设。

按 `references/story-and-content.md` 组织叙事。大纲稳定后自行完成一轮文案精炼：删除空泛词与重复句，缩短标题，补齐转场，检查事实、数字、专有名词和因果关系没有被改写。

### 4. 设计页面系统

- 全部页面使用固定 16:9 设计画布，并整体等比缩放到浏览器可视区。
- 页面四周保留统一安全区；任何内容都不得进入安全区。
- 每页只有一个最大标题；不要让多个模块争抢第一视觉层级。
- 浅色页面禁止大面积黑色或深色卡片；深色底只用于整页深色主题。
- 流程、架构、映射、层级和循环关系必须画成图，不要用“排版卡片”假装流程图。
- 除产品真实截图外，所有图形都使用内嵌 SVG；真实截图也应内嵌或转成可交付资源。
- 图中连线使用圆角路径和 SVG marker；箭头不穿字、不盖字、不制造无意义回折。
- 设计细则以 `references/design-system.md` 为准。

### 5. 实现 source HTML

以 `assets/source-template.html` 为基础：

- 将 CSS、JS、SVG 和必要媒体组织为可本地预览的 HTML Deck。
- 保留目录进度条、页面标题提示、前进/后退、全屏、键盘导航和演讲者备注。
- 重要元素必须有稳定 `data-editable`、`data-layer-id`、`data-layer-name`。
- 图片、视频、按钮、卡片、标题、正文和结论条应拆成可单独选择的原子图层。
- 布局容器、左右栏、整页分组使用 `data-editable="group"`，默认加 `data-edit-locked="true"`，避免误拖整组。
- SVG 复杂图示默认作为一个 `data-editable="svg"` 图层；不要把 SVG 内部每个 path 都暴露成普通拖拽图层。
- 新内容使用语义化元素和稳定 class；不要用绝对定位堆砌整页。
- 新内容使用稳定 `data-layer-id`，不要依赖 DOM 顺序生成编辑 ID；同一文件中 `data-layer-id` 不得重复。
- source 文件不直接内嵌完整工作台 UI；本地运行时由 preview 服务注入 Quick Edit 入口。

### 6. 用截图承载真实产品场景

每张产品截图独占一页时，按“场景”而不是“功能说明”写：

- **什么时候发生**：触发条件、原始痛点。
- **产品怎么做**：产品在系统中的具体动作和判断。
- **系统形成什么结果**：生成的事实、协议、证据或后续输入。
- 底部只保留一句结果结论。

布局规则：

- 图片保持合理原始比例，不加大面积背景容器。
- 图片使用圆角和无方向偏移的柔和投影。
- 右侧注释区在图片右边缘和右安全区之间居中并充分拉宽。
- 右上说明放在注释正文上方，顶部不得高于图片。

### 7. 逐轮修改时保护结构

- 把用户反馈翻译成系统规则后批量检查同类页面，而不是只修截图中的单页。
- 改标题或布局后清理对应编辑缓存，避免旧文本和旧位置覆盖新源码。
- 增删页面后重新核对页码、时间线数量、哈希路由、图层 ID 和致谢页。
- 不删除用户未要求删除的事实、备注、交互和编辑能力。
- 不为了塞下内容缩小到不可读；优先重组、拆页、简化句子或扩大有效区域。

## 编辑与保存规则

### Quick Edit 保存

保存前必须清理：

- `contenteditable`
- `spellcheck`
- 选中框和运行时 UI
- runtime 注入脚本
- 空 `style`
- 临时 `data-qe-*`

保存后 source 文件必须仍然通过 source 检查。

### Studio 保存

保存前必须清理：

- 工作台注入样式
- 选中态属性
- `contenteditable`
- `spellcheck`
- 空 `style`
- runtime 注入脚本

保存接口只能写回当前 preview 服务启动时指定的 source 文件。

### Viewer 导出

公开交付必须运行：

```bash
./scripts/export_viewer.py deck.source.html deck.html
./scripts/check.sh deck.html viewer
```

viewer 必须移除：

- Quick Edit 入口
- Studio 入口
- 保存按钮
- 下载 HTML
- 编辑工具栏
- 工作台脚本
- `data-editable`
- `data-layer-id`
- `data-layer-name`
- `data-edit-locked`
- `contenteditable`
- `spellcheck`
- `__studio__`
- `__HTML_DECK_STUDIO_LOCAL__`

viewer 必须保留：

- 翻页
- 全屏
- Hash 路由
- 媒体播放或查看
- 演讲者备注展示能力

## 分级验收

按 `references/qa-checklist.md` 完成：

- source 检查：`./scripts/check.sh deck.source.html source`
- viewer 导出：`./scripts/export_viewer.py deck.source.html deck.html`
- viewer 检查：`./scripts/check.sh deck.html viewer`
- 三态入口测试：`./scripts/test_three_modes.py`
- Quick Edit 保存测试：`./scripts/test_quick_edit.py`（存在时必须运行）
- Studio 测试：`./scripts/test_studio_mode.py`（存在时必须运行）
- Python 脚本编译：`python3 -m py_compile scripts/*.py`

发现问题后修复并重复验证，直到问题消失。

## 交付与部署

交付时给出：

- source 文件路径：用于本地继续编辑。
- viewer 文件路径：用于公开展示和部署。
- 页面数量、演讲时长建议与已验证范围。
- 重要数据口径或尚未验证的限制。
- 已运行的检查命令和结果。
- 本地 preview 服务地址（若已启动）。

用户要求部署时，使用当前环境可用的静态站点部署工具。部署前必须让用户明确提供目标平台要求的元数据，不得从主题或文件名推断。

## 完成标准

只有同时满足以下条件才算完成：

- 叙事能用一句主线复述，每页都有不可替代的作用。
- 背景、核心问题、方案逻辑、价值证据与行动结论讲清楚。
- 事实有来源，数字有口径，建设规模与管理杠杆没有混为一谈。
- 架构与流程关系主要靠图表达，图是清晰的内嵌 SVG。
- source 可本地运行、可快速修改、可进入 Studio、可保存。
- viewer 不包含任何编辑入口、保存接口、下载源码能力或图层元数据。
- 静态检查全部通过；有可视化能力时，常见窗口尺寸下整页完整可见、文字不重叠、安全区一致。
