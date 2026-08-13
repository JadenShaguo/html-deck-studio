# HTML PPT 工程规范

English summary: This guide describes how to keep each deck as a self-contained HTML file with fixed-canvas scaling, hash navigation, speaker notes, edit mode, local save support, embedded SVG/images, and accessibility basics.

## 1. 单文件结构

最终交付默认是一个自包含 HTML：

- CSS 写在 `<style>`。
- JS 写在底部 `<script>`。
- SVG 直接内嵌或转成 `data:image/svg+xml`。
- PNG/JPEG 先放入 SVG `<image>`，再把完整 SVG 作为 data URL。
- 不依赖 CDN、远端字体、外部图片或构建工具。
- 每个 `<section class="slide">` 设置 `data-title` 与 `data-note`。

`data-title` 用于左上灰色页名、时间线提示和导航；不要在其中加入序号。

## 2. 固定画布缩放

使用固定尺寸画布：

```css
.deck{
  width:1600px;
  height:900px;
  position:absolute;
  left:50%;
  top:50%;
  transform:translate(-50%,-50%) scale(var(--deck-scale));
  transform-origin:center;
}
```

计算：

```js
const scale=Math.min(
  (window.innerWidth-gapX)/1600,
  (window.innerHeight-gapY)/900
);
document.documentElement.style.setProperty("--deck-scale",String(Math.max(.1,scale)));
```

监听 `resize`、`orientationchange` 和全屏变化。画布内部禁止 media query 重排，避免不同屏幕出现不同 PPT。

## 3. 导航与状态

必须支持：

- 哈希：`#1`、`#2`……，刷新后保持当前页。
- 上一页/下一页按钮。
- `ArrowLeft`、`ArrowUp` 上一页；`ArrowRight`、`ArrowDown`、Space 下一页。
- `Home` 第一页、`End` 最后一页。
- 全屏切换。
- 可点击时间线与悬停标题。
- 演讲者备注可隐藏，默认不占幻灯片内容区。

文本输入或 `contenteditable` 聚焦时，不触发切页。

## 4. 编辑模式

编辑模式只处理 SVG 外的页面元素。要求：

- 点击铅笔或按 `E` 切换。
- 主要单元自动添加 `.edit-unit` 和稳定 `data-edit-id`。
- 文本节点设置 `contenteditable=true`。
- 点击单元显示选框。
- 拖拽选框或单元移动。
- 东/西/东南手柄调整宽度与高度。
- 方向键移动选中元素 1px；Shift + 方向键移动 10px。
- Esc 取消选择。
- 编辑状态下方向键优先移动元素；未选中元素时才允许切页。
- `localStorage` 保存 `{units,texts}`，刷新后恢复。

页面改版导致单元顺序变化时，通过版本化 migration 清除对应页缓存：

```js
const key=storageKey+"-slide-5-layout-v2";
if(localStorage.getItem(key)!=="done"){
  for(const group of [editState.units,editState.texts]){
    for(const id of Object.keys(group)){
      if(id.startsWith("s5-")) delete group[id];
    }
  }
  saveEditState();
  localStorage.setItem(key,"done");
}
```

## 5. 保存机制

浏览器静态页面不能直接覆盖磁盘文件。使用随 Skill 提供的本地服务：

```bash
python3 scripts/serve_editable_ppt.py \
  --file "/absolute/path/deck.html" \
  --port 4173
```

“保存”按钮：

1. 结束文本编辑并关闭编辑模式。
2. 克隆 `document.documentElement`。
3. 把当前文本和单元位置写回克隆。
4. 清除选择框、临时 UI 和动态时间线。
5. `POST /__ppt_editor_save__`，发送 `{html}`。
6. 服务端在同目录写临时文件、`fsync`、保留权限并 `os.replace` 原子覆盖。

按钮文案只写“保存”，放在编辑工具栏最右侧。不要提供“导出 HTML”按钮。

远端静态部署可保留编辑界面，但无法覆盖服务器源文件；不要承诺远端保存。

## 6. 图片与 SVG

为所有图使用统一类：

```html
<img class="diagram-asset" src="data:image/svg+xml;base64,..." alt="具体内容说明">
```

真实截图包装：

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1440 1200">
  <title>产品场景截图</title>
  <defs>
    <clipPath id="shot-clip"><rect width="1440" height="1200" rx="18"/></clipPath>
  </defs>
  <image width="1440" height="1200" href="data:image/png;base64,..." clip-path="url(#shot-clip)"/>
</svg>
```

部署前确认没有 `file://`、相对图片路径或本机绝对路径残留。

## 7. 编辑缓存迁移

以下改动必须增加 migration 版本：

- 页面增删或排序。
- `editableUnits` 选择器变化。
- 页面 DOM 大幅重排。
- 标题或关键文案必须覆盖用户旧缓存。
- SVG 容器被替换。

只清除受影响页面，保留用户其他页面的编辑。

## 8. 可访问性与性能

- 按钮提供 `aria-label`。
- SVG 提供 `<title>` 或图片 `alt`。
- 颜色对比满足正常阅读。
- 不在每次鼠标移动时序列化完整 HTML。
- 拖拽期间使用 `requestAnimationFrame` 或轻量 transform。
- 大型图片优先压缩后再嵌入，避免单文件无限膨胀。
- 自包含文件仍需在目标浏览器实际打开验证。
