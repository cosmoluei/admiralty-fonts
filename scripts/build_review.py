"""
Builds specimens/review.html: a browser page for reviewing the 0.300 additions
(62 new symbols, GF Latin Plus, Mono box drawing, Vietnamese).

The page loads the fonts by relative path from ../fonts/, so open it from a copy of the
repository (or the build folder) where fonts/variable and fonts/woff2 exist.
"""

from __future__ import annotations
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from glyphs_latin_plus import LATIN_PLUS_CODEPOINTS  # noqa: E402
from symbols_phase2 import SYMBOLS_PHASE2  # noqa: E402

PAGE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Admiralty Review</title>
<style>
@font-face{font-family:"AdmSans";src:url("../fonts/variable/AdmiraltySans[wght].woff2") format("woff2");font-weight:400 700;font-style:normal}
@font-face{font-family:"AdmSans";src:url("../fonts/variable/AdmiraltySans-Italic[wght].woff2") format("woff2");font-weight:400 700;font-style:italic}
@font-face{font-family:"AdmSerif";src:url("../fonts/variable/AdmiraltySerif[wght].woff2") format("woff2");font-weight:400 700;font-style:normal}
@font-face{font-family:"AdmSerif";src:url("../fonts/variable/AdmiraltySerif-Italic[wght].woff2") format("woff2");font-weight:400 700;font-style:italic}
@font-face{font-family:"AdmMono";src:url("../fonts/variable/AdmiraltyMono[wght].woff2") format("woff2");font-weight:400 700;font-style:normal}
@font-face{font-family:"AdmMono";src:url("../fonts/variable/AdmiraltyMono-Italic[wght].woff2") format("woff2");font-weight:400 700;font-style:italic}
@font-face{font-family:"AdmSym";src:url("../fonts/variable/AdmiraltySymbols[wght].woff2") format("woff2");font-weight:400 700}
:root{--bg:#f6f5f1;--panel:#fff;--ink:#1b1d21;--muted:#6b6f78;--line:#e2e0da;--accent:#2a5bd7;--guide:rgba(42,91,215,.10)}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#15171a;--panel:#1d2024;--ink:#eceae4;--muted:#9aa0aa;--line:#30343a;--accent:#7ea2ff;--guide:rgba(126,162,255,.14)}}
:root[data-theme="dark"]{--bg:#15171a;--panel:#1d2024;--ink:#eceae4;--muted:#9aa0aa;--line:#30343a;--accent:#7ea2ff;--guide:rgba(126,162,255,.14)}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font-family:"AdmSans",system-ui,sans-serif;font-size:15px;line-height:1.5}
header{position:sticky;top:0;z-index:5;background:var(--bg);border-bottom:1px solid var(--line);padding:12px 16px}
.bar{max-width:1280px;margin:0 auto;display:flex;flex-wrap:wrap;gap:10px 18px;align-items:center}
h1{font-size:18px;margin:0 12px 0 0;font-weight:700}
nav{display:flex;gap:4px;flex-wrap:wrap}
nav button,.seg button{font:inherit;border:1px solid var(--line);background:var(--panel);color:var(--ink);padding:5px 11px;border-radius:7px;cursor:pointer}
nav button.on,.seg button.on{background:var(--ink);color:var(--bg);border-color:var(--ink)}
.ctl{display:flex;align-items:center;gap:8px;color:var(--muted);font-size:13px}
.ctl input[type=range]{width:120px}
.seg{display:flex;gap:2px}
main{max-width:1280px;margin:0 auto;padding:18px 16px 60px}
section{display:none}section.on{display:block}
h2{font-size:16px;margin:26px 0 8px}
p.note{color:var(--muted);margin:4px 0 14px;max-width:820px}
.grid{display:grid;gap:10px}
.card{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:10px}
.sym{grid-template-columns:repeat(auto-fill,minmax(178px,1fr))}
.sym .big{font-family:AdmSym;font-size:var(--sz,64px);line-height:1;text-align:center;padding:10px 0 6px;background:linear-gradient(var(--guide),var(--guide)) center/100% 1px no-repeat}
.sym .name{font-weight:600;font-size:13px}
.sym .meta{color:var(--muted);font-size:11.5px;font-family:AdmMono}
.sym .wts{display:flex;justify-content:space-between;align-items:center;font-family:AdmSym;margin-top:6px;border-top:1px solid var(--line);padding-top:6px}
.sym .wts span:nth-child(1){font-size:24px;font-weight:400}.sym .wts span:nth-child(2){font-size:24px;font-weight:500}.sym .wts span:nth-child(3){font-size:24px;font-weight:700}
.sym .wts span:nth-child(4){font-size:16px;font-weight:400}.sym .wts span:nth-child(5){font-size:16px;font-weight:700}
.sym .inline{font-size:14px;margin-top:6px;color:var(--muted);white-space:nowrap;overflow:hidden}
.sym .inline i{font-family:AdmSym;font-style:normal;color:var(--ink)}
.cat{grid-column:1/-1;font-weight:700;color:var(--muted);font-size:12px;letter-spacing:.06em;text-transform:uppercase;margin-top:8px}
.chars{grid-template-columns:repeat(auto-fill,minmax(150px,1fr))}
.ch{display:grid;grid-template-columns:1fr 1fr 1fr;align-items:end;text-align:center;font-size:var(--sz,48px);line-height:1.25}
.ch span:nth-child(1){font-family:AdmSans}.ch span:nth-child(2){font-family:AdmSerif}.ch span:nth-child(3){font-family:AdmMono}
.lbl{display:flex;justify-content:space-between;color:var(--muted);font-family:AdmMono;font-size:11px;margin-top:4px}
.fam{display:grid;grid-template-columns:1fr 1fr 1fr;color:var(--muted);font-size:11px;text-align:center}
.sample{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:14px 16px;margin-bottom:10px}
.sample .t{font-size:var(--tsz,26px);line-height:1.5;overflow-wrap:anywhere}
.sample .k{color:var(--muted);font-size:12px;margin-bottom:4px}
.box{font-family:AdmMono;line-height:1.3;white-space:pre;font-size:var(--bsz,22px);background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:14px;overflow-x:auto;margin:0 0 12px}
.boxgrid{grid-template-columns:repeat(auto-fill,minmax(74px,1fr))}
.boxgrid .card{padding:6px;text-align:center}
.boxgrid .g{font-family:AdmMono;font-size:44px;line-height:1.3;display:inline-block;background:var(--guide)}
.boxgrid .lbl{justify-content:center}
.viet{grid-template-columns:repeat(auto-fill,minmax(132px,1fr))}
.it{font-style:italic}
</style>
</head>
<body>
<header><div class="bar">
  <h1>Admiralty 0.300 review</h1>
  <nav id="tabs">
    <button data-t="sym" class="on">New symbols</button>
    <button data-t="lp">Latin Plus</button>
    <button data-t="box">Box drawing</button>
    <button data-t="vi">Vietnamese</button>
  </nav>
  <label class="ctl">Weight <input id="wght" type="range" min="400" max="700" step="1" value="400"><b id="wv">400</b></label>
  <label class="ctl">Size <input id="size" type="range" min="16" max="120" step="1" value="56"><b id="sv">56</b></label>
  <div class="ctl seg" id="ital"><button data-v="normal" class="on">Upright</button><button data-v="italic">Italic</button></div>
  <div class="ctl seg" id="theme"><button data-v="light">Light</button><button data-v="dark">Dark</button></div>
</div></header>
<main>
<section id="sym" class="on">
  <p class="note">The 62 symbols added in 0.300 (U+E0DA–U+E117). The big glyph follows the weight slider; the strip below shows Regular, Medium and Bold at 24 px, then Regular and Bold at 16 px. The blue line is the text axis. Symbols marked ⇄ are mirrored in right-to-left text (<code>rtlm</code>): switch on RTL to see them.</p>
  <div class="ctl seg" id="rtl" style="margin-bottom:10px"><button data-v="ltr" class="on">LTR</button><button data-v="rtl">RTL</button></div>
  <div class="grid sym" id="symgrid"></div>
</section>
<section id="lp">
  <p class="note">Google Fonts Latin Plus characters added to every style. Each cell shows Sans, Serif and Mono. Weight and italic follow the controls.</p>
  <div class="sample"><div class="k">In text — Sans</div><div class="t lpt" style="font-family:AdmSans"></div></div>
  <div class="sample"><div class="k">In text — Serif</div><div class="t lpt" style="font-family:AdmSerif"></div></div>
  <div class="sample"><div class="k">In text — Mono</div><div class="t lpt" style="font-family:AdmMono"></div></div>
  <div class="grid chars" id="lpgrid"></div>
</section>
<section id="box">
  <p class="note">Admiralty Mono box drawing and block elements (U+2500–U+259F). They fill the whole cell, so lines join when the line height is 1.3 (the font's full height). They stay upright in the italics.</p>
  <pre class="box" id="tui"></pre>
  <div class="grid boxgrid" id="boxgrid"></div>
</section>
<section id="vi">
  <p class="note">Vietnamese: the horn letters Ơ ơ Ư ư, the new marks (hook above, dot below, horn) and all precomposed letters U+1EA0–U+1EF9. Acute, grave and hook sit beside a circumflex; other stacks are vertical.</p>
  <div id="visamples"></div>
  <div class="grid viet" id="vigrid"></div>
</section>
</main>
<script>
const SYMS = __SYMS__;
const LP = __LP__;
const $ = s => document.querySelector(s);
const hex = c => "U+" + c.toString(16).toUpperCase().padStart(4, "0");
const root = document.documentElement;

// ---- controls -----------------------------------------------------------------
function setWeight(v){ document.querySelectorAll("main").forEach(m => m.style.fontVariationSettings = ""); root.style.setProperty("--w", v); $("#wv").textContent = v;
  document.querySelectorAll(".big, .ch, .lpt, .viet .ch, #visamples .t, .box, .boxgrid .g").forEach(e => e.style.fontWeight = v); }
$("#wght").oninput = e => setWeight(e.target.value);
$("#size").oninput = e => { const v = e.target.value; $("#sv").textContent = v; root.style.setProperty("--sz", v + "px");
  root.style.setProperty("--tsz", Math.max(16, Math.round(v / 2)) + "px"); root.style.setProperty("--bsz", Math.max(12, Math.round(v / 2.5)) + "px"); };
function seg(id, fn){ const el = $(id); el.onclick = e => { const b = e.target.closest("button"); if(!b) return;
  el.querySelectorAll("button").forEach(x => x.classList.toggle("on", x === b)); fn(b.dataset.v); }; }
seg("#ital", v => document.querySelectorAll(".ch, .lpt, #visamples .t").forEach(e => e.style.fontStyle = v));
seg("#theme", v => root.setAttribute("data-theme", v));
seg("#rtl", v => document.querySelectorAll("#symgrid .big, #symgrid .wts").forEach(e => { e.dir = v; e.style.fontFeatureSettings = v === "rtl" ? '"rtlm" 1' : "normal"; }));
$("#tabs").onclick = e => { const b = e.target.closest("button"); if(!b) return;
  document.querySelectorAll("#tabs button").forEach(x => x.classList.toggle("on", x === b));
  document.querySelectorAll("section").forEach(s => s.classList.toggle("on", s.id === b.dataset.t)); };

// ---- symbols -------------------------------------------------------------------
{ const g = $("#symgrid"); let cat = "";
  for (const s of SYMS){
    if (s.cat !== cat){ cat = s.cat; g.insertAdjacentHTML("beforeend", `<div class="cat">${cat}</div>`); }
    const ch = String.fromCodePoint(s.cp);
    g.insertAdjacentHTML("beforeend", `<div class="card"><div class="big">${ch}</div>
      <div class="name">${s.label}${s.rtl ? " ⇄" : ""}</div><div class="meta">${s.name} · ${hex(s.cp)}</div>
      <div class="wts"><span>${ch}</span><span>${ch}</span><span>${ch}</span><span>${ch}</span><span>${ch}</span></div>
      <div class="inline">Open <i>${ch}</i> ${s.label}</div></div>`);
  } }

// ---- latin plus ----------------------------------------------------------------
{ const g = $("#lpgrid");
  for (const c of LP){ const ch = String.fromCodePoint(c);
    g.insertAdjacentHTML("beforeend", `<div class="card"><div class="ch"><span>${ch}</span><span>${ch}</span><span>${ch}</span></div>
      <div class="fam"><span>Sans</span><span>Serif</span><span>Mono</span></div><div class="lbl"><span>${hex(c)}</span></div></div>`); }
  const t = "x⁴ + y⁵ = z⁹ · H₂O, CO₂, C₆H₁₂O₆ · ⅓ + ⅔ = 1 · 3⁄4 · ₫ 50.000 · ₺ ₴ ₸ ₦ ₱ ₲ ₵ ₡ ₭ ₮ ₨ ₪ ₼ ₾ ฿ ₿ · ∂f/∂x · ∑ ∏ ∫ ∅ · ‖v‖ · ⟨a, b⟩ · 5 ℓ · ℮ · Ⓓ · ↖ ↙ ↕ · ■ □ ▪ ▫ ▲ △ ▶ ▷ ▼ ▽ ◀ ◁ ◆ ◇ ○ ● ◦";
  document.querySelectorAll(".lpt").forEach(e => e.textContent = t); }

// ---- box drawing ---------------------------------------------------------------
$("#tui").textContent =
`┌─ agent ──────────────┬──────────────┐   ╔══════════╗  ╭──────╮
│ status   ● running   │ cpu ▁▂▃▅▆▇█  │   ║ Admiralty║  │ mono │
├──────────────────────┼──────────────┤   ╠══════════╣  ╰──┬───╯
│ tasks    ███████░░░  │ mem ▓▓▓▒▒░░  │   ║ ░▒▓█ ▀▄▌▐║     │
│ queue    ┄┄┄┄┄┄┄┄┄┄  │ net ╱╲╱╲╱╲   │   ╚══════════╝  ┏━━┷━━━┓
└──────────────────────┴──────────────┘   ▛▀▜ ▙▄▟ ▚▞     ┃ bold ┃
src/                                                     ┗━━━━━━┛
├── agent/
│   ├── planner.ts
│   └── tools.ts
└── index.ts`;
{ const g = $("#boxgrid");
  for (let c = 0x2500; c <= 0x259F; c++){ const ch = String.fromCodePoint(c);
    g.insertAdjacentHTML("beforeend", `<div class="card"><span class="g">${ch}</span><div class="lbl">${c.toString(16).toUpperCase()}</div></div>`); } }

// ---- vietnamese ----------------------------------------------------------------
{ const text = "Tiếng Việt là ngôn ngữ chính thức của Việt Nam. Người ta thường nói rằng: “Học, học nữa, học mãi.” Ở đây có những quyển sách hay, bữa phở ngon và nước trà ấm. ĐẤT NƯỚC · Ở ĐÂY · QUẢNG NGÃI · THỪA THIÊN–HUẾ · Giá: 45.000 ₫";
  const box = $("#visamples");
  for (const [f, n] of [["AdmSans","Sans"],["AdmSerif","Serif"],["AdmMono","Mono"]])
    box.insertAdjacentHTML("beforeend", `<div class="sample"><div class="k">${n}</div><div class="t" style="font-family:${f}">${text}</div></div>`);
  const cps = [0x01A0,0x01A1,0x01AF,0x01B0,0x0110,0x0111,0x20AB]; for (let c = 0x1EA0; c <= 0x1EF9; c++) cps.push(c);
  const g = $("#vigrid");
  for (const c of cps){ const ch = String.fromCodePoint(c);
    g.insertAdjacentHTML("beforeend", `<div class="card"><div class="ch"><span>${ch}</span><span>${ch}</span><span>${ch}</span></div><div class="lbl"><span>${hex(c)}</span></div></div>`); } }
document.querySelector("#size").dispatchEvent(new Event("input"));
setWeight(400);
</script>
</body>
</html>
"""


def main() -> Path:
    cats = []
    meta = {}
    sj = ROOT / "symbols" / "admiralty-symbols.json"
    if sj.exists():
        for s in json.loads(sj.read_text(encoding="utf-8"))["symbols"]:
            meta[s["name"]] = s
    syms = []
    for i, spec in enumerate(SYMBOLS_PHASE2):
        m = meta.get(spec.name, {})
        syms.append({"name": spec.name, "label": m.get("label", spec.name), "cp": m.get("codepointInt", 0xE0DA + i),
                     "cat": m.get("category", ""), "rtl": bool(m.get("rtlMirror", False))})
    out = ROOT / "specimens" / "review.html"
    html = PAGE.replace("__SYMS__", json.dumps(syms, ensure_ascii=False)).replace("__LP__", json.dumps(sorted(LATIN_PLUS_CODEPOINTS)))
    out.write_text(html, encoding="utf-8")
    print(f"Review page ({len(syms)} symbols, {len(LATIN_PLUS_CODEPOINTS)} Latin Plus) -> {out}")
    return out


if __name__ == "__main__":
    main()
