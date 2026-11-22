"""
Generates the Milestone 8 Interactive Font Inspector HTML:
  - All 7 Variable WOFF2 fonts embedded (font-weight: 400..700):
      * Sans, Serif, Mono (Upright & Italic -9.5°) + Symbols (wght 400..700 w/ rvrn & rtlm)
  - Live continuous Variable Weight (wght 400-700) range slider + 400/500/700 presets + Upright/Italic toggle
  - All 21 harmonized UFO master outlines preserved for Same-Weight/Same-Slant Skeleton Microscope
Outputs standalone HTML to specimens/inspector.html.
"""

from __future__ import annotations
import base64
import json
from pathlib import Path
from fontTools.pens.svgPathPen import SVGPathPen
import ufoLib2
from release_version import VERSION_STR

ROOT = Path(__file__).resolve().parent.parent


def _extract_ufo_outlines(ufo_name: str) -> tuple[dict, ufoLib2.Font]:
    ufo = ufoLib2.Font.open(ROOT / "sources" / ufo_name)
    glyphs = []
    for gname in ufo.lib["public.glyphOrder"]:
        g = ufo[gname]
        pen = SVGPathPen(ufo, lambda v: str(int(round(v))))
        g.draw(pen)
        cp = g.unicodes[0] if g.unicodes else -1
        glyphs.append([gname, cp, int(round(g.width)), pen.getCommands()])
    return {"glyphs": glyphs}, ufo


def build_payload() -> tuple[str, int, int, float, float, float]:
    specs: dict[tuple[str, str], str] = {}
    for fam, ps_fam in (
        ("sans", "AdmiraltySans"),
        ("serif", "AdmiraltySerif"),
        ("mono", "AdmiraltyMono"),
    ):
        for wkey, style_stem in (
            ("400", "Regular"),
            ("500", "Medium"),
            ("700", "Bold"),
            ("400i", "Italic"),
            ("500i", "MediumItalic"),
            ("700i", "BoldItalic"),
        ):
            specs[(fam, wkey)] = f"{ps_fam}-{style_stem}.ufo"
    for wkey, style_stem in (("400", "Regular"), ("500", "Medium"), ("700", "Bold")):
        specs[("symbols", wkey)] = f"AdmiraltySymbols-{style_stem}.ufo"

    families: dict[str, dict[str, dict]] = {"sans": {}, "serif": {}, "mono": {}, "symbols": {}}
    ufo_sans_reg = None

    for (fam, wgt), ufo_n in specs.items():
        data, ufo = _extract_ufo_outlines(ufo_n)
        families[fam][wgt] = data
        if fam == "sans" and wgt == "400":
            ufo_sans_reg = ufo

    assert ufo_sans_reg is not None
    kern_list = []
    for (k1, k2), val in sorted(ufo_sans_reg.kerning.items()):
        rep1 = ufo_sans_reg.groups[k1][0] if k1 in ufo_sans_reg.groups else k1
        rep2 = ufo_sans_reg.groups[k2][0] if k2 in ufo_sans_reg.groups else k2
        kern_list.append([rep1, rep2, val])

    vf_map = {
        "sans": ("Admiralty Sans", "normal", "AdmiraltySans[wght].woff2"),
        "sans_i": ("Admiralty Sans", "italic", "AdmiraltySans-Italic[wght].woff2"),
        "serif": ("Admiralty Serif", "normal", "AdmiraltySerif[wght].woff2"),
        "serif_i": ("Admiralty Serif", "italic", "AdmiraltySerif-Italic[wght].woff2"),
        "mono": ("Admiralty Mono", "normal", "AdmiraltyMono[wght].woff2"),
        "mono_i": ("Admiralty Mono", "italic", "AdmiraltyMono-Italic[wght].woff2"),
        "symbols": ("Admiralty Symbols", "normal", "AdmiraltySymbols[wght].woff2"),
    }
    vf_woff2: dict[str, dict] = {}
    vf_kb = 0.0
    sym_vf_kb = 0.0
    for key, (css_fam, css_style, fname) in vf_map.items():
        p = ROOT / "fonts" / "variable" / fname
        kb = p.stat().st_size / 1024.0
        vf_kb += kb
        if key == "symbols":
            sym_vf_kb = kb
        vf_woff2[key] = {
            "family": css_fam,
            "style": css_style,
            "woff2": base64.b64encode(p.read_bytes()).decode("ascii"),
            "kb": round(kb, 1),
        }

    static_kb = sum(p.stat().st_size for p in (ROOT / "fonts" / "woff2").glob("*.woff2")) / 1024.0

    sym_meta = json.loads((ROOT / "symbols" / "admiralty-symbols.json").read_text(encoding="utf-8"))
    symbol_catalog = [
        [
            rec["name"],
            rec["codepointInt"],
            rec["category"],
            list(dict.fromkeys([*rec["tags"], *(name for name, target in
                sym_meta.get("aliases", {}).items() if target == rec["name"])])),
            1 if rec["rtlMirror"] else 0,
            1 if rec["filled"] else 0,
        ]
        for rec in sym_meta["symbols"]
    ]

    payload = {
        "vfWoff2": vf_woff2,
        "families": families,
        "kerning": kern_list,
        "symbolCatalog": symbol_catalog,
    }
    return (
        json.dumps(payload, separators=(",", ":")),
        len(families["sans"]["400"]["glyphs"]),
        len(kern_list),
        round(vf_kb, 1),
        round(static_kb, 1),
        round(sym_vf_kb, 1),
    )


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Admiralty Font Inspector — v__VERSION__ (7 Variable Fonts + 21 Static + __SYMBOL_COUNT__ Symbols)</title>
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
  <style id="admiralty-font-face"></style>
  <style>
    .adm-sans {
      font-family: 'Admiralty Sans', 'PingFang HK', 'PingFang TC', 'PingFang SC', 'Noto Sans CJK TC', -apple-system, sans-serif;
    }
    .adm-serif {
      font-family: 'Admiralty Serif', 'Noto Serif CJK TC', 'Songti TC', 'STSongti-TC-Regular', 'Songti SC', Georgia, serif;
    }
    .adm-mono {
      font-family: 'Admiralty Mono', 'PingFang HK', ui-monospace, monospace;
    }
    .adm-symbols {
      font-family: 'Admiralty Symbols', sans-serif;
    }
    .adm-active {
      font-family: var(--adm-active-stack);
      font-weight: var(--adm-active-weight);
      font-style: var(--adm-active-style);
    }
    :root {
      --adm-active-stack: 'Admiralty Serif', 'Noto Serif CJK TC', 'Songti TC', Georgia, serif;
      --adm-active-weight: 400;
      --adm-active-style: normal;
    }
    .paper-light { background-color: #faf9f5; color: #16181c; border-color: #e4e2dc; }
    .paper-dark  { background-color: #131519; color: #eceef2; border-color: #2c313b; }
    .bubble-u-light { background-color: #e5ecf6; color: #16181c; }
    .bubble-a-light { background-color: #ffffff; color: #16181c; border: 1px solid #e4e2dc; }
    .bubble-u-dark  { background-color: #262e3c; color: #eceef2; }
    .bubble-a-dark  { background-color: #1b1f26; color: #eceef2; border: 1px solid #2e3440; }
  </style>
__STANDALONE_VARS__</head>
<body class="bg-[var(--background)] text-[var(--foreground)] antialiased p-4 md:p-6">
  <div class="max-w-6xl mx-auto space-y-4">
    <!-- Top Header -->
    <div class="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-[var(--border)]">
      <div class="space-y-1">
        <div class="flex flex-wrap items-center gap-2.5">
          <h1 id="hdr-family-title" class="text-lg font-semibold tracking-tight adm-active">Admiralty Serif Regular</h1>
          <span class="px-2 py-0.5 text-xs rounded-full bg-[var(--secondary)] text-[var(--secondary-foreground)] font-mono">v__VERSION__ · 7 Variable Fonts (__VF_KB__ KB) + 21 Static (__STATIC_KB__ KB)</span>
          <span class="px-2 py-0.5 text-xs rounded-full bg-[var(--card)] border border-[var(--border)] text-[var(--muted-foreground)] font-mono">Sym VF __SYM_KB__ KB</span>
        </div>
        <p class="text-xs text-[var(--muted-foreground)]">Designer: Lei Yutian · SIL OFL 1.1 · 1000 UPM · Continuous wght 400..700 Variable Axes · Upright &amp; -9.5° Cursive Italic</p>
      </div>

      <div class="flex flex-wrap items-center gap-2">
        <!-- Family Switcher -->
        <div class="flex flex-wrap gap-1 bg-[var(--card)] p-1 rounded-lg border border-[var(--border)] text-xs" id="fam-bar">
          <button data-fam="serif" class="fam-btn px-2.5 py-1.5 rounded-md font-medium bg-[var(--primary)] text-[var(--primary-foreground)]">Serif</button>
          <button data-fam="sans" class="fam-btn px-2.5 py-1.5 rounded-md font-medium text-[var(--muted-foreground)]">Sans</button>
          <button data-fam="mono" class="fam-btn px-2.5 py-1.5 rounded-md font-medium text-[var(--muted-foreground)]">Mono</button>
          <button data-fam="symbols" class="fam-btn px-2.5 py-1.5 rounded-md font-medium text-[var(--muted-foreground)]">Symbols</button>
        </div>

        <!-- Weight Presets + Live Variable wght Slider -->
        <div class="flex flex-wrap items-center gap-1.5 bg-[var(--card)] p-1 rounded-lg border border-[var(--border)] text-xs" id="wgt-bar">
          <button data-wgt="400" class="wgt-btn px-2.5 py-1.5 rounded-md font-medium bg-[var(--primary)] text-[var(--primary-foreground)]">Regular 400</button>
          <button data-wgt="500" class="wgt-btn px-2.5 py-1.5 rounded-md font-medium text-[var(--muted-foreground)]">Medium 500</button>
          <button data-wgt="700" class="wgt-btn px-2.5 py-1.5 rounded-md font-medium text-[var(--muted-foreground)]">Bold 700</button>
          <label class="flex items-center gap-1.5 px-2 py-0.5 border-l border-[var(--border)] text-[var(--muted-foreground)]">
            <span class="font-mono">wght</span>
            <input id="inp-vf-wght" type="range" min="400" max="700" step="1" value="400" class="w-24 accent-[var(--primary)]" />
            <span id="lbl-vf-wght" class="font-mono text-[var(--foreground)] w-7 text-right">400</span>
          </label>
        </div>

        <!-- Slant Switcher -->
        <div class="flex gap-1 bg-[var(--card)] p-1 rounded-lg border border-[var(--border)] text-xs" id="sln-bar">
          <button data-sln="normal" class="sln-btn px-2.5 py-1.5 rounded-md font-medium bg-[var(--primary)] text-[var(--primary-foreground)]">Upright</button>
          <button data-sln="italic" class="sln-btn px-2.5 py-1.5 rounded-md font-medium text-[var(--muted-foreground)]">Italic -9.5°</button>
        </div>

        <!-- Navigation Tabs -->
        <div class="flex flex-wrap gap-1 bg-[var(--card)] p-1 rounded-lg border border-[var(--border)] text-xs" id="tab-bar">
          <button data-tab="tester" class="tab-btn px-3 py-1.5 rounded-md font-medium bg-[var(--primary)] text-[var(--primary-foreground)]">自由试排</button>
          <button data-tab="microscope" class="tab-btn px-3 py-1.5 rounded-md font-medium text-[var(--muted-foreground)]">单字解剖显微镜</button>
          <button data-tab="lab" class="tab-btn px-3 py-1.5 rounded-md font-medium text-[var(--muted-foreground)]">易混与字距实验室</button>
          <button data-tab="chat" class="tab-btn px-3 py-1.5 rounded-md font-medium text-[var(--muted-foreground)]">三字体 App 原型</button>
          <button data-tab="symbols" class="tab-btn px-3 py-1.5 rounded-md font-medium text-[var(--muted-foreground)]">Symbols 图标库 (__SYMBOL_COUNT__)</button>
          <button data-tab="specs" class="tab-btn px-3 py-1.5 rounded-md font-medium text-[var(--muted-foreground)]">度量与 Kerning 表</button>
        </div>
      </div>
    </div>

    <!-- TAB 1: LIVE TYPE TESTER -->
    <section id="panel-tester" class="tab-panel space-y-4">
      <div class="bg-[var(--card)] border border-[var(--border)] rounded-xl p-4 space-y-3">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
          <label class="space-y-1 block">
            <div class="flex justify-between text-[var(--muted-foreground)]">
              <span>字号 (Font Size)</span>
              <span id="lbl-size" class="font-mono text-[var(--foreground)]">32 px</span>
            </div>
            <input id="inp-size" type="range" min="11" max="110" value="32" class="w-full accent-[var(--primary)]" />
            <div class="flex gap-1 pt-0.5">
              <button class="sz-preset px-1.5 py-0.5 rounded border border-[var(--border)] text-[var(--muted-foreground)]" data-sz="12">12</button>
              <button class="sz-preset px-1.5 py-0.5 rounded border border-[var(--border)] text-[var(--muted-foreground)]" data-sz="14">14</button>
              <button class="sz-preset px-1.5 py-0.5 rounded border border-[var(--border)] text-[var(--muted-foreground)]" data-sz="16">16</button>
              <button class="sz-preset px-1.5 py-0.5 rounded border border-[var(--border)] text-[var(--muted-foreground)]" data-sz="18">18</button>
              <button class="sz-preset px-1.5 py-0.5 rounded border border-[var(--border)] text-[var(--muted-foreground)]" data-sz="24">24</button>
              <button class="sz-preset px-1.5 py-0.5 rounded border border-[var(--border)] text-[var(--muted-foreground)]" data-sz="48">48</button>
              <button class="sz-preset px-1.5 py-0.5 rounded border border-[var(--border)] text-[var(--muted-foreground)]" data-sz="72">72</button>
            </div>
          </label>
          <label class="space-y-1 block">
            <div class="flex justify-between text-[var(--muted-foreground)]">
              <span>行高 (Line Height)</span>
              <span id="lbl-lh" class="font-mono text-[var(--foreground)]">1.48</span>
            </div>
            <input id="inp-lh" type="range" min="100" max="200" value="148" class="w-full accent-[var(--primary)]" />
          </label>
          <label class="space-y-1 block">
            <div class="flex justify-between text-[var(--muted-foreground)]">
              <span>字间距微调 (Tracking)</span>
              <span id="lbl-tr" class="font-mono text-[var(--foreground)]">0.000 em</span>
            </div>
            <input id="inp-tr" type="range" min="-40" max="80" value="0" class="w-full accent-[var(--primary)]" />
          </label>
        </div>

        <div class="flex flex-wrap items-center justify-between gap-2 pt-2 border-t border-[var(--card-border)] text-xs">
          <div class="flex flex-wrap items-center gap-1.5">
            <span class="text-[var(--muted-foreground)] mr-1">OpenType:</span>
            <button data-feat="kern" class="feat-btn px-2.5 py-1 rounded-md border border-[var(--primary)] bg-[var(--primary)] text-[var(--primary-foreground)] font-mono">kern (字距)</button>
            <button data-feat="pnum" class="feat-btn px-2.5 py-1 rounded-md border border-[var(--primary)] bg-[var(--primary)] text-[var(--primary-foreground)] font-mono">pnum (比例数字)</button>
            <button data-feat="tnum" class="feat-btn px-2.5 py-1 rounded-md border border-[var(--border)] text-[var(--muted-foreground)] font-mono">tnum (等宽数字)</button>
            <button data-feat="zero" class="feat-btn px-2.5 py-1 rounded-md border border-[var(--border)] text-[var(--muted-foreground)] font-mono">zero (斜杠 0)</button>
            <button data-feat="case" class="feat-btn px-2.5 py-1 rounded-md border border-[var(--border)] text-[var(--muted-foreground)] font-mono">case (大写标点居中)</button>
            <button data-feat="ss01" class="feat-btn px-2.5 py-1 rounded-md border border-[var(--border)] text-[var(--muted-foreground)] font-mono">ss01 (Mono 编程连字)</button>
          </div>
          <div class="flex items-center gap-1">
            <span class="text-[var(--muted-foreground)] mr-1">画布底色:</span>
            <button data-paper="auto" class="paper-btn px-2 py-1 rounded border border-[var(--primary)] font-medium">跟随主题</button>
            <button data-paper="light" class="paper-btn px-2 py-1 rounded border border-[var(--border)] text-[var(--muted-foreground)]">浅色暖纸</button>
            <button data-paper="dark" class="paper-btn px-2 py-1 rounded border border-[var(--border)] text-[var(--muted-foreground)]">深色夜间</button>
          </div>
        </div>

        <div class="flex flex-wrap items-center gap-1.5 pt-2 border-t border-[var(--card-border)] text-xs">
          <span class="text-[var(--muted-foreground)] mr-1">快速样文:</span>
          <button data-preset="hero" class="preset-btn px-2.5 py-1 rounded bg-[var(--secondary)] text-[var(--secondary-foreground)]">核心词与衬线细节</button>
          <button data-preset="disambig" class="preset-btn px-2.5 py-1 rounded bg-[var(--secondary)] text-[var(--secondary-foreground)]">易混与编码 (Il1 O0 rn/m)</button>
          <button data-preset="euro" class="preset-btn px-2.5 py-1 rounded bg-[var(--secondary)] text-[var(--secondary-foreground)]">泛欧多语种与符号</button>
          <button data-preset="prose" class="preset-btn px-2.5 py-1 rounded bg-[var(--secondary)] text-[var(--secondary-foreground)]">长段落阅读测试</button>
          <button data-preset="table" class="preset-btn px-2.5 py-1 rounded bg-[var(--secondary)] text-[var(--secondary-foreground)]">对账单数字列</button>
          <button data-preset="code80" class="preset-btn px-2.5 py-1 rounded bg-[var(--secondary)] text-[var(--secondary-foreground)]">80列代码与连字 (Mono)</button>
          <button data-preset="cjk" class="preset-btn px-2.5 py-1 rounded bg-[var(--secondary)] text-[var(--secondary-foreground)]">中英混排对齐</button>
        </div>
      </div>

      <div id="tester-surface" class="rounded-xl border border-[var(--border)] bg-[var(--card)] p-6 transition-colors">
        <div class="text-xs text-[var(--muted-foreground)] mb-2 flex justify-between">
          <span>可直接点击下方文本任意编辑（随时点击顶部切换 Sans / Serif 观察 0px 重排）：</span>
          <span id="tester-css-readout" class="font-mono">font-feature-settings: "kern" 1</span>
        </div>
        <div id="tester-editor" contenteditable="true" spellcheck="false" class="adm-active outline-none whitespace-pre-wrap break-words min-h-[220px]" style="font-size: 32px; line-height: 1.48;">Calm, literary clarity for your Personal Agent.
Admiralty Serif & Sans — Zero Layout Reflow (2026)
Il1 O0 rn/m   $1,480.95 €290 £75 ¥3,600   § © ª ← ↑ → ↓ ↩</div>
      </div>
    </section>

    <!-- TAB 2: GLYPH OUTLINE & NODE MICROSCOPE -->
    <section id="panel-microscope" class="tab-panel hidden space-y-4">
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-4">
        <div class="lg:col-span-5 bg-[var(--card)] border border-[var(--border)] rounded-xl p-3.5 flex flex-col space-y-3">
          <div class="flex flex-wrap items-center justify-between gap-2 text-xs">
            <div class="flex flex-wrap gap-1" id="cat-bar">
              <button data-cat="all" class="cat-btn px-2 py-1 rounded bg-[var(--primary)] text-[var(--primary-foreground)]">全部</button>
              <button data-cat="upper" class="cat-btn px-2 py-1 rounded text-[var(--muted-foreground)]">A–Z</button>
              <button data-cat="lower" class="cat-btn px-2 py-1 rounded text-[var(--muted-foreground)]">a–z</button>
              <button data-cat="figs" class="cat-btn px-2 py-1 rounded text-[var(--muted-foreground)]">数字</button>
              <button data-cat="punct" class="cat-btn px-2 py-1 rounded text-[var(--muted-foreground)]">扩展与符号</button>
              <button data-cat="feat" class="cat-btn px-2 py-1 rounded text-[var(--muted-foreground)]">OT变体</button>
            </div>
            <input id="glyph-search" type="text" placeholder="搜索名称或字符..." class="px-2 py-1 rounded border border-[var(--border)] bg-[var(--background)] text-xs w-32 outline-none" />
          </div>
          <div id="glyph-grid" class="grid grid-cols-7 sm:grid-cols-8 gap-1 max-h-[460px] overflow-y-auto pr-1"></div>
        </div>

        <div class="lg:col-span-7 bg-[var(--card)] border border-[var(--border)] rounded-xl p-4 space-y-3">
          <div class="flex flex-wrap items-center justify-between gap-2 text-xs pb-2 border-b border-[var(--card-border)]">
            <div class="flex items-center gap-2">
              <span id="mic-title" class="font-mono text-sm font-semibold">a</span>
              <span id="mic-uni" class="font-mono text-[var(--muted-foreground)]">U+0061</span>
            </div>
            <div class="flex flex-wrap items-center gap-2.5">
              <label class="flex items-center gap-1 cursor-pointer font-medium text-sky-600 dark:text-sky-400"><input type="checkbox" id="chk-ghost" checked class="accent-sky-500" />对比骨架叠影</label>
              <label class="flex items-center gap-1 cursor-pointer"><input type="checkbox" id="chk-fill" checked class="accent-[var(--primary)]" />填充</label>
              <label class="flex items-center gap-1 cursor-pointer"><input type="checkbox" id="chk-outline" checked class="accent-[var(--primary)]" />轮廓</label>
              <label class="flex items-center gap-1 cursor-pointer"><input type="checkbox" id="chk-nodes" checked class="accent-[var(--primary)]" />节点</label>
              <label class="flex items-center gap-1 cursor-pointer"><input type="checkbox" id="chk-metrics" checked class="accent-[var(--primary)]" />度量线</label>
            </div>
          </div>

          <div class="relative rounded-lg border border-[var(--border)] bg-[var(--background)] overflow-hidden">
            <div id="mic-coords" class="absolute top-2 right-2.5 text-xs font-mono text-[var(--muted-foreground)] pointer-events-none">UPM (x: —, y: —)</div>
            <div class="absolute top-2 left-2.5 flex items-center gap-3 text-xs font-mono text-[var(--muted-foreground)] pointer-events-none">
              <span>● 平滑点</span>
              <span>■ 转角点</span>
              <span class="text-sky-500">■ 蓝影 = 伴侣字体同宽骨架</span>
            </div>
            <svg id="mic-svg" viewBox="-140 -900 1080 1240" class="w-full h-[360px] select-none cursor-crosshair"></svg>
          </div>

          <div class="grid grid-cols-3 sm:grid-cols-6 gap-2 text-xs">
            <div class="p-2 rounded bg-[var(--background)] border border-[var(--border)]">
              <div class="text-[var(--muted-foreground)]">同宽步进</div>
              <div id="st-width" class="font-mono font-semibold mt-0.5">544</div>
            </div>
            <div class="p-2 rounded bg-[var(--background)] border border-[var(--border)]">
              <div class="text-[var(--muted-foreground)]">左留白 LSB</div>
              <div id="st-lsb" class="font-mono font-semibold mt-0.5">54</div>
            </div>
            <div class="p-2 rounded bg-[var(--background)] border border-[var(--border)]">
              <div class="text-[var(--muted-foreground)]">右留白 RSB</div>
              <div id="st-rsb" class="font-mono font-semibold mt-0.5">70</div>
            </div>
            <div class="p-2 rounded bg-[var(--background)] border border-[var(--border)]">
              <div class="text-[var(--muted-foreground)]">墨迹边界</div>
              <div id="st-bbox" class="font-mono font-semibold mt-0.5 text-[11px]">54..474</div>
            </div>
            <div class="p-2 rounded bg-[var(--background)] border border-[var(--border)]">
              <div class="text-[var(--muted-foreground)]">闭合轮廓数</div>
              <div id="st-contours" class="font-mono font-semibold mt-0.5">2</div>
            </div>
            <div class="p-2 rounded bg-[var(--background)] border border-[var(--border)]">
              <div class="text-[var(--muted-foreground)]">节点 / 控制柄</div>
              <div id="st-pts" class="font-mono font-semibold mt-0.5">18 / 24</div>
            </div>
          </div>

          <div class="p-3 rounded-lg bg-[var(--background)] border border-[var(--border)] space-y-1.5">
            <div class="text-xs text-[var(--muted-foreground)]">Sans vs Serif 上下文同宽实测 (14px / 18px / 32px)：</div>
            <div id="mic-context" class="flex flex-wrap items-baseline gap-6"></div>
          </div>
        </div>
      </div>
    </section>

    <!-- TAB 3: DISAMBIGUATION & SPACING LAB -->
    <section id="panel-lab" class="tab-panel hidden space-y-4">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div class="bg-[var(--card)] border border-[var(--border)] rounded-xl p-4 space-y-2">
          <div class="text-xs font-medium text-[var(--muted-foreground)]">1. 竖笔与连拱易混组：Il1| · rn vs m · cl vs d</div>
          <div class="adm-active text-4xl tracking-wide py-1">Il1|  rn m  cl d</div>
          <div class="adm-active text-sm space-y-1 pt-2 border-t border-[var(--card-border)]">
            <div><span class="font-mono text-xs text-[var(--muted-foreground)] mr-2">12px</span><span style="font-size:12px">Il1|  rn/m  ID-10lI  Hello  11:15</span></div>
            <div><span class="font-mono text-xs text-[var(--muted-foreground)] mr-2">14px</span><span style="font-size:14px">Il1|  rn/m  ID-10lI  Hello  11:15</span></div>
            <div><span class="font-mono text-xs text-[var(--muted-foreground)] mr-2">16px</span><span style="font-size:16px">Il1|  rn/m  ID-10lI  Hello  11:15</span></div>
          </div>
        </div>

        <div class="bg-[var(--card)] border border-[var(--border)] rounded-xl p-4 space-y-2">
          <div class="text-xs font-medium text-[var(--muted-foreground)]">2. 圆形易混组：O / 0 (微点) / 0 (斜杠) / o</div>
          <div class="adm-active text-4xl tracking-wide py-1">O0 <span style="font-feature-settings:'zero' 1">0</span> o</div>
          <div class="adm-active text-sm space-y-1 pt-2 border-t border-[var(--card-border)]">
            <div><span class="font-mono text-xs text-[var(--muted-foreground)] mr-2">默认</span><span style="font-size:14px">O0o  CX801  $1,250.00  #O08</span></div>
            <div><span class="font-mono text-xs text-[var(--muted-foreground)] mr-2">zero</span><span style="font-size:14px;font-feature-settings:'zero' 1">O0o  CX801  $1,250.00  #O08</span></div>
            <div><span class="font-mono text-xs text-[var(--muted-foreground)] mr-2">tnum</span><span style="font-size:14px;font-feature-settings:'tnum' 1">$1,111.10 vs $8,490.05</span></div>
          </div>
        </div>

        <div class="bg-[var(--card)] border border-[var(--border)] rounded-xl p-4 space-y-2">
          <div class="text-xs font-medium text-[var(--muted-foreground)]">3. 标点与连字清晰度：fi fl fj · ‘ ’ “ ” ` '</div>
          <div class="adm-active text-4xl tracking-wide py-1">fi fl fj  ‘ ’ ` '</div>
          <div class="adm-active text-sm space-y-1 pt-2 border-t border-[var(--card-border)]">
            <div><span class="font-mono text-xs text-[var(--muted-foreground)] mr-2">13px</span><span style="font-size:13px">‘Quote’, “Dialog”; `code` 'str' fi fl fj</span></div>
            <div><span class="font-mono text-xs text-[var(--muted-foreground)] mr-2">15px</span><span style="font-size:15px">‘Quote’, “Dialog”; `code` 'str' fi fl fj</span></div>
            <div><span class="font-mono text-xs text-[var(--muted-foreground)] mr-2">case</span><span style="font-size:14px;font-feature-settings:'case' 1">[ADMIRALTY — (2026: OK)]</span></div>
          </div>
        </div>
      </div>

      <!-- Duplex Zero-Reflow Stacked Strip -->
      <div class="bg-[var(--card)] border border-[var(--border)] rounded-xl p-4 space-y-2.5">
        <div class="text-xs font-medium text-[var(--muted-foreground)]">1:1 同宽共享骨架与共享 Kerning 叠行对照（随顶部 400/500/700 × Upright/Italic 联动，0.00 px 位移）：</div>
        <div class="p-3.5 rounded-lg bg-[var(--background)] border border-[var(--border)] space-y-2 overflow-x-auto">
          <div class="adm-sans text-2xl whitespace-nowrap opacity-70" style="font-weight:var(--adm-active-weight);font-style:var(--adm-active-style)">Admiralty Personal Agent — WAVEY To Va Yo (f) “Hello!” $1,480.95 €290 ← ↑ → ↓ ↩</div>
          <div class="adm-serif text-2xl whitespace-nowrap" style="font-weight:var(--adm-active-weight);font-style:var(--adm-active-style)">Admiralty Personal Agent — WAVEY To Va Yo (f) “Hello!” $1,480.95 €290 ← ↑ → ↓ ↩</div>
        </div>
      </div>

      <div class="bg-[var(--card)] border border-[var(--border)] rounded-xl p-4 space-y-2">
        <div class="flex items-center justify-between text-xs">
          <span class="font-medium text-[var(--muted-foreground)]">Walter Tracy 匀质灰度扫描串（检查衬线与脚座在直笔/圆笔之间的节奏）：</span>
          <div class="flex gap-1">
            <button id="wt-lc" class="px-2 py-1 rounded bg-[var(--primary)] text-[var(--primary-foreground)]">小写 nn*noo</button>
            <button id="wt-uc" class="px-2 py-1 rounded border border-[var(--border)] text-[var(--muted-foreground)]">大写 HH*HOO</button>
          </div>
        </div>
        <div id="wt-output" class="adm-active text-xl leading-relaxed pt-1 grid grid-cols-2 sm:grid-cols-4 md:grid-cols-6 gap-y-1.5 gap-x-3"></div>
      </div>
    </section>

    <!-- TAB 4: DUAL-FAMILY CHAT UI & ZERO-REFLOW ROLE SWAP -->
    <section id="panel-chat" class="tab-panel hidden space-y-4">
      <div class="bg-[var(--card)] border border-[var(--border)] rounded-xl p-4 flex flex-wrap items-center justify-between gap-4 text-xs">
        <div class="flex flex-wrap items-center gap-4">
          <button id="btn-swap-roles" class="px-3 py-1.5 rounded-lg bg-[var(--primary)] text-[var(--primary-foreground)] font-medium">⇄ 互换 Agent / User 字体角色</button>
          <span id="role-status-badge" class="font-mono px-2.5 py-1 rounded bg-[var(--secondary)] text-[var(--secondary-foreground)]">当前默认：Agent = Serif · User = Sans</span>
          <span id="reflow-audit-badge" class="font-mono text-emerald-600 dark:text-emerald-400">实测重排位移：Δwidth = 0px · Δheight = 0px</span>
        </div>
        <div class="flex flex-wrap items-center gap-4">
          <label class="flex items-center gap-2">
            <span class="text-[var(--muted-foreground)]">正文字号:</span>
            <input id="chat-sz" type="range" min="12" max="20" value="16" class="accent-[var(--primary)]" />
            <span id="chat-sz-lbl" class="font-mono w-10">16 px</span>
          </label>
          <label class="flex items-center gap-2">
            <span class="text-[var(--muted-foreground)]">行高:</span>
            <input id="chat-lh" type="range" min="130" max="170" value="150" class="accent-[var(--primary)]" />
            <span id="chat-lh-lbl" class="font-mono w-8">1.50</span>
          </label>
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <!-- Light Phone Card -->
        <div class="paper-light rounded-2xl border p-5 space-y-3">
          <div class="text-xs opacity-60 font-mono flex justify-between">
            <span>LIGHT MODE · Personal Agent</span>
            <span class="role-caption">Agent: Serif · User: Sans</span>
          </div>
          <div id="probe-u-bubble" class="bubble-u-light role-user adm-sans ml-auto max-w-[85%] w-fit rounded-2xl rounded-br-sm px-4 py-2.5 chat-txt" style="font-size:16px;line-height:1.5">
            ↩ Summarize <strong>Q3 European revenue</strong> in <em>Letters of Credit</em> &amp; check flight <strong>CX801</strong> (#I1l-O08) for Søren in Zürich.
          </div>
          <div id="probe-a-bubble" class="bubble-a-light role-agent adm-serif max-w-[92%] rounded-2xl rounded-bl-sm px-4 py-3 chat-txt space-y-2" style="font-size:16px;line-height:1.5">
            <div>Q3 net revenue reached <strong>$1,480,920.50</strong> (+14.2% YoY) across Zürich, München, and København — verified in <em>The Elements of Typographic Style</em> with <strong>28.5%</strong> operating margin.</div>
            <div>Flight <strong>CX801</strong> (<code class="adm-mono text-[0.92em] px-1.5 py-0.5 rounded bg-black/5">ID-1lI-O08</code>) departs at <strong>09:30</strong> from Gate B14 · <strong><em>Voix ambiguë d’un cœur</em></strong> ↗</div>
            <pre class="adm-mono text-[13px] leading-relaxed p-3 rounded-xl bg-[#161920] text-[#e6eaf2] overflow-x-auto" style="font-feature-settings:'ss01' 1,'zero' 1"><em class="text-[#8b9bb4]">// src/billing/invoice.ts (Admiralty Mono · Reg/Med/Bold/Italic · ss01=1)</em>
<strong class="font-bold">const</strong> <span class="font-medium">ok</span> = rate != 0.00 &amp;&amp; rate &lt;= 0.25 ? rate -&gt; calc(1480.95) : 0;</pre>
            <div class="flex flex-wrap gap-1.5 pt-1 text-xs adm-sans">
              <span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-md border border-[var(--border)] bg-[var(--background)] font-medium"><span class="adm-symbols font-medium">&#xE007;</span> Copy</span>
              <span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-md border border-[var(--border)] bg-[var(--background)] font-medium"><span class="adm-symbols font-medium">&#xE00B;</span> Regenerate</span>
              <span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-md border border-[var(--border)] bg-[var(--background)] font-medium"><span class="adm-symbols font-medium">&#xE071;</span> Share</span>
              <span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-md border border-[var(--border)] bg-[var(--background)] font-bold"><span class="adm-symbols font-bold">&#xE0D4;</span> Pinned</span>
            </div>
          </div>
          <div class="bubble-u-light role-user adm-sans ml-auto max-w-[85%] w-fit rounded-2xl rounded-br-sm px-4 py-2.5 chat-txt" style="font-size:16px;line-height:1.5">
            Convert <strong>$1,480,920.50</strong> to EUR at 0.92 and pin to <strong><em>Q3 Board</em></strong> →
          </div>
          <div class="bubble-a-light role-agent adm-serif max-w-[92%] rounded-2xl rounded-bl-sm px-4 py-2.5 chat-txt" style="font-size:16px;line-height:1.5">
            <strong>Pinned to <em>Q3 Board</em></strong> ↗ — €1,362,446.86 at 0.9200 EUR/USD (Section §4.2 · © 2026).
          </div>
        </div>

        <!-- Dark Phone Card -->
        <div class="paper-dark rounded-2xl border p-5 space-y-3">
          <div class="text-xs opacity-60 font-mono flex justify-between">
            <span>DARK MODE · Personal Agent</span>
            <span class="role-caption">Agent: Serif · User: Sans</span>
          </div>
          <div class="bubble-u-dark role-user adm-sans ml-auto max-w-[85%] w-fit rounded-2xl rounded-br-sm px-4 py-2.5 chat-txt" style="font-size:16px;line-height:1.5">
            ↩ Summarize <strong>Q3 European revenue</strong> in <em>Letters of Credit</em> &amp; check flight <strong>CX801</strong> (#I1l-O08) for Søren in Zürich.
          </div>
          <div class="bubble-a-dark role-agent adm-serif max-w-[92%] rounded-2xl rounded-bl-sm px-4 py-3 chat-txt space-y-2" style="font-size:16px;line-height:1.5">
            <div>Q3 net revenue reached <strong>$1,480,920.50</strong> (+14.2% YoY) across Zürich, München, and København — verified in <em>The Elements of Typographic Style</em> with <strong>28.5%</strong> operating margin.</div>
            <div>Flight <strong>CX801</strong> (<code class="adm-mono text-[0.92em] px-1.5 py-0.5 rounded bg-black/5">ID-1lI-O08</code>) departs at <strong>09:30</strong> from Gate B14 · <strong><em>Voix ambiguë d’un cœur</em></strong> ↗</div>
            <pre class="adm-mono text-[13px] leading-relaxed p-3 rounded-xl bg-[#161920] text-[#e6eaf2] overflow-x-auto" style="font-feature-settings:'ss01' 1,'zero' 1"><em class="text-[#8b9bb4]">// src/billing/invoice.ts (Admiralty Mono · Reg/Med/Bold/Italic · ss01=1)</em>
<strong class="font-bold">const</strong> <span class="font-medium">ok</span> = rate != 0.00 &amp;&amp; rate &lt;= 0.25 ? rate -&gt; calc(1480.95) : 0;</pre>
            <div class="flex flex-wrap gap-1.5 pt-1 text-xs adm-sans">
              <span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-md border border-[#343c4a] bg-[#222732] font-medium"><span class="adm-symbols font-medium">&#xE007;</span> Copy</span>
              <span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-md border border-[#343c4a] bg-[#222732] font-medium"><span class="adm-symbols font-medium">&#xE00B;</span> Regenerate</span>
              <span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-md border border-[#343c4a] bg-[#222732] font-medium"><span class="adm-symbols font-medium">&#xE071;</span> Share</span>
              <span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-md border border-[#343c4a] bg-[#222732] font-bold"><span class="adm-symbols font-bold">&#xE0D4;</span> Pinned</span>
            </div>
          </div>
          <div class="bubble-u-dark role-user adm-sans ml-auto max-w-[85%] w-fit rounded-2xl rounded-br-sm px-4 py-2.5 chat-txt" style="font-size:16px;line-height:1.5">
            Convert <strong>$1,480,920.50</strong> to EUR at 0.92 and pin to <strong><em>Q3 Board</em></strong> →
          </div>
          <div class="bubble-a-dark role-agent adm-serif max-w-[92%] rounded-2xl rounded-bl-sm px-4 py-2.5 chat-txt" style="font-size:16px;line-height:1.5">
            <strong>Pinned to <em>Q3 Board</em></strong> ↗ — €1,362,446.86 at 0.9200 EUR/USD (Section §4.2 · © 2026).
          </div>
        </div>
      </div>

      <div class="bg-[var(--card)] border border-[var(--border)] rounded-xl p-4 space-y-2">
        <div class="flex items-center justify-between gap-2 text-xs pb-2 border-b border-[var(--card-border)]">
          <span class="text-[var(--muted-foreground)]">多字号瀑布流 (12 / 14 / 16 / 18 / 24 / 32 px) — 跟随顶部当前选中家族：</span>
          <input id="wf-input" type="text" value="Admiralty Personal Agent — Il1 O0 rn/m · $1,480.95 · Voix ambiguë d’un cœur ↩" class="px-2.5 py-1 rounded border border-[var(--border)] bg-[var(--background)] w-96 text-xs outline-none" />
        </div>
        <div id="wf-rows" class="divide-y divide-[var(--card-border)]"></div>
      </div>
    </section>

    <!-- TAB 5: ADMIRALTY SYMBOLS PHASE 1 (218 ICONS) -->
    <section id="panel-symbols" class="tab-panel hidden space-y-4">
      <div class="bg-[var(--card)] border border-[var(--border)] rounded-xl p-4 space-y-3 text-xs">
        <div class="flex flex-wrap items-center justify-between gap-3">
          <div class="flex flex-wrap items-center gap-2">
            <input id="sym-search" type="text" placeholder="搜索图标名、标签或 U+E0xx..." class="px-2.5 py-1.5 rounded-lg border border-[var(--border)] bg-[var(--background)] w-60 outline-none" />
            <div class="flex gap-1 bg-[var(--background)] p-1 rounded-lg border border-[var(--border)]" id="sym-sz-bar">
              <button data-sz="14" class="sym-sz-btn px-2 py-1 rounded text-[var(--muted-foreground)]">14px</button>
              <button data-sz="20" class="sym-sz-btn px-2 py-1 rounded bg-[var(--primary)] text-[var(--primary-foreground)]">20px</button>
              <button data-sz="28" class="sym-sz-btn px-2 py-1 rounded text-[var(--muted-foreground)]">28px</button>
            </div>
            <label class="inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg border border-[var(--border)] bg-[var(--background)] cursor-pointer font-mono">
              <input type="checkbox" id="sym-rtl" class="accent-[var(--primary)]" />
              <span>RTL Mirror (rtlm)</span>
            </label>
          </div>
          <div id="sym-count-lbl" class="font-mono text-[var(--muted-foreground)]">显示 __SYMBOL_COUNT__ / __SYMBOL_COUNT__ 个 24×24 原创图标 (U+E000..__LAST_PUA__)</div>
        </div>

        <div id="sym-cat-bar" class="flex flex-wrap gap-1 pt-2 border-t border-[var(--card-border)]"></div>

        <div class="pt-2 border-t border-[var(--card-border)] flex flex-wrap items-center gap-2">
          <span class="text-[var(--muted-foreground)] mr-1">按钮图文 Cap-Centering 预览：</span>
          <span id="sym-btn-bar" class="flex flex-wrap items-center gap-2"></span>
        </div>
      </div>

      <div id="sym-grid" class="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-6 lg:grid-cols-8 gap-2"></div>
    </section>

    <!-- TAB 6: METRICS & KERNING SPECS -->
    <section id="panel-specs" class="tab-panel hidden space-y-4">
      <div class="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
        <div class="bg-[var(--card)] border border-[var(--border)] rounded-xl p-3.5">
          <div class="text-[var(--muted-foreground)]">UPM / x-Height / Cap</div>
          <div class="font-mono text-base font-semibold mt-1">1000 / 520 / 700</div>
          <div class="text-[var(--muted-foreground)] mt-1">Ascender 740 · Descender -220</div>
        </div>
        <div class="bg-[var(--card)] border border-[var(--border)] rounded-xl p-3.5">
          <div class="text-[var(--muted-foreground)]">跨平台垂直度量 (GF 130%)</div>
          <div class="font-mono text-base font-semibold mt-1">+980 / -320 / 0</div>
          <div class="text-[var(--muted-foreground)] mt-1">Sans = Serif = Mono 严格统一</div>
        </div>
        <div class="bg-[var(--card)] border border-[var(--border)] rounded-xl p-3.5">
          <div class="text-[var(--muted-foreground)]">衬线对比度 (Serif Regular)</div>
          <div class="font-mono text-base font-semibold mt-1">竖 92u / 横 40u (2.3:1)</div>
          <div class="text-[var(--muted-foreground)] mt-1">大写 102/44u · 双层 g · 梨形滴珠</div>
        </div>
        <div class="bg-[var(--card)] border border-[var(--border)] rounded-xl p-3.5">
          <div class="text-[var(--muted-foreground)]">共享 OpenType 特性与字距</div>
          <div class="font-mono text-base font-semibold mt-1">ccmp locl tnum zero case</div>
          <div id="kern-count-lbl" class="text-[var(--muted-foreground)] mt-1">163 组共享 Class Kerning</div>
        </div>
      </div>

      <div class="bg-[var(--card)] border border-[var(--border)] rounded-xl p-4 space-y-3">
        <div class="flex items-center justify-between text-xs">
          <span class="font-medium text-[var(--muted-foreground)]">Sans &amp; Serif 1:1 共享 Class Kerning 检视（点击任意对进入显微镜查看）：</span>
          <input id="kern-filter" type="text" placeholder="筛选字符 (如 A, T, V)..." class="px-2 py-1 rounded border border-[var(--border)] bg-[var(--background)] text-xs w-44 outline-none" />
        </div>
        <div id="kern-grid" class="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-6 lg:grid-cols-8 gap-2 max-h-[380px] overflow-y-auto pr-1"></div>
      </div>
    </section>
  </div>

  <script>
    const PAYLOAD = __PAYLOAD_JSON__;

    document.getElementById('admiralty-font-face').textContent = Object.values(PAYLOAD.vfWoff2).map(vf => `
      @font-face {
        font-family: '${vf.family}';
        src: url('data:font/woff2;base64,${vf.woff2}') format('woff2');
        font-weight: 400 700;
        font-style: ${vf.style};
      }`).join('\\n');

    function parseSvgPath(d) {
      if (!d) return { contours: [], nodes: [], handles: [], bbox: null };
      const tokens = d.match(/[MLHVCZ]|-?\\d+(?:\\.\\d+)?/g) || [];
      let i = 0, cx = 0, cy = 0, sx = 0, sy = 0, cmd = '';
      const contours = [];
      let curNodes = [];
      const handles = [];
      let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
      const touch = (x, y) => {
        if (x < minX) minX = x; if (x > maxX) maxX = x;
        if (y < minY) minY = y; if (y > maxY) maxY = y;
      };

      while (i < tokens.length) {
        const t = tokens[i];
        if (/^[MLHVCZ]$/.test(t)) { cmd = t; i++; }
        if (cmd === 'M') {
          cx = +tokens[i++]; cy = +tokens[i++];
          sx = cx; sy = cy;
          curNodes = [{ x: cx, y: cy, curve: false }];
          touch(cx, cy);
          cmd = 'L';
        } else if (cmd === 'L') {
          cx = +tokens[i++]; cy = +tokens[i++];
          curNodes.push({ x: cx, y: cy, curve: false });
          touch(cx, cy);
        } else if (cmd === 'H') {
          cx = +tokens[i++];
          curNodes.push({ x: cx, y: cy, curve: false });
          touch(cx, cy);
        } else if (cmd === 'V') {
          cy = +tokens[i++];
          curNodes.push({ x: cx, y: cy, curve: false });
          touch(cx, cy);
        } else if (cmd === 'C') {
          const x1 = +tokens[i++], y1 = +tokens[i++];
          const x2 = +tokens[i++], y2 = +tokens[i++];
          const nx = +tokens[i++], ny = +tokens[i++];
          handles.push({ ax: cx, ay: cy, hx: x1, hy: y1 });
          handles.push({ ax: nx, ay: ny, hx: x2, hy: y2 });
          if (curNodes.length) curNodes[curNodes.length - 1].curveOut = true;
          curNodes.push({ x: nx, y: ny, curve: true });
          cx = nx; cy = ny;
          touch(x1, y1); touch(x2, y2); touch(nx, ny);
        } else if (cmd === 'Z') {
          if (curNodes.length > 1) {
            const first = curNodes[0], last = curNodes[curNodes.length - 1];
            if (first.x === last.x && first.y === last.y) {
              first.curve = first.curve || last.curve;
              curNodes.pop();
            }
          }
          contours.push(curNodes);
          curNodes = [];
          cx = sx; cy = sy;
          cmd = '';
        }
      }
      const nodes = contours.flat();
      return {
        contours,
        nodes,
        handles,
        bbox: minX === Infinity ? null : [minX, minY, maxX, maxY]
      };
    }

    function buildGlyphList(rawList) {
      return rawList.map(([name, cp, width, d], idx) => {
        let cat = 'punct';
        if (name === '.notdef' || name.includes('.')) cat = 'feat';
        else if (cp >= 65 && cp <= 90) cat = 'upper';
        else if (cp >= 97 && cp <= 122) cat = 'lower';
        else if (cp >= 48 && cp <= 57) cat = 'figs';
        const ch = cp > 0 ? String.fromCodePoint(cp) : '';
        return { idx, name, cp, ch, width, d, cat, parsed: parseSvgPath(d) };
      });
    }

    const STYLE_LABELS = {
      '400': 'Regular (400)',
      '500': 'Medium (500)',
      '700': 'Bold (700)',
      '400i': 'Italic (400)',
      '500i': 'Medium Italic (500)',
      '700i': 'Bold Italic (700)',
    };

    function buildFamilyWeights(famKey, labelBase, stack) {
      const weights = {};
      Object.keys(PAYLOAD.families[famKey]).forEach(w => {
        const glyphs = buildGlyphList(PAYLOAD.families[famKey][w].glyphs);
        weights[w] = {
          label: `${labelBase} ${STYLE_LABELS[w] || w}`,
          glyphs,
          byName: Object.fromEntries(glyphs.map(g => [g.name, g])),
        };
      });
      return { stack, weights };
    }

    const FAMILIES = {
      serif: buildFamilyWeights('serif', 'Admiralty Serif', "'Admiralty Serif', 'Noto Serif CJK TC', 'Songti TC', Georgia, serif"),
      sans: buildFamilyWeights('sans', 'Admiralty Sans', "'Admiralty Sans', 'PingFang HK', 'PingFang TC', 'Noto Sans CJK TC', -apple-system, sans-serif"),
      mono: buildFamilyWeights('mono', 'Admiralty Mono (600u)', "'Admiralty Mono', 'PingFang HK', ui-monospace, monospace"),
      symbols: buildFamilyWeights('symbols', 'Admiralty Symbols (24x24)', "'Admiralty Symbols', sans-serif"),
    };

    let activeFam = 'serif';
    let activeWeight = '400';
    let activeStyle = 'normal';
    let curGlyphName = 'g';
    let lastRenderedMasterKey = '';
    let lastRenderedGlyphName = '';

    function nearestMasterWeight(w) {
      const n = +w;
      return n < 450 ? '400' : (n < 600 ? '500' : '700');
    }

    function activeStoreKey() {
      const m = nearestMasterWeight(activeWeight);
      return (activeStyle === 'italic' && activeFam !== 'symbols') ? (m + 'i') : m;
    }

    function activeGlyphStore() {
      return FAMILIES[activeFam].weights[activeStoreKey()];
    }

    function updateHeaderAndControls() {
      const mKey = activeStoreKey();
      const store = FAMILIES[activeFam].weights[mKey];
      const effStyle = activeFam === 'symbols' ? 'normal' : activeStyle;
      document.documentElement.style.setProperty('--adm-active-stack', FAMILIES[activeFam].stack);
      document.documentElement.style.setProperty('--adm-active-weight', activeWeight);
      document.documentElement.style.setProperty('--adm-active-style', effStyle);
      document.getElementById('inp-vf-wght').value = activeWeight;
      document.getElementById('lbl-vf-wght').textContent = activeWeight;
      const isMaster = activeWeight === '400' || activeWeight === '500' || activeWeight === '700';
      document.getElementById('hdr-family-title').textContent = isMaster
        ? store.label
        : `${store.label.split(' ')[0]} ${store.label.split(' ')[1]} (wght ${activeWeight} · Nearest: ${nearestMasterWeight(activeWeight)})`;
      document.querySelectorAll('.fam-btn').forEach(b => {
        const on = b.dataset.fam === activeFam;
        b.className = 'fam-btn px-2.5 py-1.5 rounded-md font-medium ' + (on
          ? 'bg-[var(--primary)] text-[var(--primary-foreground)]'
          : 'text-[var(--muted-foreground)]');
      });
      document.querySelectorAll('.wgt-btn').forEach(b => {
        const on = b.dataset.wgt === activeWeight;
        b.className = 'wgt-btn px-2.5 py-1.5 rounded-md font-medium ' + (on
          ? 'bg-[var(--primary)] text-[var(--primary-foreground)]'
          : 'text-[var(--muted-foreground)]');
      });
      document.getElementById('sln-bar').classList.toggle('opacity-50', activeFam === 'symbols');
      document.querySelectorAll('.sln-btn').forEach(b => {
        const on = b.dataset.sln === activeStyle;
        b.className = 'sln-btn px-2.5 py-1.5 rounded-md font-medium ' + (on
          ? 'bg-[var(--primary)] text-[var(--primary-foreground)]'
          : 'text-[var(--muted-foreground)]');
      });
      if (!store.byName[curGlyphName]) {
        curGlyphName = store.glyphs[2] ? store.glyphs[2].name : store.glyphs[0].name;
      }
      const fullKey = `${activeFam}:${mKey}:${effStyle}`;
      const masterChanged = fullKey !== lastRenderedMasterKey;
      if (masterChanged || curGlyphName !== lastRenderedGlyphName) {
        renderGlyphSelector();
        renderMicroscope();
      }
      if (masterChanged) {
        lastRenderedMasterKey = fullKey;
        renderKerning();
      }
      if (typeof renderSymbolsCatalog === 'function') renderSymbolsCatalog();
    }

    function setActiveFamily(fam) {
      activeFam = fam;
      updateHeaderAndControls();
    }

    function setActiveWeight(wgt) {
      activeWeight = String(wgt);
      updateHeaderAndControls();
    }

    function setActiveStyle(sln) {
      activeStyle = sln;
      updateHeaderAndControls();
    }

    document.querySelectorAll('.fam-btn').forEach(b => {
      b.addEventListener('click', () => setActiveFamily(b.dataset.fam));
    });
    document.querySelectorAll('.wgt-btn').forEach(b => {
      b.addEventListener('click', () => setActiveWeight(b.dataset.wgt));
    });
    document.getElementById('inp-vf-wght').addEventListener('input', e => {
      setActiveWeight(e.target.value);
    });
    document.querySelectorAll('.sln-btn').forEach(b => {
      b.addEventListener('click', () => setActiveStyle(b.dataset.sln));
    });

    // Tab Switching
    document.querySelectorAll('.tab-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const target = btn.dataset.tab;
        document.querySelectorAll('.tab-btn').forEach(b => {
          const active = b === btn;
          b.className = 'tab-btn px-3 py-1.5 rounded-md font-medium ' + (active
            ? 'bg-[var(--primary)] text-[var(--primary-foreground)]'
            : 'text-[var(--muted-foreground)]');
        });
        document.querySelectorAll('.tab-panel').forEach(p => {
          p.classList.toggle('hidden', p.id !== 'panel-' + target);
        });
      });
    });

    // ---------------- TAB 1: LIVE TYPE TESTER ----------------
    const featState = { kern: true, pnum: true, tnum: false, zero: false, case: false, ss01: false };
    const editor = document.getElementById('tester-editor');
    const surface = document.getElementById('tester-surface');

    function syncTesterStyles() {
      const sz = document.getElementById('inp-size').value;
      const lh = (document.getElementById('inp-lh').value / 100).toFixed(2);
      const tr = (document.getElementById('inp-tr').value / 1000).toFixed(3);
      document.getElementById('lbl-size').textContent = sz + ' px';
      document.getElementById('lbl-lh').textContent = lh;
      document.getElementById('lbl-tr').textContent = tr + ' em';

      const fparts = Object.entries(featState).map(([k, v]) => `"${k}" ${v ? 1 : 0}`);
      const fcss = fparts.join(', ');
      editor.style.fontSize = sz + 'px';
      editor.style.lineHeight = lh;
      editor.style.letterSpacing = tr + 'em';
      editor.style.fontFeatureSettings = fcss;
      document.getElementById('tester-css-readout').textContent = 'font-feature-settings: ' + fcss;
    }

    ['inp-size', 'inp-lh', 'inp-tr'].forEach(id => {
      document.getElementById(id).addEventListener('input', syncTesterStyles);
    });
    document.querySelectorAll('.sz-preset').forEach(b => {
      b.addEventListener('click', () => {
        document.getElementById('inp-size').value = b.dataset.sz;
        syncTesterStyles();
      });
    });
    document.querySelectorAll('.feat-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const f = btn.dataset.feat;
        featState[f] = !featState[f];
        btn.className = 'feat-btn px-2.5 py-1 rounded-md border font-mono ' + (featState[f]
          ? 'border-[var(--primary)] bg-[var(--primary)] text-[var(--primary-foreground)]'
          : 'border-[var(--border)] text-[var(--muted-foreground)]');
        syncTesterStyles();
      });
    });
    document.querySelectorAll('.paper-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const mode = btn.dataset.paper;
        document.querySelectorAll('.paper-btn').forEach(b => {
          b.className = 'paper-btn px-2 py-1 rounded border ' + (b === btn
            ? 'border-[var(--primary)] font-medium'
            : 'border-[var(--border)] text-[var(--muted-foreground)]');
        });
        surface.className = 'rounded-xl border p-6 transition-colors ' + (
          mode === 'light' ? 'paper-light' :
          mode === 'dark'  ? 'paper-dark' :
          'border-[var(--border)] bg-[var(--card)]'
        );
      });
    });

    const PRESETS = {
      hero: { sz: 38, lh: 138, text: 'Calm, literary clarity for your Personal Agent.\\nABCDEFGHIJKLMNOPQRSTUVWXYZ\\nabcdefghijklmnopqrstuvwxyz\\n0123456789   $1,480.95   €290   £75   ¥3,600   ₹990   ₩12,000   ₽500' },
      disambig: { sz: 34, lh: 145, text: 'Il1|   O0o   rn m   cl d   fi fl fj   fV fW fY qj gj   2011 / 1,111\\nID: A1-I0-l9   CX801   ‘Single’  “Double”  `grave`  \\\'ascii\\\'  \"str\"\\n[ADMIRALTY — CASE: (2026)]   {a + b = c}' },
      euro: { sz: 28, lh: 150, text: 'nǐ hǎo · lǚshī · Nǚ’ér · ǖ ǘ ǚ ǜ · Ǖ Ǘ Ǚ Ǜ · ǟ Ä́\\nÆther & Œuvre · Voix ambiguë d’un cœur · STRASSE -> STRAẞE · Ĳĳ ĸ Ŀŀ ŉ Ŧŧ ſ\\nZażółć gęślą jaźń · Příliš žluťoučký kůň úpěl ďábelské ódy · ð Þþ Ŋŋ\\n≈ ∞ √ π ∆ Ω ↔ ⇒ ✓ ✗ ‰ ′ ″ № · §4.2 · © 2026 · ← ↑ → ↓ ↩' },
      prose: { sz: 18, lh: 155, text: 'In a personal agent conversation, typography can quietly distinguish two speakers without colorful badges or clutter: Admiralty Serif gives the assistant a calm, literary, trustworthy voice, while Admiralty Sans keeps the user’s prompts crisp and immediate.\\n\\nBecause both families are built on the exact same humanist skeleton, identical 1000-UPM vertical metrics (+980 / -320 / 0), and 1:1 duplexed glyph advance widths, switching any message or role between Sans and Serif produces zero layout shift — not even a single pixel of line-wrap reflow.' },
      table: { sz: 22, lh: 155, tnum: true, pnum: false, text: 'Q1 Revenue     $1,111.10     +14.2%\\nQ2 Revenue     $8,490.05     -08.0%\\nQ3 Forecast    $9,024.80     +26.5%\\nTotal Net     $18,625.95     +10.9%' },
      code80: { fam: 'mono', sz: 16, lh: 155, ss01: true, text: '12345678901234567890123456789012345678901234567890123456789012345678901234567890\\nexport const check = (id = \\\'ID-1lI-O08\\\', x = 0) => x != 0 && x <= 99 ? x -> 1 : 0;\\n// Il1| O0o ,.:; \\\'\"` {[(<>)]}  |  a -> b  x <- y  fn => x == 0  x != y  a <= b >= c' },
      cjk: { sz: 20, lh: 158, text: 'Admiralty 你好 Hello 世界 2026 · Pinyin: nǐ hǎo lǚshī ǖǘǚǜ\\n在香港金鐘站（Admiralty Station）轉乘快線，09:30 a.m. 準時出發。\\nAdmiralty Serif 與宋體 / 明體搭配書卷溫潤；Admiralty Sans 與蘋方 / 思源黑體乾淨現代。' }
    };

    document.querySelectorAll('.preset-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const p = PRESETS[btn.dataset.preset];
        if (p.fam) setActiveFamily(p.fam);
        document.getElementById('inp-size').value = p.sz;
        document.getElementById('inp-lh').value = p.lh;
        ['tnum', 'pnum', 'ss01'].forEach(fk => {
          if (p[fk] !== undefined) {
            featState[fk] = p[fk];
            const tb = document.querySelector(`[data-feat="${fk}"]`);
            if (tb) tb.className = 'feat-btn px-2.5 py-1 rounded-md border font-mono ' + (featState[fk]
              ? 'border-[var(--primary)] bg-[var(--primary)] text-[var(--primary-foreground)]'
              : 'border-[var(--border)] text-[var(--muted-foreground)]');
          }
        });
        editor.textContent = p.text;
        syncTesterStyles();
      });
    });

    // ---------------- TAB 2: GLYPH MICROSCOPE ----------------
    let curCat = 'all';

    function renderGlyphSelector() {
      const q = document.getElementById('glyph-search').value.trim().toLowerCase();
      const grid = document.getElementById('glyph-grid');
      grid.innerHTML = '';
      const list = activeGlyphStore().glyphs;
      list.forEach(g => {
        if (curCat !== 'all' && g.cat !== curCat && activeFam !== 'symbols') return;
        if (q && !g.name.toLowerCase().includes(q) && g.ch.toLowerCase() !== q) return;
        const btn = document.createElement('button');
        const sel = g.name === curGlyphName;
        btn.className = 'p-1.5 rounded-lg border text-center transition-colors flex flex-col items-center justify-center h-14 ' + (sel
          ? 'border-[var(--primary)] bg-[var(--primary)] text-[var(--primary-foreground)]'
          : 'border-[var(--border)] bg-[var(--background)]');
        btn.innerHTML = `
          <svg viewBox="-60 -780 780 1040" class="w-7 h-7 fill-current">
            <g transform="scale(1,-1)"><path d="${g.d}" /></g>
          </svg>
          <span class="text-[10px] font-mono truncate max-w-full opacity-75">${g.name}</span>
        `;
        btn.addEventListener('click', () => { curGlyphName = g.name; renderGlyphSelector(); renderMicroscope(); });
        grid.appendChild(btn);
      });
    }

    document.querySelectorAll('.cat-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        curCat = btn.dataset.cat;
        document.querySelectorAll('.cat-btn').forEach(b => {
          b.className = 'cat-btn px-2 py-1 rounded ' + (b === btn
            ? 'bg-[var(--primary)] text-[var(--primary-foreground)]'
            : 'text-[var(--muted-foreground)]');
        });
        renderGlyphSelector();
      });
    });
    document.getElementById('glyph-search').addEventListener('input', renderGlyphSelector);

    function renderMicroscope() {
      const store = activeGlyphStore();
      const g = store.byName[curGlyphName] || store.glyphs[2];
      lastRenderedGlyphName = g.name;
      const curKey = activeStoreKey();
      const masterW = nearestMasterWeight(activeWeight);
      const ghostFam = activeFam === 'serif' ? 'sans' : activeFam === 'sans' ? 'serif' : activeFam;
      let ghostKey = curKey;
      if (activeFam === 'mono') {
        ghostKey = activeStyle === 'italic' ? masterW : (masterW === '400' ? '700' : '400');
      } else if (activeFam === 'symbols') {
        ghostKey = masterW === '400' ? '700' : '400';
      }
      const ghostG = FAMILIES[ghostFam].weights[ghostKey].byName[g.name];

      const showGhost = document.getElementById('chk-ghost').checked;
      const showFill = document.getElementById('chk-fill').checked;
      const showOutline = document.getElementById('chk-outline').checked;
      const showNodes = document.getElementById('chk-nodes').checked;
      const showMetrics = document.getElementById('chk-metrics').checked;

      document.getElementById('mic-title').textContent = g.name + (g.ch ? ` (“${g.ch}”)` : '');
      document.getElementById('mic-uni').textContent = g.cp > 0
        ? 'U+' + g.cp.toString(16).toUpperCase().padStart(4, '0')
        : 'OpenType / Combining Glyph';

      const bb = g.parsed.bbox;
      const lsb = bb ? bb[0] : 0;
      const rsb = bb ? (g.width - bb[2]) : g.width;
      document.getElementById('st-width').textContent = g.width + ' u';
      document.getElementById('st-lsb').textContent = bb ? lsb + ' u' : '—';
      document.getElementById('st-rsb').textContent = bb ? rsb + ' u' : '—';
      document.getElementById('st-bbox').textContent = bb ? `${bb[0]}..${bb[2]}, ${bb[1]}..${bb[3]}` : 'empty';
      document.getElementById('st-contours').textContent = g.parsed.contours.length;
      document.getElementById('st-pts').textContent = `${g.parsed.nodes.length} / ${g.parsed.handles.length}`;

      const svg = document.getElementById('mic-svg');
      const cxOffset = Math.round((800 - g.width) / 2);
      let html = `<g transform="translate(${cxOffset}, 0)">`;

      if (showMetrics) {
        const mlines = [
          [740, 'Asc 740', '0.35'],
          [700, 'Cap 700', '0.45'],
          [520, 'x-h 520', '0.55'],
          [0, 'Base 0', '0.75'],
          [-220, 'Desc -220', '0.35']
        ];
        mlines.forEach(([y, label, op]) => {
          html += `<line x1="-180" y1="${-y}" x2="${g.width + 180}" y2="${-y}" stroke="currentColor" stroke-opacity="${op}" stroke-width="2" stroke-dasharray="${y === 0 ? '' : '6 5'}" />`;
          html += `<text x="${g.width + 95}" y="${-y + 8}" fill="currentColor" fill-opacity="0.55" font-size="22" font-family="monospace">${label}</text>`;
        });
        html += `<line x1="0" y1="-820" x2="0" y2="290" stroke="var(--primary)" stroke-opacity="0.65" stroke-width="2.5" />`;
        html += `<line x1="${g.width}" y1="-820" x2="${g.width}" y2="290" stroke="var(--primary)" stroke-opacity="0.65" stroke-width="2.5" />`;
        html += `<text x="6" y="275" fill="currentColor" fill-opacity="0.6" font-size="22" font-family="monospace">0</text>`;
        html += `<text x="${g.width + 6}" y="275" fill="currentColor" fill-opacity="0.6" font-size="22" font-family="monospace">w=${g.width}</text>`;
      }

      html += `<g transform="scale(1, -1)">`;
      if (showGhost && ghostG && ghostG.d) {
        html += `<path d="${ghostG.d}" fill="#0ea5e9" fill-opacity="0.24" stroke="#0284c7" stroke-opacity="0.55" stroke-width="2.5" />`;
      }
      if (g.d) {
        html += `<path d="${g.d}" fill="${showFill ? 'currentColor' : 'none'}" fill-opacity="${showOutline ? '0.18' : '0.86'}" stroke="${showOutline ? 'currentColor' : 'none'}" stroke-width="3.5" />`;
      }
      if (showNodes) {
        g.parsed.handles.forEach(h => {
          html += `<line x1="${h.ax}" y1="${h.ay}" x2="${h.hx}" y2="${h.hy}" stroke="var(--muted-foreground)" stroke-width="2" />`;
          html += `<circle cx="${h.hx}" cy="${h.hy}" r="6.5" fill="var(--background)" stroke="var(--muted-foreground)" stroke-width="2.5" />`;
        });
        g.parsed.nodes.forEach(n => {
          if (n.curve || n.curveOut) {
            html += `<circle cx="${n.x}" cy="${n.y}" r="8" fill="var(--primary)" />`;
          } else {
            html += `<rect x="${n.x - 7.5}" y="${n.y - 7.5}" width="15" height="15" fill="var(--foreground)" />`;
          }
        });
      }
      html += `</g></g>`;
      svg.innerHTML = html;

      const ctx = document.getElementById('mic-context');
      const dispChar = g.ch || (g.name.startsWith('zero') ? '0' : g.name.startsWith('one') ? '1' : 'A');
      const featCss = g.name.includes('slash') ? "'zero' 1" : g.name.includes('tnum') ? "'tnum' 1" : g.name.includes('case') ? "'case' 1" : "'kern' 1";
      const sample = g.cat === 'upper' ? `HH${dispChar}HOO` : g.cat === 'figs' ? `00${dispChar}1188` : `nn${dispChar}noo`;
      const effStyle = activeFam === 'symbols' ? 'normal' : activeStyle;
      ctx.innerHTML = [14, 18, 30].map(s => `
        <div class="space-y-0.5">
          <div class="adm-sans opacity-65" style="font-size:${s}px;font-weight:${activeWeight};font-style:${effStyle};font-feature-settings:${featCss}"><span class="text-[10px] font-mono mr-1">Sans ${s}</span>${sample}</div>
          <div class="adm-serif" style="font-size:${s}px;font-weight:${activeWeight};font-style:${effStyle};font-feature-settings:${featCss}"><span class="text-[10px] font-mono mr-1">Serif ${s}</span>${sample}</div>
        </div>
      `).join('');
    }

    ['chk-ghost', 'chk-fill', 'chk-outline', 'chk-nodes', 'chk-metrics'].forEach(id => {
      document.getElementById(id).addEventListener('change', renderMicroscope);
    });

    const micSvg = document.getElementById('mic-svg');
    micSvg.addEventListener('mousemove', e => {
      const store = activeGlyphStore();
      const g = store.byName[curGlyphName] || store.glyphs[2];
      const pt = micSvg.createSVGPoint();
      pt.x = e.clientX; pt.y = e.clientY;
      const svgP = pt.matrixTransform(micSvg.getScreenCTM().inverse());
      const cxOffset = Math.round((800 - g.width) / 2);
      const ux = Math.round(svgP.x - cxOffset);
      const uy = Math.round(-svgP.y);
      document.getElementById('mic-coords').textContent = `UPM (x: ${ux}, y: ${uy})`;
    });

    // ---------------- TAB 3: WALTER TRACY RHYTHM ----------------
    function renderTracy(upper) {
      const out = document.getElementById('wt-output');
      const chars = upper ? 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' : 'abcdefghijklmnopqrstuvwxyz';
      out.innerHTML = [...chars].map(c =>
        `<div class="px-2 py-1 rounded bg-[var(--background)] border border-[var(--border)] text-center">${upper ? `HH${c}HOO` : `nn${c}noo`}</div>`
      ).join('');
      document.getElementById('wt-lc').className = 'px-2 py-1 rounded ' + (!upper ? 'bg-[var(--primary)] text-[var(--primary-foreground)]' : 'border border-[var(--border)] text-[var(--muted-foreground)]');
      document.getElementById('wt-uc').className = 'px-2 py-1 rounded ' + (upper ? 'bg-[var(--primary)] text-[var(--primary-foreground)]' : 'border border-[var(--border)] text-[var(--muted-foreground)]');
    }
    document.getElementById('wt-lc').addEventListener('click', () => renderTracy(false));
    document.getElementById('wt-uc').addEventListener('click', () => renderTracy(true));

    // ---------------- TAB 4: CHAT & ROLE SWAP ----------------
    let rolesSwapped = false;
    document.getElementById('btn-swap-roles').addEventListener('click', () => {
      const uProbe = document.getElementById('probe-u-bubble');
      const aProbe = document.getElementById('probe-a-bubble');
      const wBefore = aProbe.offsetWidth, hBefore = aProbe.offsetHeight;
      const uwBefore = uProbe.offsetWidth, uhBefore = uProbe.offsetHeight;

      rolesSwapped = !rolesSwapped;
      document.querySelectorAll('.role-agent').forEach(el => {
        el.classList.toggle('adm-serif', !rolesSwapped);
        el.classList.toggle('adm-sans', rolesSwapped);
      });
      document.querySelectorAll('.role-user').forEach(el => {
        el.classList.toggle('adm-sans', !rolesSwapped);
        el.classList.toggle('adm-serif', rolesSwapped);
      });

      const wAfter = aProbe.offsetWidth, hAfter = aProbe.offsetHeight;
      const dw = Math.abs(wAfter - wBefore) + Math.abs(uProbe.offsetWidth - uwBefore);
      const dh = Math.abs(hAfter - hBefore) + Math.abs(uProbe.offsetHeight - uhBefore);

      const desc = rolesSwapped ? '已互换：Agent = Sans · User = Serif' : '当前默认：Agent = Serif · User = Sans';
      document.getElementById('role-status-badge').textContent = desc;
      document.querySelectorAll('.role-caption').forEach(el => {
        el.textContent = rolesSwapped ? 'Agent: Sans · User: Serif' : 'Agent: Serif · User: Sans';
      });
      document.getElementById('reflow-audit-badge').textContent = `实测重排位移：Δwidth = ${dw}px · Δheight = ${dh}px`;
    });

    function syncChat() {
      const sz = document.getElementById('chat-sz').value;
      const lh = (document.getElementById('chat-lh').value / 100).toFixed(2);
      document.getElementById('chat-sz-lbl').textContent = sz + ' px';
      document.getElementById('chat-lh-lbl').textContent = lh;
      document.querySelectorAll('.chat-txt').forEach(el => {
        el.style.fontSize = sz + 'px';
        el.style.lineHeight = lh;
      });
    }
    document.getElementById('chat-sz').addEventListener('input', syncChat);
    document.getElementById('chat-lh').addEventListener('input', syncChat);

    function renderWaterfall() {
      const txt = document.getElementById('wf-input').value;
      const rows = document.getElementById('wf-rows');
      rows.innerHTML = [12, 14, 16, 18, 24, 32].map(sz => `
        <div class="py-2.5 flex items-baseline gap-4">
          <span class="w-12 shrink-0 text-xs font-mono text-[var(--muted-foreground)]">${sz} px</span>
          <div class="adm-active truncate" style="font-size:${sz}px;line-height:1.45"></div>
        </div>
      `).join('');
      rows.querySelectorAll('.adm-active').forEach(el => { el.textContent = txt; });
    }
    document.getElementById('wf-input').addEventListener('input', renderWaterfall);

    // ---------------- TAB 5: SYMBOLS CATALOG (218 ICONS) ----------------
    let symCatFilter = 'all';
    let symSizePx = 20;
    const symCategories = ['all', ...new Set(PAYLOAD.symbolCatalog.map(s => s[2]))];
    const symCatBar = document.getElementById('sym-cat-bar');
    symCategories.forEach(cat => {
      const b = document.createElement('button');
      b.dataset.scat = cat;
      const cnt = cat === 'all' ? PAYLOAD.symbolCatalog.length : PAYLOAD.symbolCatalog.filter(s => s[2] === cat).length;
      b.textContent = `${cat === 'all' ? '全部' : cat} (${cnt})`;
      b.className = 'scat-btn px-2.5 py-1 rounded-md text-[11px] font-medium ' + (cat === 'all'
        ? 'bg-[var(--primary)] text-[var(--primary-foreground)]'
        : 'text-[var(--muted-foreground)] hover:bg-[var(--background)]');
      b.addEventListener('click', () => {
        symCatFilter = cat;
        document.querySelectorAll('.scat-btn').forEach(btn => {
          const on = btn.dataset.scat === symCatFilter;
          btn.className = 'scat-btn px-2.5 py-1 rounded-md text-[11px] font-medium ' + (on
            ? 'bg-[var(--primary)] text-[var(--primary-foreground)]'
            : 'text-[var(--muted-foreground)] hover:bg-[var(--background)]');
        });
        renderSymbolsCatalog();
      });
      symCatBar.appendChild(b);
    });

    document.querySelectorAll('.sym-sz-btn').forEach(b => {
      b.addEventListener('click', () => {
        symSizePx = +b.dataset.sz;
        document.querySelectorAll('.sym-sz-btn').forEach(btn => {
          const on = +btn.dataset.sz === symSizePx;
          btn.className = 'sym-sz-btn px-2 py-1 rounded ' + (on
            ? 'bg-[var(--primary)] text-[var(--primary-foreground)]'
            : 'text-[var(--muted-foreground)]');
        });
        renderSymbolsCatalog();
      });
    });
    document.getElementById('sym-search').addEventListener('input', renderSymbolsCatalog);
    document.getElementById('sym-rtl').addEventListener('change', renderSymbolsCatalog);

    function renderSymbolsCatalog() {
      const q = document.getElementById('sym-search').value.trim().toLowerCase();
      const rtlOn = document.getElementById('sym-rtl').checked;
      const wgt = +activeWeight;

      // Update live inline Icon + Text button strip
      const symByName = Object.fromEntries(PAYLOAD.symbolCatalog.map(s => [s[0], s]));
      const btnItems = [
        ['send', 'Send Prompt', true],
        ['settings', 'Settings', false],
        ['run-code', 'Run Code', false],
        ['share', 'Share', false],
        ['mic-off', 'Muted', false],
        ['report-flag', 'Flag', false],
        ['pin-filled', 'Pinned', false],
      ];
      document.getElementById('sym-btn-bar').innerHTML = btnItems.map(([nm, lbl, prim]) => {
        const s = symByName[nm];
        const ch = s ? String.fromCodePoint(s[1]) : '';
        return `<span ${rtlOn ? 'dir="rtl"' : ''} class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg border ${prim ? 'bg-[var(--primary)] text-[var(--primary-foreground)] border-[var(--primary)]' : 'bg-[var(--background)] border-[var(--border)]'} adm-sans" style="font-size:${Math.min(symSizePx, 20)}px;font-weight:${wgt};line-height:1.25"><span class="adm-symbols" style="font-weight:${wgt};${rtlOn ? 'font-feature-settings:&quot;rtlm&quot; 1' : ''}">${ch}</span><span>${lbl}</span></span>`;
      }).join('');

      const filtered = PAYLOAD.symbolCatalog.filter(([name, cp, cat, tags]) => {
        if (symCatFilter !== 'all' && cat !== symCatFilter) return false;
        if (!q) return true;
        const hex = 'u+' + cp.toString(16).padStart(4, '0');
        return name.includes(q) || hex.includes(q) || cat.toLowerCase().includes(q) || tags.some(t => t.toLowerCase().includes(q));
      });
      document.getElementById('sym-count-lbl').textContent = `显示 ${filtered.length} / ${PAYLOAD.symbolCatalog.length} 个 24×24 图标 (Weight ${wgt}${rtlOn ? ', RTL rtlm' : ''})`;

      const grid = document.getElementById('sym-grid');
      grid.innerHTML = '';
      filtered.forEach(([name, cp, cat, tags, rtlFlag, filledFlag]) => {
        const ch = String.fromCodePoint(cp);
        const hex = 'U+' + cp.toString(16).toUpperCase().padStart(4, '0');
        const card = document.createElement('button');
        card.className = 'p-2.5 rounded-xl border text-center transition-colors flex flex-col items-center justify-between min-h-[88px] ' + (filledFlag
          ? 'border-sky-400/50 bg-sky-500/5'
          : 'border-[var(--border)] bg-[var(--background)] hover:border-[var(--primary)]');
        card.title = `${name} (${hex}) · ${cat} · tags: ${tags.join(', ')}`;
        const dirAttr = (rtlOn && rtlFlag) ? 'dir="rtl"' : '';
        const featStyle = (rtlOn && rtlFlag) ? "font-feature-settings:'rtlm' 1;" : '';
        card.innerHTML = `
          <div class="w-full flex justify-between text-[9px] font-mono text-[var(--muted-foreground)]">
            <span>${hex}</span>
            <span>${rtlFlag ? 'RTL' : (filledFlag ? 'FILL' : '')}</span>
          </div>
          <div ${dirAttr} class="adm-symbols my-1 text-[var(--foreground)] leading-none" style="font-size:${symSizePx}px;font-weight:${wgt};${featStyle}">${ch}</div>
          <div class="text-[10px] font-mono truncate max-w-full text-[var(--foreground)]">${name}</div>
        `;
        card.addEventListener('click', () => {
          activeFam = 'symbols';
          const store = activeGlyphStore();
          const base = store.glyphs.find(g => g.cp === cp);
          const glyph = (rtlOn && rtlFlag && store.byName[base.name + '.rtl']) || base;
          curGlyphName = glyph.name;
          document.querySelector('[data-tab="microscope"]').click();
          updateHeaderAndControls();
        });
        grid.appendChild(card);
      });
    }

    // ---------------- TAB 6: KERNING TABLE ----------------
    document.getElementById('kern-count-lbl').textContent = `${PAYLOAD.kerning.length} 组共享 Class Kerning`;
    function renderKerning() {
      const q = document.getElementById('kern-filter').value.trim().toLowerCase();
      const grid = document.getElementById('kern-grid');
      grid.innerHTML = '';
      const kernFam = (activeFam === 'serif' || activeFam === 'sans') ? activeFam : 'serif';
      const kWgt = nearestMasterWeight(activeWeight);
      const kKey = activeStyle === 'italic' ? (kWgt + 'i') : kWgt;
      const map = FAMILIES[kernFam].weights[kKey].byName;
      const extraItalicPairs = activeStyle === 'italic'
        ? [['parenleft', 'f', 28], ['bracketleft', 'f', 28], ['braceleft', 'f', 28]]
        : [];
      const pairsToShow = [...extraItalicPairs, ...PAYLOAD.kerning];
      pairsToShow.forEach(([l, r, val]) => {
        if (q && !l.toLowerCase().includes(q) && !r.toLowerCase().includes(q)) return;
        const lg = map[l], rg = map[r];
        const pairStr = (lg && lg.ch ? lg.ch : l) + (rg && rg.ch ? rg.ch : r);
        const card = document.createElement('button');
        card.className = 'p-2 rounded-lg border border-[var(--border)] bg-[var(--background)] text-left flex items-baseline justify-between gap-1';
        card.innerHTML = `
          <span class="adm-active text-xl">${pairStr}</span>
          <span class="font-mono text-xs ${val < 0 ? 'text-[var(--muted-foreground)]' : 'text-[var(--primary)]'}">${val > 0 ? '+' + val : val}</span>
        `;
        card.title = `${l} + ${r} = ${val}u`;
        card.addEventListener('click', () => {
          if (lg) {
            curGlyphName = lg.name;
            document.querySelector('[data-tab="microscope"]').click();
            renderGlyphSelector();
            renderMicroscope();
          }
        });
        grid.appendChild(card);
      });
    }
    document.getElementById('kern-filter').addEventListener('input', renderKerning);

    syncTesterStyles();
    setActiveFamily('serif');
    renderTracy(false);
    renderWaterfall();
    renderSymbolsCatalog();
  </script>
</body>
</html>
"""

STANDALONE_THEME_CSS = """  <style>
    :root {
      --background: #f5f4f0;
      --card: #ffffff;
      --card-border: #eae8e2;
      --border: #dfddd6;
      --foreground: #16181c;
      --muted-foreground: #6c727f;
      --primary: #181a1f;
      --primary-foreground: #ffffff;
      --secondary: #ebeae4;
      --secondary-foreground: #22252b;
    }
    @media (prefers-color-scheme: dark) {
      :root {
        --background: #101216;
        --card: #181b21;
        --card-border: #252a34;
        --border: #2b303b;
        --foreground: #eceef2;
        --muted-foreground: #8f96a3;
        --primary: #eceef2;
        --primary-foreground: #14161a;
        --secondary: #242933;
        --secondary-foreground: #e5e7eb;
      }
    }
  </style>
"""


def main() -> None:
    payload_str, n_glyphs, n_kern, vf_kb, static_kb, sym_vf_kb = build_payload()
    catalog = json.loads(payload_str)["symbolCatalog"]
    filled = (
        HTML_TEMPLATE.replace("__PAYLOAD_JSON__", payload_str)
        .replace("__VERSION__", VERSION_STR)
        .replace("__N_GLYPHS__", str(n_glyphs))
        .replace("__SYMBOL_COUNT__", str(len(catalog)))
        .replace("__LAST_PUA__", f"U+{catalog[-1][1]:04X}")
        .replace("__VF_KB__", f"{vf_kb:.1f}")
        .replace("__STATIC_KB__", f"{static_kb:.1f}")
        .replace("__SYM_KB__", f"{sym_vf_kb:.1f}")
    )

    standalone_html = filled.replace("__STANDALONE_VARS__", STANDALONE_THEME_CSS)
    out_path = ROOT / "specimens" / "inspector.html"
    out_path.write_text(standalone_html, encoding="utf-8")
    print(
        f"Built Milestone 8 Inspector v{VERSION_STR} (7 VF {vf_kb:.1f} KB + 21 Static {static_kb:.1f} KB, "
        f"{len(catalog)} Symbols, {n_kern} class rules) -> {out_path} ({out_path.stat().st_size // 1024} KB)"
    )


if __name__ == "__main__":
    main()
