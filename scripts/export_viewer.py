#!/usr/bin/env python3
"""Export a lightweight dual-state deck into a public viewer-only HTML file."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


FORBIDDEN_VIEWER_TOKENS = (
    "data-editable",
    "data-layer-id",
    "data-layer-name",
    "data-edit-locked",
    "data-edit-id",
    "data-edit-text-id",
    "editToggle",
    "editToolbar",
    "saveCurrentHtml",
    "downloadCurrentHtml",
    "layerPanel",
    "layerTree",
    "inspectorPanel",
    "editSelection",
    "editToast",
    "__HTML_DECK_STUDIO_LOCAL__",
    "htmlDeckStudioLocalFlag",
    "contenteditable",
    "localStorage",
    "/__ppt_editor_save__",
    "/__ppt_editor_status__",
)


VIEWER_RUNTIME = r'''<script>
    (function(){
      var deck=document.getElementById("deck");
      var slides=[].slice.call(document.querySelectorAll(".slide"));
      var label=document.getElementById("slideLabel");
      var timeline=document.getElementById("timeline");
      var notePanel=document.getElementById("speakerNotes");
      var noteText=document.getElementById("noteText");
      var active=0;
      var currentScale=1;

      function fitDeck(){
        var gapX=32;
        var gapY=32;
        currentScale=Math.max(.1,Math.min(
          (window.innerWidth-gapX)/1600,
          (window.innerHeight-gapY)/900
        ));
        document.documentElement.style.setProperty("--deck-scale",String(currentScale));
      }

      function clamp(index){return Math.max(0,Math.min(slides.length-1,index))}

      function showSlide(index,writeHash){
        active=clamp(index);
        slides.forEach(function(slide,i){slide.classList.toggle("active",i===active)});
        timeline.querySelectorAll("button").forEach(function(button,i){button.classList.toggle("active",i===active)});
        label.textContent=slides[active].dataset.title||"";
        noteText.textContent=slides[active].dataset.note||"";
        if(writeHash!==false){history.replaceState(null,"","#"+(active+1))}
      }

      function buildTimeline(){
        timeline.replaceChildren();
        slides.forEach(function(slide,index){
          var button=document.createElement("button");
          button.type="button";
          button.dataset.tip=(index+1)+" / "+(slide.dataset.title||"未命名");
          button.setAttribute("aria-label","跳转至第 "+(index+1)+" 页："+(slide.dataset.title||"未命名"));
          button.addEventListener("click",function(){showSlide(index,true)});
          timeline.appendChild(button);
        });
      }

      function toggleFullscreen(){
        if(document.fullscreenElement){document.exitFullscreen()}
        else{document.documentElement.requestFullscreen()}
      }

      document.getElementById("prev").addEventListener("click",function(){showSlide(active-1,true)});
      document.getElementById("next").addEventListener("click",function(){showSlide(active+1,true)});
      document.getElementById("fullscreen").addEventListener("click",toggleFullscreen);

      document.addEventListener("keydown",function(event){
        if((event.key==="n"||event.key==="N")){
          event.preventDefault();
          notePanel.classList.toggle("show");
          return;
        }
        if(event.key==="ArrowLeft"||event.key==="ArrowUp"){
          event.preventDefault();showSlide(active-1,true);
        }else if(event.key==="ArrowRight"||event.key==="ArrowDown"||event.key===" "){
          event.preventDefault();showSlide(active+1,true);
        }else if(event.key==="Home"){
          event.preventDefault();showSlide(0,true);
        }else if(event.key==="End"){
          event.preventDefault();showSlide(slides.length-1,true);
        }
      });

      window.addEventListener("hashchange",function(){
        var requested=Number(location.hash.slice(1));
        if(Number.isFinite(requested)){showSlide(requested-1,false)}
      });
      window.addEventListener("resize",fitDeck);
      window.addEventListener("orientationchange",fitDeck);
      document.addEventListener("fullscreenchange",fitDeck);
      window.HTMLDeckStudioViewer={
        showSlide:showSlide,
        getActiveIndex:function(){return active},
        getScale:function(){return currentScale},
        refresh:function(){buildTimeline();fitDeck();showSlide(active,false)}
      };

      buildTimeline();
      fitDeck();
      var initial=Number(location.hash.slice(1));
      showSlide(Number.isFinite(initial)&&initial>0?initial-1:0,false);
    })();
  </script>'''


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export an editable deck to viewer-only HTML.")
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    return parser.parse_args()


def remove_block_by_id(html: str, tag: str, element_id: str) -> str:
    pattern = re.compile(
        rf"\n?\s*<{tag}\b(?=[^>]*\bid=[\"']{re.escape(element_id)}[\"'])[^>]*>.*?</{tag}>\s*",
        re.S,
    )
    return pattern.sub("", html)


def remove_edit_css(html: str) -> str:
    return re.sub(r"\n\s*/\* Editor \*/.*?\n\s*</style>", "\n  </style>", html, flags=re.S)


def remove_edit_entry_button(html: str) -> str:
    return re.sub(
        r"\n?\s*<button\b(?=[^>]*\bid=[\"']editToggle[\"'])[^>]*>.*?</button>\s*",
        "",
        html,
        flags=re.S,
    )


def strip_edit_attributes(html: str) -> str:
    html = re.sub(
        r"\s(?:data-editable|data-layer-id|data-layer-name|data-edit-locked|data-edit-id|data-edit-text-id|contenteditable|spellcheck)=(\"[^\"]*\"|'[^']*')",
        "",
        html,
    )

    def clean_class(match: re.Match[str]) -> str:
        classes = [
            item
            for item in match.group(1).split()
            if item not in {"edit-unit", "edit-mode", "local-edit-available"}
        ]
        return f' class="{" ".join(classes)}"' if classes else ""

    return re.sub(r'\sclass="([^"]*)"', clean_class, html)


def replace_runtime(html: str) -> str:
    return re.sub(r"<script>\s*\(function\(\)\{.*?\}\)\(\);\s*</script>", VIEWER_RUNTIME, html, flags=re.S)


def export_viewer(source: Path, output: Path) -> None:
    html = source.read_text(encoding="utf-8")
    if 'id="deck"' not in html or 'id="timeline"' not in html:
        raise SystemExit("Source does not look like an HTML Deck Studio presentation.")

    html = remove_edit_css(html)
    html = remove_edit_entry_button(html)
    for tag, element_id in (
        ("div", "editToolbar"),
        ("aside", "layerPanel"),
        ("aside", "inspectorPanel"),
        ("div", "editSelection"),
        ("div", "editToast"),
    ):
        html = remove_block_by_id(html, tag, element_id)
    html = strip_edit_attributes(html)
    html = replace_runtime(html)

    remaining = [token for token in FORBIDDEN_VIEWER_TOKENS if token in html]
    if remaining:
        raise SystemExit("Viewer export still contains editor token(s): " + ", ".join(remaining[:8]))

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(html, encoding="utf-8")


def main() -> None:
    args = parse_args()
    source = args.source.expanduser().resolve()
    output = args.output.expanduser().resolve()
    if not source.is_file():
        raise SystemExit(f"Source HTML does not exist: {source}")
    export_viewer(source, output)
    print(f"Exported viewer HTML: {output}")


if __name__ == "__main__":
    main()
