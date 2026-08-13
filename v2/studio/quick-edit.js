(function () {
  var config = window.__HTML_DECK_STUDIO_LOCAL__;
  if (!config || document.getElementById("html-deck-studio-quick-edit-style")) {
    return;
  }

  var selected = null;
  var drag = null;
  var editing = false;

  function activeSlide() {
    return document.querySelector(".slide.active") || document.querySelector(".slide");
  }

  function scale() {
    if (window.HTMLDeckStudioViewer && window.HTMLDeckStudioViewer.getScale) {
      return window.HTMLDeckStudioViewer.getScale() || 1;
    }
    return Number(getComputedStyle(document.documentElement).getPropertyValue("--deck-scale")) || 1;
  }

  function layerName(layer) {
    return layer.dataset.layerName || layer.dataset.layerId || layer.dataset.editable || layer.tagName.toLowerCase();
  }

  function isLocked(layer) {
    return layer && layer.dataset.editLocked === "true";
  }

  function nearestLayer(node) {
    var slide = activeSlide();
    while (node && node !== slide && node !== document) {
      if (node.matches && node.matches("[data-editable]")) {
        return node;
      }
      node = node.parentElement;
    }
    return null;
  }

  function state(layer) {
    return {
      x: Number(layer.dataset.studioX || 0),
      y: Number(layer.dataset.studioY || 0)
    };
  }

  function applyPosition(layer, x, y) {
    layer.dataset.studioX = String(Math.round(x));
    layer.dataset.studioY = String(Math.round(y));
    layer.style.transform = "translate(" + x + "px," + y + "px)";
  }

  function select(layer) {
    if (selected) {
      selected.removeAttribute("data-qe-selected");
    }
    selected = layer;
    if (selected) {
      selected.dataset.qeSelected = "true";
    }
    var label = document.getElementById("html-deck-studio-selected-label");
    if (label) {
      label.textContent = selected ? "当前图层：" + layerName(selected) : "未选择图层";
    }
  }

  function setTextEditable(enabled) {
    document.querySelectorAll('[data-editable="text"]').forEach(function (el) {
      if (enabled) {
        el.setAttribute("contenteditable", "true");
        el.setAttribute("spellcheck", "false");
      } else {
        el.removeAttribute("contenteditable");
        el.removeAttribute("spellcheck");
      }
    });
  }

  function openWorkbench() {
    var page = 1;
    if (window.HTMLDeckStudioViewer && window.HTMLDeckStudioViewer.getActiveIndex) {
      page = window.HTMLDeckStudioViewer.getActiveIndex() + 1;
    }
    location.href = config.workbenchPath + "?file=" + encodeURIComponent(config.file) + "&page=" + page;
  }

  function enterQuickEdit() {
    editing = true;
    document.documentElement.classList.add("html-deck-studio-quick-editing");
    setTextEditable(true);
    document.getElementById("html-deck-studio-local-actions").hidden = true;
    document.getElementById("html-deck-studio-edit-toolbar").hidden = false;
    select(null);
  }

  function exitQuickEdit() {
    editing = false;
    document.documentElement.classList.remove("html-deck-studio-quick-editing");
    setTextEditable(false);
    document.getElementById("html-deck-studio-local-actions").hidden = false;
    document.getElementById("html-deck-studio-edit-toolbar").hidden = true;
    select(null);
  }

  function cleanForSave() {
    select(null);
    setTextEditable(false);
    var clone = document.documentElement.cloneNode(true);
    clone.classList.remove("html-deck-studio-quick-editing");
    [
      "html-deck-studio-local-actions",
      "html-deck-studio-edit-toolbar",
      "html-deck-studio-quick-edit-style",
      "html-deck-studio-local-runtime",
      "html-deck-studio-quick-edit-loader"
    ].forEach(function (id) {
      var node = clone.querySelector("#" + id);
      if (node) {
        node.remove();
      }
    });
    clone.querySelectorAll("[data-qe-selected]").forEach(function (el) {
      el.removeAttribute("data-qe-selected");
    });
    clone.querySelectorAll("[contenteditable],[spellcheck]").forEach(function (el) {
      el.removeAttribute("contenteditable");
      el.removeAttribute("spellcheck");
    });
    clone.querySelectorAll("[style]").forEach(function (el) {
      if (!el.getAttribute("style").trim()) {
        el.removeAttribute("style");
      }
    });
    return "<!doctype html>\n" + clone.outerHTML;
  }

  async function save() {
    var status = document.getElementById("html-deck-studio-save-status");
    var saveButton = document.getElementById("html-deck-studio-save");
    try {
      saveButton.disabled = true;
      status.textContent = "保存中";
      var response = await fetch(config.savePath, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ html: cleanForSave() })
      });
      var result = await response.json();
      if (!response.ok || !result.ok) {
        throw new Error(result.error || "保存失败");
      }
      setTextEditable(true);
      status.textContent = "已保存";
      status.className = "hds-qe-status ok";
    } catch (error) {
      if (editing) {
        setTextEditable(true);
      }
      status.textContent = "保存失败：" + error.message;
      status.className = "hds-qe-status err";
    } finally {
      saveButton.disabled = false;
    }
  }

  function onPointerDown(event) {
    if (!editing) {
      return;
    }
    var layer = nearestLayer(event.target);
    if (!layer) {
      select(null);
      return;
    }
    select(layer);
    if (layer.dataset.editable === "text" || isLocked(layer) || event.target.isContentEditable) {
      return;
    }
    event.preventDefault();
    var current = state(layer);
    drag = { layer: layer, startX: event.clientX, startY: event.clientY, x: current.x, y: current.y };
    document.addEventListener("pointermove",onPointerMove);
    document.addEventListener("pointerup",onPointerUp,{ once: true });
    document.addEventListener("pointercancel",onPointerUp,{ once: true });
  }

  function onPointerMove(event) {
    if (!drag) {
      return;
    }
    var ratio = scale();
    applyPosition(drag.layer, drag.x + (event.clientX - drag.startX) / ratio, drag.y + (event.clientY - drag.startY) / ratio);
  }

  function onPointerUp() {
    document.removeEventListener("pointermove",onPointerMove);
    drag = null;
  }

  function onKeyDown(event) {
    if (!editing || !selected || event.target.isContentEditable) {
      return;
    }
    var delta = event.shiftKey ? 10 : 1;
    var current = state(selected);
    if (event.key === "ArrowLeft") {
      event.preventDefault();
      applyPosition(selected,current.x - delta,current.y);
    } else if (event.key === "ArrowRight") {
      event.preventDefault();
      applyPosition(selected,current.x + delta,current.y);
    } else if (event.key === "ArrowUp") {
      event.preventDefault();
      applyPosition(selected,current.x,current.y - delta);
    } else if (event.key === "ArrowDown") {
      event.preventDefault();
      applyPosition(selected,current.x,current.y + delta);
    }
  }

  function installUi() {
    var style = document.createElement("style");
    style.id = "html-deck-studio-quick-edit-style";
    style.textContent = [
      ".hds-local-actions,.hds-edit-toolbar{position:fixed;z-index:99999;top:18px;right:18px;display:flex;align-items:center;gap:8px;padding:8px;border:1px solid rgba(216,213,205,.9);border-radius:999px;background:rgba(251,251,248,.96);box-shadow:0 8px 24px rgba(30,30,24,.12);font-family:Inter,'SF Pro Display','PingFang SC','Microsoft YaHei',sans-serif}",
      ".hds-local-actions[hidden],.hds-edit-toolbar[hidden]{display:none!important}",
      ".hds-local-actions button,.hds-edit-toolbar button{height:30px;border:1px solid #d8d5cd;border-radius:999px;background:#fff;color:#24231f;padding:0 12px;font-size:12.5px;font-weight:750;cursor:pointer}",
      ".hds-local-actions button:hover,.hds-edit-toolbar button:hover{border-color:#f46a3b;color:#f46a3b}",
      ".hds-edit-toolbar .primary{background:#f46a3b;color:#fff;border-color:#f46a3b}",
      ".hds-qe-status{min-width:64px;color:#77736a;font-size:12px;font-weight:650}.hds-qe-status.ok{color:#278e84}.hds-qe-status.err{color:#f46a3b}",
      "#html-deck-studio-selected-label{max-width:260px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:#77736a;font-size:12px;font-weight:650}",
      ".html-deck-studio-quick-editing [data-qe-selected='true']{outline:2px solid #f46a3b!important;outline-offset:3px!important}",
      ".html-deck-studio-quick-editing [contenteditable='true']{outline:1px dashed rgba(244,106,59,.45);outline-offset:2px}"
    ].join("\n");
    document.head.appendChild(style);

    var actions = document.createElement("div");
    actions.id = "html-deck-studio-local-actions";
    actions.className = "hds-local-actions";
    actions.innerHTML = '<button type="button" id="html-deck-studio-enter-quick">快速修改</button><button type="button" id="html-deck-studio-open-workbench">打开工作台</button>';
    document.body.appendChild(actions);

    var toolbar = document.createElement("div");
    toolbar.id = "html-deck-studio-edit-toolbar";
    toolbar.className = "hds-edit-toolbar";
    toolbar.hidden = true;
    toolbar.innerHTML = '<span id="html-deck-studio-selected-label">未选择图层</span><button type="button" class="primary" id="html-deck-studio-save">保存</button><button type="button" id="html-deck-studio-exit">退出编辑</button><button type="button" id="html-deck-studio-open-workbench-2">打开工作台</button><span class="hds-qe-status" id="html-deck-studio-save-status">本地已连接</span>';
    document.body.appendChild(toolbar);

    document.getElementById("html-deck-studio-enter-quick").addEventListener("click",enterQuickEdit);
    document.getElementById("html-deck-studio-open-workbench").addEventListener("click",openWorkbench);
    document.getElementById("html-deck-studio-open-workbench-2").addEventListener("click",openWorkbench);
    document.getElementById("html-deck-studio-exit").addEventListener("click",exitQuickEdit);
    document.getElementById("html-deck-studio-save").addEventListener("click",save);
    document.addEventListener("pointerdown",onPointerDown);
    document.addEventListener("keydown",onKeyDown,true);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded",installUi,{ once: true });
  } else {
    installUi();
  }
})();
