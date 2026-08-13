# HTML PPT 验收清单

English summary: This checklist covers content, visual layout, static validation, optional browser checks, interaction testing, local save verification, deployment verification, and final delivery notes.

## 1. 内容验收

- [ ] 一句话主线明确。
- [ ] 痛点、发生机制、为什么改变均被说明。
- [ ] “做了什么”与“创造了什么杠杆”分开表达。
- [ ] 工作体系沉淀的对象明确，不只写抽象方法。
- [ ] 产品当前工作流程明确。
- [ ] 产品与研发、测试、AI 的协作流程明确。
- [ ] 每个典型场景按触发、动作、结果组织。
- [ ] 数字有口径、范围、时间与来源。
- [ ] 最快案例、平均效率与推算值没有混用。
- [ ] 首页与尾页复述同一核心结论。
- [ ] 演讲者备注足以支撑目标时长。

## 2. 视觉验收

逐页截图并检查：

- [ ] 画布比例为 16:9。
- [ ] 页面四边安全区等距且无内容侵入。
- [ ] 每页只有一个最大标题。
- [ ] 最小文字可读，字号层级差距不过大。
- [ ] 所有文字行距正常，无重叠或相切。
- [ ] 标题不被控件或页眉遮挡。
- [ ] 浅色页没有大面积黑色卡片。
- [ ] 分割线颜色、粗细一致。
- [ ] 卡片圆角一致。
- [ ] 图片无多余背景，圆角和无偏移投影正确。
- [ ] 图片右侧注释区充分利用空间并对齐。
- [ ] 流程图/架构图是真实关系图，不是并列卡片排版。
- [ ] SVG 箭头美观，不盖字、不穿框、不出现尖锐折角。
- [ ] 时间线数量与页面数一致。
- [ ] 尾页与首页样式对齐。

## 3. 无浏览器静态检查

任何环境都先运行：

```bash
./scripts/check.sh "/absolute/path/deck.source.html" source
```

该检查不依赖第三方包或浏览器，覆盖：

- HTML 基础结构、DOCTYPE 和幻灯片数量。
- 每页 `data-title` 与 `data-note`。
- 16:9 固定画布声明。
- 导航、全屏、时间线和演讲者备注。
- source 图层元数据：`data-editable`、`data-layer-id`、`data-layer-name`。
- 重复 ID、缺失 SVG `viewBox`。
- 外部脚本、样式、图片和本机文件路径。
- source 不应包含本地 runtime 注入脚本或工作台 UI。

公开交付前必须导出并检查 viewer：

```bash
./scripts/export_viewer.py deck.source.html deck.html
./scripts/check.sh deck.html viewer
```

viewer 检查必须确认：

- 没有 `快速修改` 和 `打开工作台`。
- 没有 `__studio__`、`__HTML_DECK_STUDIO_LOCAL__` 或 `quick-edit.js`。
- 没有 `data-editable`、`data-layer-id`、`data-layer-name`。
- 没有保存按钮、下载源码按钮或 `contenteditable`。

静态检查不能证明视觉布局正确。若环境没有自动浏览器或截图能力，必须在交付说明中列出未自动验证的动态项目，不能声称已完成视觉验收。

## 4. 可用时执行动态布局检查

在浏览器执行每页越界检测：

```js
const results=[...document.querySelectorAll(".slide")].map((slide,index)=>{
  const r=slide.getBoundingClientRect();
  const overflow=[...slide.querySelectorAll("*")].filter(el=>{
    const b=el.getBoundingClientRect();
    return b.left<r.left-1 || b.right>r.right+1 ||
           b.top<r.top-1 || b.bottom>r.bottom+1;
  }).map(el=>({
    tag:el.tagName,
    className:String(el.className),
    text:(el.textContent||"").trim().slice(0,80)
  }));
  return {slide:index+1,overflow};
});
```

还要检测：

- `scrollWidth > clientWidth` 或 `scrollHeight > clientHeight`。
- 文本元素矩形相交。
- 图片自然尺寸为 0。
- SVG `viewBox` 缺失。
- 资源加载失败。

窗口组合至少包括：

- 1920×1080 或等效 16:9。
- 1366×768。
- 1024×768 或较窄窗口。

三种尺寸都必须完整展示整页，不能依靠滚动看到被裁内容。

没有浏览器自动化但能打开系统浏览器时，启动本地服务并打开页面，使用环境现有的截图或预览能力逐页观察。不要要求用户安装特定浏览器插件。

## 5. 可用时执行交互验收

- [ ] 前进、后退图标正常。
- [ ] 上下左右键均可切页。
- [ ] Home/End 正常。
- [ ] 时间线每段可点击。
- [ ] 悬停时间线显示页序和标题。
- [ ] 哈希与当前页同步。
- [ ] 全屏正常。
- [ ] 直接打开 source 文件时不显示编辑入口。
- [ ] preview 服务打开 source 页面时显示 `快速修改` 和 `打开工作台`。
- [ ] Quick Edit 可进入、退出。
- [ ] Quick Edit 文本可直接修改。
- [ ] Quick Edit 元素可移动，选中后方向键可微调。
- [ ] Quick Edit 编辑文本时不会误切页。
- [ ] Studio 工作台可打开并加载当前 source。
- [ ] Studio 图层树可选择当前页图层。
- [ ] Studio 保存按钮可写回 source。
- [ ] Studio 导出 viewer 按钮可生成公开 HTML。
- [ ] 控制台无错误。

## 6. 保存与部署验收

本地保存：

- [ ] Quick Edit 保存按钮可写回 source。
- [ ] Studio 保存按钮可写回 source。
- [ ] 保存后原 HTML 的修改时间和内容改变。
- [ ] 刷新后文本、位置与尺寸仍存在。
- [ ] source 不包含本地运行时注入脚本。
- [ ] viewer 不包含编辑入口或图层元数据。
- [ ] 临时文件已清理。

部署：

- [ ] 部署工具要求的元数据均由用户明确提供。
- [ ] 部署 API 返回成功。
- [ ] 平台目录索引 URL 实际打开验证。
- [ ] 服务器真实文件 URL 实际打开验证。
- [ ] 页面标题正确。
- [ ] 远端图片、SVG、键盘导航和全屏正常。
- [ ] 如果索引失效，交付真实文件 URL 并说明原因。

## 7. 最终交付记录

记录：

- 源文件绝对路径。
- 页面数与建议时长。
- 使用的事实来源。
- 核心数字及口径。
- 已完成的静态检查结果。
- 已测试浏览器尺寸（若具备可视化能力）。
- 自动化溢出检查结果（若具备浏览器控制能力）。
- 编辑、保存、部署验证结果。
- 仍然存在的限制或未验证项。
