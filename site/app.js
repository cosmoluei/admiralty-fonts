(() => {
  "use strict";
  const T = window.TYPE;
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const reduce = matchMedia("(prefers-reduced-motion: reduce)");
  const clamp = (v, a, b) => Math.min(b, Math.max(a, v));
  const lerp = (a, b, t) => a + (b - a) * t;
  const R = T.radiusTag;
  const FAM = T.families;
  const NAMES = { sans: "Admiralty Sans", serif: "Admiralty Serif", mono: "Admiralty Mono" };
  const SAX = FAM.sans.axes, WG = SAX.wght, WD = SAX.wdth || [100, 100], RD = SAX.radius || [0, 0];
  const esc = (s) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

  /* ---------- type helpers ---------- */
  // Weight and width use the standard CSS properties; radius and slant use
  // font-variation-settings (custom or extra axes). Values are clamped to each family's range.
  function typeProps(famKey, s) {
    const f = FAM[famKey], ax = f.axes, o = { "font-family": f.css };
    o["font-weight"] = String(Math.round(clamp(s.w ?? 400, ...(ax.wght || [400, 400]))));
    o["font-stretch"] = (ax.wdth ? clamp(s.d ?? 100, ...ax.wdth) : 100).toFixed(1) + "%";
    const fvs = [];
    if (ax.radius) fvs.push(`"${R}" ${Math.round(clamp(s.r ?? 0, ...ax.radius))}`);
    const ital = f.italic ? s.ital || 0 : 0;
    o["font-style"] = f.italic === "face" && ital > 0.5 ? "italic" : "normal";
    if (f.italic === "slnt") fvs.push(`"slnt" ${(f.slnt * ital).toFixed(2)}`);
    o["font-variation-settings"] = fvs.length ? fvs.join(", ") : "normal";
    return o;
  }
  const apply = (el, famKey, s) => { const p = typeProps(famKey, s); for (const k in p) el.style.setProperty(k, p[k]); };
  const cssText = (p) => Object.entries(p).map(([k, v]) => `${k}: ${v};`).join(" ");

  /* ---------- symbols ---------- */
  const SYM = new Map(window.SYMBOLS.map(([name, label, cp, cat, tags]) => [name, { name, label, cp, cat, tags }]));
  const ch = (n) => (SYM.has(n) ? String.fromCodePoint(SYM.get(n).cp) : "");
  const symHTML = (n, extra = "") => `<i class="sym" aria-hidden="true" data-char="${ch(n)}" ${extra}></i>`;
  const paintSyms = (root = document) => $$("[data-sym]", root).forEach((el) => el.setAttribute("data-char", ch(el.dataset.sym)));
  paintSyms();

  /* ---------- toast, copy ---------- */
  const toast = $("#toast"); let toastT;
  function say(msg) { toast.textContent = msg; toast.classList.add("show"); clearTimeout(toastT); toastT = setTimeout(() => toast.classList.remove("show"), 1800); }
  async function copy(text, msg) {
    try { await navigator.clipboard.writeText(text); say(msg); } catch { say("Copy is blocked here. Select the text and copy it yourself."); }
  }

  /* ---------- theme ---------- */
  const root = document.documentElement, themeBtn = $("#theme");
  const isDark = () => (root.dataset.theme ? root.dataset.theme === "dark" : matchMedia("(prefers-color-scheme: dark)").matches);
  function paintTheme() { $(".sym", themeBtn).dataset.sym = isDark() ? "light-mode" : "dark-mode"; paintSyms(themeBtn); themeBtn.setAttribute("aria-label", isDark() ? "Switch to day colours" : "Switch to night colours"); }
  try { const t = localStorage.getItem("adm-theme"); if (t) root.dataset.theme = t; } catch {}
  themeBtn.addEventListener("click", () => { root.dataset.theme = isDark() ? "light" : "dark"; try { localStorage.setItem("adm-theme", root.dataset.theme); } catch {} paintTheme(); drawChart(); });
  paintTheme();

  /* =========================================================================================
     1. Hero: drag the handles of the selected word
     ========================================================================================= */
  const word = $("#word"), canvas = $("#canvas"), sel = $("#sel");
  const H = { w: 400, d: 100, r: 0 };
  function rulerLabels() {
    const r = $("#ruler"), w = r.clientWidth; let html = "";
    for (let x = 0; x < w; x += 100) html += `<span style="left:${x}px">${x}</span>`;
    r.innerHTML = html;
  }
  let frozen = null;
  function paintHero() {
    apply(word, "sans", H);
    // fit: the word fills the canvas width at its current settings, but never grows taller than the canvas allows
    // The width scales with the font size, so measure at the current size (no reset, so a transition can run).
    // While a handle is held the size is frozen, so the box edges follow the pointer; it only shrinks if the word would overflow.
    const fs = parseFloat(getComputedStyle(word).fontSize) || 100;
    const w100 = (word.getBoundingClientRect().width / fs) * 100;
    const cs = getComputedStyle(canvas);
    const avail = canvas.clientWidth - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight) - 24;
    const maxByH = Math.max(80, innerHeight * 0.44);
    const fit = Math.min((avail / w100) * 100, maxByH);
    word.style.fontSize = (frozen ? Math.min(frozen, fit) : fit) + "px";
    const v = { w: Math.round(H.w), d: Math.round(H.d), r: Math.round(H.r) };
    $("#pW").textContent = v.w; $("#pD").textContent = v.d + "%"; $("#pR").textContent = v.r;
    $("#tipW").textContent = v.w; $("#tipD").textContent = v.d + "%"; $("#tipR").textContent = v.r;
    [["#hdW", WG, v.w, v.w], ["#hdD", WD, v.d, v.d + "%"], ["#hdR", RD, v.r, v.r]].forEach(([s, [lo, hi], now, txt]) => {
      const el = $(s); el.setAttribute("aria-valuemin", lo); el.setAttribute("aria-valuemax", hi); el.setAttribute("aria-valuenow", now); el.setAttribute("aria-valuetext", txt); });
  }
  const handles = { hdW: "w", hdD: "d", hdR: "r" };
  const RANGE = { w: WG, d: WD, r: RD };
  Object.entries(handles).forEach(([id, key]) => {
    const el = $("#" + id);
    if (key === "r" && !SAX.radius) { el.hidden = true; return; }
    let start = null;
    el.addEventListener("pointerdown", (e) => {
      e.preventDefault(); el.setPointerCapture(e.pointerId); el.classList.add("drag"); document.body.classList.add("dragging");
      frozen = parseFloat(getComputedStyle(word).fontSize); word.classList.remove("settle");
      const hb = el.getBoundingClientRect();
      start = { x: e.clientX, y: e.clientY, v: H[key], hx: hb.left + hb.width / 2 };
    });
    el.addEventListener("pointermove", (e) => {
      if (!start) return;
      const [lo, hi] = RANGE[key], span = hi - lo;
      const dx = e.clientX - start.x, dy = e.clientY - start.y;
      if (key === "d") {
        // the width handle sits on the right edge and stays under the pointer: find the width whose right edge lands there
        const target = start.hx + dx, mid = () => sel.getBoundingClientRect().right;
        let a = lo, b = hi;
        for (let i = 0; i < 9; i++) { const m = (a + b) / 2; word.style.fontStretch = m + "%"; if (mid() < target) a = m; else b = m; }
        H.d = (a + b) / 2;
      } else H[key] = clamp(start.v + (key === "w" ? -dy / 240 : dx / 280) * span, lo, hi);
      paintHero();
    });
    const end = () => {
      if (!start) return; start = null; el.classList.remove("drag"); document.body.classList.remove("dragging");
      frozen = null; word.classList.add("settle"); paintHero(); };
    el.addEventListener("pointerup", end); el.addEventListener("pointercancel", end);
    el.addEventListener("keydown", (e) => {
      const [lo, hi] = RANGE[key], step = (hi - lo) / (e.shiftKey ? 8 : 40);
      const dir = { ArrowUp: 1, ArrowRight: 1, ArrowDown: -1, ArrowLeft: -1 }[e.key];
      if (!dir) return; e.preventDefault(); H[key] = clamp(H[key] + dir * step, lo, hi); paintHero();
    });
  });
  if (matchMedia("(pointer: coarse)").matches) $("#hint").textContent = "Drag the handles on the box: the top one sets the weight, the right one the width, the corner one the radius.";
  function heroIntro() {
    if (reduce.matches) { paintHero(); return; }
    // one opening move: from Thin Compressed to Regular, then the handles pulse to invite a drag
    const from = { w: WG[0], d: WD[0] }, t0 = performance.now(), dur = 1300;
    const step = (now) => {
      const k = clamp((now - t0) / dur, 0, 1), e = 1 - Math.pow(1 - k, 3);
      H.w = lerp(from.w, 400, e); H.d = lerp(from.d, 100, e); paintHero();
      if (k < 1) requestAnimationFrame(step); else $$(".hd-w, .hd-d, .hd-r").forEach((h) => h.classList.add("pulse"));
    };
    requestAnimationFrame(step);
  }

  /* =========================================================================================
     2. Two voices: a divider through one paragraph
     ========================================================================================= */
  const SPLIT_TEXT = "The last ferry leaves Central at 23:30.";
  const split = $("#split"), sSerif = $("#splitSerif"), sSans = $("#splitSans"), bar = $("#splitBar");
  sSerif.textContent = SPLIT_TEXT; sSans.textContent = SPLIT_TEXT;
  let splitPos = 0.5;
  function paintSplit() {
    const b = split.getBoundingClientRect(), x = splitPos * b.width;
    bar.style.left = x + "px"; bar.setAttribute("aria-valuenow", Math.round(splitPos * 100));
    const sr = sSerif.getBoundingClientRect(), nr = sSans.getBoundingClientRect();
    sSerif.style.clipPath = `inset(-20px ${Math.max(0, sr.right - (b.left + x))}px -20px -20px)`;
    sSans.style.clipPath = `inset(-20px -20px -20px ${Math.max(0, b.left + x - nr.left)}px)`;
  }
  function lineEnds(p) {
    const node = p.firstChild, txt = node.textContent, ends = []; const re = /\S+/g; let m, lastTop = null, idx = 0, last = -1;
    const range = document.createRange();
    while ((m = re.exec(txt))) { range.setStart(node, m.index); range.setEnd(node, m.index + m[0].length); const r = range.getClientRects()[0]; if (lastTop !== null && r.top > lastTop + 2) ends.push(last); lastTop = r.top; last = idx++; }
    ends.push(last); return ends;
  }
  function measureSplit() {
    const a = lineEnds(sSans), b = lineEnds(sSerif);
    const same = a.length === b.length && a.every((v, i) => v === b[i]);
    $("#measure").textContent = same ? `Measured now: all ${a.length} lines break on the same word in Sans and Serif.` : `Measured now: ${a.filter((v, i) => v === b[i]).length} of ${a.length} lines break on the same word.`;
  }
  let splitDrag = false;
  const splitTo = (cx) => { const b = split.getBoundingClientRect(); splitPos = clamp((cx - b.left) / b.width, 0.04, 0.96); paintSplit(); };
  split.addEventListener("pointerdown", (e) => { e.preventDefault(); splitDrag = true; split.setPointerCapture(e.pointerId); document.body.classList.add("dragging"); splitTo(e.clientX); });
  split.addEventListener("pointermove", (e) => { if (splitDrag) splitTo(e.clientX); });
  const splitEnd = () => { splitDrag = false; document.body.classList.remove("dragging"); };
  split.addEventListener("pointerup", splitEnd); split.addEventListener("pointercancel", splitEnd);
  bar.addEventListener("keydown", (e) => { const d = { ArrowLeft: -0.04, ArrowRight: 0.04 }[e.key]; if (d) { e.preventDefault(); splitPos = clamp(splitPos + d, 0.04, 0.96); paintSplit(); } });

  /* =========================================================================================
     3. Put it to work: six real interfaces, one set of controls
     ========================================================================================= */
  const SCENES = [
    { id: "code", label: "Code editor", icon: "code", fam: "mono", role: "Code and terminal text", rules: [["#ideCode", "14px"], ["#term", "13px"]], def: { w: 400, d: 100, r: 0, ital: 0, s: 100 } },
    { id: "dash", label: "Dashboard", icon: "bar-chart", fam: "sans", role: "Figures and headings", rules: [[".num", "clamp(24px, 5.6vw, 34px)"], [".dash-title", "28px"]], def: { w: 700, d: 82, r: 0, ital: 0, s: 100 } },
    { id: "read", label: "Reading app", icon: "document", fam: "serif", role: "Article text", rules: [["#readBody", "19px"]], def: { w: 400, d: 100, r: 0, ital: 0, s: 100 } },
    { id: "chat", label: "Assistant", icon: "chat", fam: "serif", role: "Assistant replies", rules: [[".msg.bot .bt", "17px"]], def: { w: 400, d: 100, r: 0, ital: 0, s: 100 } },
    { id: "poster", label: "Poster", icon: "image", fam: "sans", role: "Poster headline", rules: [["#poH", "19cqi"], ["#po.line #poH", "11cqi"]], def: { w: 900, d: 150, r: 100, ital: 0, s: 100 } },
    { id: "sign", label: "Station sign", icon: "location", fam: "sans", role: "Place names", rules: [[".sign-dest", "8.5cqi"], [".sign-name", "5.6cqi"]], def: { w: 600, d: 88, r: 0, ital: 0, s: 100 } },
  ];
  const tabs = $("#sceneTabs"), benchStyle = document.createElement("style");
  document.head.appendChild(benchStyle);
  tabs.innerHTML = SCENES.map((s, i) => `<button type="button" role="tab" id="tab-${s.id}" aria-controls="scene-${s.id}" aria-selected="${i === 0}">${symHTML(s.icon)}${s.label}</button>`).join("");
  const state = Object.fromEntries(SCENES.map((s) => [s.id, { ...s.def }]));
  let cur = SCENES[0];
  const cW = $("#cW"), cD = $("#cD"), cR = $("#cR"), cS = $("#cS"), cI = $("#cI");
  function setCtl(input, ax, v) {
    const row = input.closest(".ctl");
    if (!ax) { input.disabled = true; row.classList.add("off"); return; }
    input.disabled = false; row.classList.remove("off"); input.min = ax[0]; input.max = ax[1]; input.value = clamp(v, ax[0], ax[1]);
  }
  function syncBench() {
    const f = FAM[cur.fam], st = state[cur.id];
    setCtl(cW, f.axes.wght, st.w); setCtl(cD, f.axes.wdth, st.d); setCtl(cR, f.axes.radius, st.r); cS.value = st.s;
    cI.disabled = !f.italic; cI.setAttribute("aria-pressed", String(!!(f.italic && st.ital)));
    $("#role").innerHTML = `Editing: ${cur.role} <b>${NAMES[cur.fam]}</b>`;
    paintBench();
  }
  function paintBench() {
    const st = state[cur.id], f = FAM[cur.fam];
    st.w = +cW.value; if (!cD.disabled) st.d = +cD.value; if (!cR.disabled) st.r = +cR.value; st.s = +cS.value;
    const p = typeProps(cur.fam, st);
    benchStyle.textContent = SCENES.map((sc) => {
      const s2 = state[sc.id], p2 = cssText(typeProps(sc.fam, s2));
      return sc.rules.map(([selr, base]) => `#scene-${sc.id} ${selr} { ${p2} font-size: calc(${base} * ${s2.s / 100}); }`).join("\n");
    }).join("\n");
    $("#oW").textContent = Math.round(st.w); $("#oD").textContent = cD.disabled ? "fixed" : st.d + "%"; $("#oR").textContent = cR.disabled ? "none" : Math.round(st.r); $("#oS").textContent = st.s + "%";
    const out = [`font-family: "${NAMES[cur.fam]}";`, `font-weight: ${p["font-weight"]};`];
    if (f.axes.wdth) out.push(`font-stretch: ${parseFloat(p["font-stretch"])}%;`);
    if (st.ital && f.italic) out.push("font-style: italic;");
    if (f.axes.radius && st.r) out.push(`font-variation-settings: "${R}" ${Math.round(st.r)};`);
    $("#cssLine").innerHTML = out.map(hlCSS).join("  ");
    if (cur.id === "sign") fitSign();
    if (cur.id === "poster") fitPoster();
    if (cur.id === "code") $("#stFont").textContent = `${NAMES.mono} ${Math.round(st.w)}`;
  }
  tabs.addEventListener("click", (e) => {
    const b = e.target.closest("button"); if (!b) return;
    cur = SCENES.find((s) => "tab-" + s.id === b.id);
    $$("button", tabs).forEach((x) => x.setAttribute("aria-selected", String(x === b)));
    SCENES.forEach((s) => ($("#scene-" + s.id).hidden = s !== cur));
    syncBench();
    if (cur.id === "dash") drawChart();
  });
  tabs.addEventListener("keydown", (e) => {
    const i = SCENES.indexOf(cur), d = { ArrowRight: 1, ArrowLeft: -1 }[e.key]; if (!d) return;
    const b = $$("button", tabs)[(i + d + SCENES.length) % SCENES.length]; b.focus(); b.click();
  });
  [cW, cD, cR, cS].forEach((i) => i.addEventListener("input", paintBench));
  cI.addEventListener("click", () => { if (cI.disabled) return; state[cur.id].ital = state[cur.id].ital ? 0 : 1; syncBench(); });
  $("#cReset").addEventListener("click", () => { state[cur.id] = { ...cur.def }; syncBench(); });
  $("#cCopy").addEventListener("click", () => copy($("#cssLine").textContent.replace(/  /g, "\n"), "Copied the CSS"));

  /* ----- code editor ----- */
  const FILES = {
    "ferries.ts": `import { Pier, Route, minutes } from "../schedule";

// Next departures from a pier, soonest first
export async function nextFerries(pier: Pier, limit = 3): Promise<Route[]> {
  const now = new Date();
  const routes = await pier.routes();

  return routes
    .filter((r) => r.departs > now && r.status !== "suspended")
    .sort((a, b) => a.departs.getTime() - b.departs.getTime())
    .slice(0, limit);
}

export function waitTime(route: Route, now = new Date()): string {
  const m = minutes(route.departs, now);
  if (m <= 0) return "Boarding";
  return m === 1 ? "1 min" : \`\${m} min\`;
}

// Central Pier 6: 0O 1lI {} [] => !== <= >=
export const CENTRAL_6 = { id: "CPR6", lat: 22.2873, lng: 114.1617 };`,
    "schedule.ts": `export type Status = "on-time" | "delayed" | "suspended";

export interface Route {
  id: string;
  from: string;
  to: string;
  departs: Date;
  status: Status;
}

export interface Pier {
  id: string;
  name: string;
  routes(): Promise<Route[]>;
}

// Whole minutes between two times, rounded up
export function minutes(a: Date, b: Date): number {
  return Math.ceil((a.getTime() - b.getTime()) / 60000);
}`,
    "package.json": `{
  "name": "harbour-api",
  "version": "1.4.0",
  "private": true,
  "scripts": {
    "test": "vitest run",
    "dev": "tsx watch src/server.ts"
  },
  "dependencies": {
    "hono": "4.6.3"
  }
}`,
  };
  const TREE = [["dir", "src", 0], ["dir", "routes", 1], ["file", "ferries.ts", 2], ["file", "schedule.ts", 2], ["dir", "tests", 0], ["file", "ferries.test.ts", 1], ["file", "package.json", 0], ["file", "README.md", 0]];
  let openTabs = ["ferries.ts", "schedule.ts"], curFile = "ferries.ts", curLine = 4;
  const KW = /\b(import|from|export|async|function|const|let|return|if|await|type|interface|new|true|false)\b/;
  function hl(line) {
    const re = /(\/\/.*$)|("(?:[^"\\]|\\.)*"|`(?:[^`\\]|\\.)*`)|(\b\d+(?:\.\d+)?\b)|([A-Za-z_$][\w$]*)(?=\s*\()|(\b[A-Z][A-Za-z0-9_]*\b)|([A-Za-z_$][\w$]*)/g;
    let out = "", last = 0, m;
    while ((m = re.exec(line))) {
      out += esc(line.slice(last, m.index)); last = re.lastIndex;
      const t = m[0];
      if (m[1]) out += `<span class="c">${esc(t)}</span>`;
      else if (m[2]) out += `<span class="s">${esc(t)}</span>`;
      else if (m[3]) out += `<span class="n">${t}</span>`;
      else if (KW.test(t) && (m[4] || m[6])) out += `<span class="k">${t}</span>`;
      else if (m[4]) out += `<span class="f">${t}</span>`;
      else if (m[5]) out += `<span class="t">${t}</span>`;
      else out += KW.test(t) ? `<span class="k">${t}</span>` : esc(t);
    }
    return out + esc(line.slice(last));
  }
  function renderCode() {
    const lines = FILES[curFile].split("\n");
    curLine = clamp(curLine, 1, lines.length);
    $("#ideCode").innerHTML = lines.map((l, i) => `<div class="row${i + 1 === curLine ? " cur" : ""}" data-l="${i + 1}"><span class="ln">${i + 1}</span><span class="cd">${hl(l)}${i + 1 === curLine ? '<span class="caret"></span>' : ""}</span></div>`).join("");
    $("#stPos").textContent = `Ln ${curLine}, Col ${lines[curLine - 1].length + 1}`;
    $("#ideTabs").innerHTML = openTabs.map((f) => `<button type="button" class="${f === curFile ? "on" : ""}" data-f="${f}">${symHTML("code-file")}${f}</button>`).join("");
    $("#tree").innerHTML = TREE.map(([k, n, lv]) => `<li class="${k}${n === curFile ? " on" : ""}" data-f="${k === "file" ? n : ""}" style="padding-left:${14 + lv * 14}px">${symHTML(k === "dir" ? "folder" : "code-file")}${n}</li>`).join("");
    paintSyms($("#scene-code"));
  }
  function openFile(f) {
    if (!FILES[f]) { say(`${f} is not part of this demo. Try ferries.ts, schedule.ts or package.json.`); return; }
    if (!openTabs.includes(f)) openTabs.push(f);
    curFile = f; curLine = 1; renderCode();
  }
  $("#tree").addEventListener("click", (e) => { const li = e.target.closest("li"); if (li && li.dataset.f) openFile(li.dataset.f); });
  $("#ideTabs").addEventListener("click", (e) => { const b = e.target.closest("button"); if (b) openFile(b.dataset.f); });
  $("#ideCode").addEventListener("click", (e) => { const r = e.target.closest(".row"); if (r) { curLine = +r.dataset.l; renderCode(); } });
  $("#ideCode").addEventListener("keydown", (e) => { const d = { ArrowDown: 1, ArrowUp: -1 }[e.key]; if (d) { e.preventDefault(); curLine += d; renderCode(); } });
  function terminal() {
    const rows = [["Central to Tsim Sha Tsui", 412, "99.1%"], ["Wan Chai to Hung Hom", 188, "97.4%"], ["Central to Mui Wo", 64, "98.0%"], ["Central to Peng Chau", 0, "n/a"]];
    const w = [26, 7, 9], line = (l, m, r) => l + w.map((n) => "─".repeat(n)).join(m) + r;
    const cell = (a, b, c) => `│ ${String(a).padEnd(w[0] - 2)} │ ${String(b).padStart(w[1] - 2)} │ ${String(c).padStart(w[2] - 2)} │`;
    $("#term").innerHTML = [
      `<span class="pr">~/harbour-api</span> <span class="dim">main</span> $ npm test`, "",
      ` <span class="ok">PASS</span>  tests/ferries.test.ts <span class="dim">(0.84 s)</span>`,
      line("┌", "┬", "┐"), cell("route", "trips", "on time"), line("├", "┼", "┤"),
      ...rows.map((r) => cell(...r)), line("└", "┴", "┘"),
      ` Tests  <span class="ok">12 passed</span> <span class="dim">(12)</span>`,
    ].join("\n");
  }
  renderCode(); terminal();

  /* ----- dashboard ----- */
  const wave = (n, base, amp, peaks, seed) => Array.from({ length: n }, (_, i) => Math.round(base + amp * peaks.reduce((s, [c, wd, h]) => s + h * Math.exp(-(((i - c) / wd) ** 2)), 0) + 6 * Math.sin(i * 1.7 + seed)));
  const DATA = {
    day: { labels: Array.from({ length: 18 }, (_, i) => `${String(6 + i).padStart(2, "0")}:00`),
      a: wave(18, 38, 70, [[2.5, 1.6, 1], [12, 1.8, 0.92]], 1), b: wave(18, 36, 66, [[2.5, 1.6, 1], [12, 1.8, 0.85]], 3),
      kpi: [["Crossings", "1,284", "+3.2%", 1], ["On time", "98.6%", "+0.4 pt", 1], ["Passengers", "152,940", "+5.1%", 1], ["Average wait", "4.1 min", "−0.3 min", 1]],
      routes: [["Central to Tsim Sha Tsui", 412], ["Wan Chai to Hung Hom", 188], ["Central to Cheung Chau", 102], ["Central to Mui Wo", 64], ["Central to Lamma", 58]] },
    week: { labels: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
      a: [1240, 1262, 1251, 1288, 1340, 1495, 1436], b: [1218, 1240, 1236, 1260, 1302, 1452, 1410],
      kpi: [["Crossings", "9,312", "+2.4%", 1], ["On time", "97.9%", "−0.3 pt", 0], ["Passengers", "1,031,400", "+3.8%", 1], ["Average wait", "4.6 min", "+0.2 min", 0]],
      routes: [["Central to Tsim Sha Tsui", 2884], ["Wan Chai to Hung Hom", 1316], ["Central to Cheung Chau", 714], ["Central to Mui Wo", 448], ["Central to Lamma", 406]] },
    month: { labels: Array.from({ length: 30 }, (_, i) => String(i + 1)),
      a: wave(30, 1240, 260, [[5, 1, 0.5], [12, 1, 0.6], [19, 1, 0.55], [26, 1, 0.7]], 2), b: wave(30, 1220, 240, [[5, 1, 0.5], [12, 1, 0.55], [19, 1, 0.5], [26, 1, 0.62]], 5),
      kpi: [["Crossings", "38,240", "+1.9%", 1], ["On time", "98.2%", "+0.1 pt", 1], ["Passengers", "4,412,800", "+4.4%", 1], ["Average wait", "4.4 min", "−0.1 min", 1]],
      routes: [["Central to Tsim Sha Tsui", 12360], ["Wan Chai to Hung Hom", 5640], ["Central to Cheung Chau", 3060], ["Central to Mui Wo", 1920], ["Central to Lamma", 1740]] },
  };
  const TABLE = [
    { route: "Central to Tsim Sha Tsui", trips: 412, ontime: 99.1, wait: 3.2, st: ["ok", "On time"] },
    { route: "Wan Chai to Hung Hom", trips: 188, ontime: 97.4, wait: 4.8, st: ["warn", "Minor delays"] },
    { route: "Central to Cheung Chau", trips: 102, ontime: 98.8, wait: 5.1, st: ["ok", "On time"] },
    { route: "Central to Mui Wo", trips: 64, ontime: 98.0, wait: 6.4, st: ["ok", "On time"] },
    { route: "Central to Peng Chau", trips: 0, ontime: 0, wait: 0, st: ["bad", "Suspended"] },
  ];
  let period = "day", sortK = "trips", sortDir = -1;
  function renderDash() {
    const D = DATA[period];
    $("#kpis").innerHTML = D.kpi.map(([l, v, d, good]) => `<div class="kpi"><p>${l}</p><p class="num t-main">${v}</p><span class="delta ${good ? "up" : "down"}">${d}</span></div>`).join("");
    const max = Math.max(...D.routes.map((r) => r[1]));
    $("#routeBars").innerHTML = D.routes.map(([n, v]) => `<div class="rb"><div class="rb-t"><span>${n}</span><b>${v.toLocaleString("en")}</b></div><div class="rb-bar"><i style="width:${(v / max) * 100}%"></i></div></div>`).join("");
    const rows = [...TABLE].sort((a, b) => (a[sortK] > b[sortK] ? 1 : a[sortK] < b[sortK] ? -1 : 0) * sortDir);
    $("#table tbody").innerHTML = rows.map((r) => `<tr><td>${r.route}</td><td>${r.trips || "–"}</td><td>${r.ontime ? r.ontime.toFixed(1) + "%" : "–"}</td><td>${r.wait ? r.wait.toFixed(1) + " min" : "–"}</td><td><span class="pill ${r.st[0]}">${r.st[1]}</span></td></tr>`).join("");
    $$("#table th button").forEach((b) => { if (b.dataset.k === sortK) b.setAttribute("aria-sort", sortDir > 0 ? "ascending" : "descending"); else b.removeAttribute("aria-sort"); });
    drawChart();
  }
  function drawChart() {
    const svg = $("#lineChart"); if (!svg || $("#scene-dash").hidden) return;
    const D = DATA[period], W = svg.clientWidth || 600, Hh = svg.clientHeight || 210, padL = 40, padB = 22, padT = 8, padR = 8;
    const all = [...D.a, ...D.b], lo = 0, hi = Math.ceil(Math.max(...all) * 1.12 / 10) * 10;
    const X = (i) => padL + (i / (D.a.length - 1)) * (W - padL - padR), Y = (v) => padT + (1 - (v - lo) / (hi - lo)) * (Hh - padT - padB);
    const path = (arr) => arr.map((v, i) => `${i ? "L" : "M"}${X(i).toFixed(1)},${Y(v).toFixed(1)}`).join("");
    let g = "";
    for (let k = 0; k <= 4; k++) { const v = lo + (hi - lo) * k / 4, y = Y(v); g += `<line class="grid" x1="${padL}" x2="${W - padR}" y1="${y}" y2="${y}"/><text class="ax" x="${padL - 6}" y="${y + 4}" text-anchor="end">${Math.round(v).toLocaleString("en")}</text>`; }
    const every = Math.ceil(D.labels.length / 7);
    D.labels.forEach((l, i) => { if (i % every === 0) g += `<text class="ax" x="${X(i)}" y="${Hh - 6}" text-anchor="middle">${l}</text>`; });
    g += `<path class="area" d="${path(D.a)}L${X(D.a.length - 1)},${Y(lo)}L${X(0)},${Y(lo)}Z"/><path class="lb" d="${path(D.b)}"/><path class="la" d="${path(D.a)}"/>`;
    g += `<line class="cross" id="cross" y1="${padT}" y2="${Hh - padB}" x1="-10" x2="-10"/><circle class="pt" id="pt" r="5" cx="-10" cy="-10"/>`;
    svg.setAttribute("viewBox", `0 0 ${W} ${Hh}`); svg.innerHTML = g;
    svg.onpointermove = (e) => {
      const b = svg.getBoundingClientRect(), i = clamp(Math.round(((e.clientX - b.left) - padL) / (W - padL - padR) * (D.a.length - 1)), 0, D.a.length - 1);
      $("#cross").setAttribute("x1", X(i)); $("#cross").setAttribute("x2", X(i)); $("#pt").setAttribute("cx", X(i)); $("#pt").setAttribute("cy", Y(D.a[i]));
      const tip = $("#tooltip"); tip.hidden = false;
      tip.innerHTML = `<b>${period === "month" ? "Day " : ""}${D.labels[i]}</b><br>${D.a[i].toLocaleString("en")} this period<br>${D.b[i].toLocaleString("en")} last period`;
      tip.style.left = clamp(X(i) + 12, 0, W - 150) + "px";
    };
    svg.onpointerleave = () => { $("#tooltip").hidden = true; $("#pt").setAttribute("cx", -10); $("#cross").setAttribute("x1", -10); $("#cross").setAttribute("x2", -10); };
  }
  $("#period").addEventListener("click", (e) => { const b = e.target.closest("button"); if (!b) return; period = b.dataset.p; $$("#period button").forEach((x) => x.setAttribute("aria-checked", String(x === b))); renderDash(); });
  $("#table thead").addEventListener("click", (e) => { const b = e.target.closest("button"); if (!b) return; if (sortK === b.dataset.k) sortDir = -sortDir; else { sortK = b.dataset.k; sortDir = b.dataset.k === "route" ? 1 : -1; } renderDash(); });
  renderDash();

  /* ----- reading app ----- */
  const ARTICLE = {
    en: { t: "The harbour that never sleeps", by: "Story by Wing Chan, 18 November 2026", time: "4 min read", p: [
      "Just after midnight the last commuter ferry ties up at Central and the night shift begins. Tugs push container barges toward the western anchorage, a pilot boat waits off Green Island, and the harbour control room watches all of it on a wall of screens.",
      "“You learn the water by its sounds,” says the duty officer, who has worked nights for eleven years. “When it is quiet, something is about to change.”",
      "By four the fishing boats from Aberdeen are already moving, and the first ferry crews arrive to check engines, ropes and life jackets. Nobody hurries. The timetable starts at six, and it has not been late in months.",
      "Then the sun comes up over Lei Yue Mun, the water turns from grey to blue, and the city takes the harbour back."] },
  };
  function renderArticle(l) {
    const a = ARTICLE[l];
    $("#readTitle").textContent = a.t; $("#readBy").textContent = a.by; $("#readTime").textContent = a.time;
    $("#readBody").innerHTML = a.p.map((p) => `<p>${esc(p)}</p>`).join("");
    $("#scene-read .reader-page").lang = l;
  }
  renderArticle("en");

  /* ----- assistant chat ----- */
  const log = $("#chatLog");
  const botTools = `<div class="msg-tools"><button type="button" aria-label="Copy reply">${symHTML("copy")}</button><button type="button" aria-label="Good reply">${symHTML("thumbs-up")}</button><button type="button" aria-label="Try again">${symHTML("regenerate")}</button></div>`;
  function addMsg(who, html) {
    const d = document.createElement("div");
    d.className = "msg " + who;
    d.innerHTML = who === "you" ? html : `<span class="av">${symHTML("agent")}</span><div class="bt">${html}${botTools}</div>`;
    log.appendChild(d); log.scrollTop = log.scrollHeight; return d;
  }
  const REPLIES = [
    [/pier|wheelchair|access/i, "<p>Central Pier 6 has step-free access from the footbridge, and lifts to both decks. Staff can set up a boarding ramp if you ask at the counter.</p>"],
    [/weather|typhoon|rain|signal/i, "<p>Ferries keep running under Signal No. 1 and usually under Signal No. 3, with fewer trips. When Signal No. 8 is announced, most outlying-island services stop about two hours later.</p>"],
    [/fare|price|cost|octopus/i, "<p>An ordinary ferry to Mui Wo costs less on weekdays than on Sundays and holidays. Fast ferries cost about twice as much. Octopus cards work at every pier.</p><pre>Ordinary  Mon–Sat   standard\nOrdinary  Sun, hol  + about 50%\nFast      any day   about 2×</pre>"],
  ];
  function reply(q) {
    const hit = REPLIES.find(([re]) => re.test(q));
    return hit ? hit[1] : "<p>Here are the next departures from Central Pier 6. Times can change in bad weather, so check the board before you board.</p><pre>Route        Departs  Type\nMui Wo       21:40    ordinary\nMui Wo       22:30    fast\nMui Wo       23:30    ordinary</pre>";
  }
  addMsg("you", "When is the last ferry to Mui Wo tonight?");
  addMsg("bot", "<p>The last one leaves Central Pier 6 at <b>23:30</b>. On Fridays there is also a late fast ferry:</p><pre>Day  Departs  Type   Time\nFri  00:30    fast   40 min\nSat  23:30    slow   55 min</pre><p>Ask me about piers, fares or the weather.</p>");
  $("#composer").addEventListener("submit", (e) => {
    e.preventDefault(); const inp = $("#msg"), q = inp.value.trim(); if (!q) return; inp.value = "";
    addMsg("you", esc(q));
    const typing = addMsg("bot", "<p>…</p>");
    setTimeout(() => { $(".bt", typing).innerHTML = reply(q) + botTools; log.scrollTop = log.scrollHeight; }, reduce.matches ? 0 : 650);
  });
  log.addEventListener("click", (e) => { const b = e.target.closest(".msg-tools button"); if (!b) return; if (b.getAttribute("aria-label") === "Copy reply") copy(b.closest(".bt").innerText.trim(), "Copied the reply"); else say("Thanks, noted"); });

  /* ----- poster ----- */
  const po = $("#po");
  $("#swatches").addEventListener("click", (e) => { const b = e.target.closest("button"); if (!b) return; po.dataset.c = b.dataset.c; $$("#swatches button").forEach((x) => x.classList.toggle("on", x === b)); });
  $("#poLayout").addEventListener("click", (e) => { const b = e.target.closest("button"); if (!b) return; po.classList.toggle("line", b.dataset.a === "line"); $$("#poLayout button").forEach((x) => x.setAttribute("aria-checked", String(x === b))); fitPoster(); });
  $("#poH").addEventListener("keydown", (e) => { if (e.key === "Enter") e.preventDefault(); });
  // the headline shrinks until its longest word (or, on one line, the whole line) fits the poster
  const poProbe = document.createElement("span");
  Object.assign(poProbe.style, { position: "absolute", visibility: "hidden", whiteSpace: "nowrap", left: "-9999px", top: "0" });
  function fitPoster() {
    const h = $("#poH"); h.style.removeProperty("font-size");
    const one = po.classList.contains("line"), cs = getComputedStyle(h);
    const text = one ? h.textContent : (h.textContent.split(/\s+/).sort((a, b) => b.length - a.length)[0] || "W");
    po.appendChild(poProbe);
    ["fontFamily", "fontWeight", "fontStretch", "fontStyle", "fontVariationSettings", "fontSize", "letterSpacing"].forEach((k) => (poProbe.style[k] = cs[k]));
    poProbe.textContent = text;
    const need = poProbe.getBoundingClientRect().width, have = h.clientWidth;
    if (need > have && have > 0) h.style.fontSize = parseFloat(cs.fontSize) * have / need * 0.97 + "px";
    poProbe.remove();
  }
  $("#poH").addEventListener("input", fitPoster);

  /* ----- station sign ----- */
  const ZH = { "central": "中環", "tsim sha tsui": "尖沙咀", "tsim sha tsui east": "尖東", "hong kong station": "香港", "hong kong international airport": "香港國際機場", "admiralty": "金鐘", "mui wo": "梅窩", "wan chai": "灣仔" };
  const dest = $("#signDest"), destIn = $("#destIn"), fitW = $("#fitW");
  function fitSign() {
    const st = state.sign, base = typeProps("sans", st);
    [dest, ...$$(".sign-name")].forEach((el) => el.style.removeProperty("font-stretch"));
    if (!fitW.checked || !SAX.wdth) { $("#signNote").textContent = "Long names are cut off when they do not fit."; return; }
    let note = "Every name fits at the chosen width.";
    [dest, ...$$(".sign-name")].forEach((el) => {
      if (el.scrollWidth <= el.clientWidth + 1) return;
      let lo = WD[0], hi = parseFloat(base["font-stretch"]);
      for (let i = 0; i < 12; i++) { const mid = (lo + hi) / 2; el.style.fontStretch = mid + "%"; if (el.scrollWidth <= el.clientWidth + 1) lo = mid; else hi = mid; }
      el.style.fontStretch = lo + "%";
      if (el === dest) note = el.scrollWidth > el.clientWidth + 1 ? `This name is too long even at ${Math.round(WD[0])}% width. Use a shorter name or a smaller size.` : `Width set to ${Math.round(lo)}% so “${el.textContent}” fits without a smaller size.`;
    });
    $("#signNote").textContent = note;
  }
  function setDest(v) { dest.textContent = v || " "; $("#signZh").textContent = ZH[v.trim().toLowerCase()] || ""; fitSign(); }
  destIn.addEventListener("input", () => setDest(destIn.value));
  fitW.addEventListener("change", fitSign);
  $(".sign-try").addEventListener("click", (e) => { const b = e.target.closest("button"); if (!b) return; destIn.value = b.dataset.d; setDest(b.dataset.d); });

  /* =========================================================================================
     4. Symbols
     ========================================================================================= */
  const grid = $("#symGrid"), search = $("#symSearch"), count = $("#symCount"), symW = $("#symW"), more = $("#symMore");
  grid.innerHTML = window.SYMBOLS.map(([n, l]) => `<button type="button" data-n="${n}" aria-pressed="false" aria-label="${l}">${symHTML(n)}<small>${n}</small></button>`).join("");
  const btns = $$("button", grid);
  let chosen = "heart-filled", showAll = false;
  const firstCount = () => Math.max(1, getComputedStyle(grid).gridTemplateColumns.split(" ").length) * 4;
  function inspect(n) {
    const s = SYM.get(n);
    $("#symBig").setAttribute("data-char", ch(n)); $("#symName").textContent = n; $("#symLabel").textContent = `${s.label}, in ${s.cat}`;
    $("#symWeights").innerHTML = [400, 500, 700].map((w) => `<span><i class="sym" style="font-weight:${w}" data-char="${ch(n)}"></i><small>${w}</small></span>`).join("");
    $("#symInline").innerHTML = [400, 500, 700].map((w) => `<span style="font-weight:${w}"><i class="sym" style="font-weight:${w}" data-char="${ch(n)}"></i>${s.label}</span>`).join("");
  }
  function choose(n) { chosen = n; inspect(n); btns.forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.n === n))); }
  function filterSyms() {
    const q = search.value.trim().toLowerCase(); let shown = 0; const fc = firstCount();
    btns.forEach((b, i) => { const s = SYM.get(b.dataset.n), hay = `${s.name} ${s.label} ${s.cat} ${s.tags}`.toLowerCase(); const ok = q ? q.split(/\s+/).every((w) => hay.includes(w)) : showAll || i < fc; b.hidden = !ok; if (ok) shown++; });
    more.hidden = !!q || showAll;
    count.textContent = q ? (shown ? `${shown} of ${btns.length} match “${search.value.trim()}”` : `Nothing matches “${search.value.trim()}”. Try a shorter word, such as file or user.`) : `${shown} of ${btns.length}`;
  }
  search.addEventListener("input", filterSyms);
  more.addEventListener("click", () => { const n = firstCount(); showAll = true; filterSyms(); btns[n] && btns[n].focus(); });
  grid.addEventListener("click", (e) => { const b = e.target.closest("button"); if (b) choose(b.dataset.n); });
  grid.addEventListener("pointerover", (e) => { const b = e.target.closest("button"); if (b && matchMedia("(hover: hover)").matches) inspect(b.dataset.n); });
  grid.addEventListener("pointerleave", () => inspect(chosen));
  $("#symCopy").addEventListener("click", () => copy(chosen, `Copied ${chosen}`));
  symW.addEventListener("input", () => { $("#symbols").style.setProperty("--symW", symW.value); $("#oSW").textContent = symW.value; });
  choose(chosen); filterSyms();
  addEventListener("resize", () => { if (!showAll && !search.value) filterSyms(); });

  /* =========================================================================================
     5. Characters
     ========================================================================================= */
  const CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789&@#%?!*()[]{}$€£¥₫" +
    "ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÑÒÓÔÕÖØÙÚÛÜÝßàáâãäåæçèéêëìíîïñòóôõöøùúûüýÿ" +
    "ĀāĂăĄąĆćČčĎďĐđĒēĘęĚěĞğĪīİıŁłŃńŇňŌōŐőŒœŘřŚśŠšŤťŪūŮůŰűŸŹźŻżŽž" +
    "ẠạẢảẤấẦầẨẩẪẫẬậẮắẰằẲẳẴẵẶặẸẹẺẻẼẽẾếỀềỂểỄễỆệỈỉỊịỌọỎỏỐốỒồỔổỖỗỘộỚớỜờỞởỠỡỢợỤụỦủỨứỪừỬửỮữỰựỲỳỴỵỶỷỸỹƠơƯư" + "ǍǎǏǐǑǒǓǔǕǖǗǘǙǚǛǜ";
  const hex = (c) => "U+" + c.codePointAt(0).toString(16).toUpperCase().padStart(4, "0");
  const gGrid = $("#gGrid"), gBig = $("#gBig"), gInfo = $("#gInfo"), gStage = $("#gStage");
  gGrid.innerHTML = [...CHARS].map((c) => `<button type="button" aria-label="${c}, ${hex(c)}">${c}</button>`).join("");
  let G = { w: 400, d: 100 };
  const paintG = () => { apply(gBig, "sans", G); gInfo.textContent = `${hex(gBig.textContent)}   weight ${Math.round(G.w)}   width ${Math.round(G.d)}%`; };
  function showG(b) { gBig.textContent = b.textContent; $$("button[aria-pressed]", gGrid).forEach((x) => x.removeAttribute("aria-pressed")); b.setAttribute("aria-pressed", "true"); paintG(); }
  gGrid.addEventListener("pointerover", (e) => { const b = e.target.closest("button"); if (b) showG(b); });
  gGrid.addEventListener("focusin", (e) => { const b = e.target.closest("button"); if (b) showG(b); });
  gStage.addEventListener("pointermove", (e) => { const b = gStage.getBoundingClientRect(); G = { w: lerp(WG[1], WG[0], clamp((e.clientY - b.top) / b.height, 0, 1)), d: lerp(WD[0], WD[1], clamp((e.clientX - b.left) / b.width, 0, 1)) }; paintG(); });
  paintG();
  $("#gMore").addEventListener("click", () => { gGrid.classList.add("all"); gGrid.children[70] && gGrid.children[70].focus(); });

  /* ---------- install tabs, footer ---------- */
  // Syntax colours for the install code (HTML, Swift, Kotlin, Dart), with the same token classes as the editor
  const LANG = {
    web: { kw: /^(?:var)$/ },
    ios: { kw: /^(?:import|let|var|func|struct|return|true|false)$/ },
    android: { kw: /^(?:import|val|var|fun|return|true|false|null|as)$/ },
    flutter: { kw: /^(?:import|const|final|var|return|true|false|new)$/ },
  };
  function hlHTML(src) {
    const re = /(<\/?)([\w-]+)|([\w-]+)(?==)|("[^"]*")|(\/?>)/g; let out = "", last = 0, m;
    while ((m = re.exec(src))) {
      out += esc(src.slice(last, m.index)); last = re.lastIndex;
      if (m[2]) out += `<span class="p">${esc(m[1])}</span><span class="k">${m[2]}</span>`;
      else if (m[3]) out += `<span class="t">${m[3]}</span>`;
      else if (m[4]) out += `<span class="s">${esc(m[4]).replace(/var\((--[\w-]+)\)/g, '<span class="f">var</span>(<span class="m">$1</span>)')}</span>`;
      else out += `<span class="p">${esc(m[5])}</span>`;
    }
    return out + esc(src.slice(last));
  }
  function hlLang(src, kw) {
    const re = /(\/\/.*$)|("[^"\n]*"|'[^'\n]*')|(\b\d+(?:\.\d+)?)|(\.[a-z][\w]*)|([A-Za-z_]\w*)(?=\s*\()|(\b[A-Z]\w*)|([a-z_]\w*)(?=\s*[:=](?!=))|([A-Za-z_]\w*)/gm;
    let out = "", last = 0, m;
    while ((m = re.exec(src))) {
      out += esc(src.slice(last, m.index)); last = re.lastIndex; const t = m[0];
      if (m[1]) out += `<span class="c">${esc(t)}</span>`;
      else if (m[2]) out += `<span class="s">${esc(t)}</span>`;
      else if (m[3]) out += `<span class="n">${t}</span>`;
      else if (kw.test(t.replace(/^\./, "")) && !m[4]) out += `<span class="k">${t}</span>`;
      else if (m[4]) out += `.<span class="m">${t.slice(1)}</span>`;
      else if (m[5]) out += `<span class="f">${t}</span>`;
      else if (m[6]) out += `<span class="t">${t}</span>`;
      else if (m[7]) out += `<span class="a">${t}</span>`;
      else out += esc(t);
    }
    return out + esc(src.slice(last));
  }
  function hlCSS(decl) { // one "property: value;" declaration
    const m = decl.match(/^([\w-]+)(:\s*)(.*?)(;?)$/); if (!m) return esc(decl);
    const val = esc(m[3]).replace(/(&quot;|")(.*?)\1/g, '<span class="vs">"$2"</span>').replace(/(-?\d+(?:\.\d+)?%?)(?![^<]*<\/span>)/g, '<span class="vn">$1</span>');
    return `<span class="vp">${m[1]}</span>${m[2]}${val}${m[4]}`;
  }
  Object.keys(LANG).forEach((k) => { const code = $(`#p-${k} code`); const src = code.textContent;
    code.innerHTML = k === "web" ? hlHTML(src) : hlLang(src, LANG[k].kw); });
  const ptabs = $$('#get [role="tab"]');
  ptabs.forEach((t) => t.addEventListener("click", () => ptabs.forEach((x) => { const on = x === t; x.setAttribute("aria-selected", String(on)); $("#" + x.getAttribute("aria-controls")).hidden = !on; })));
  $("#standin").textContent = T.standinNote || "";
  const foot = $(".foot"), footWord = $(".foot-word");
  if (SAX.radius) footWord.style.fontVariationSettings = `"${R}" ${RD[1]}`;
  // The footer word is sized once, at its widest and heaviest, so it never changes height;
  // the pointer then changes only its width and weight.
  function footFit() {
    const keep = [footWord.style.fontStretch, footWord.style.fontWeight];
    footWord.style.fontStretch = WD[1] + "%"; footWord.style.fontWeight = WG[1]; footWord.style.fontSize = "100px";
    const w = footWord.getBoundingClientRect().width, cs = getComputedStyle(foot);
    const avail = foot.clientWidth - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight);
    footWord.style.fontSize = (avail / w) * 100 * 0.995 + "px";
    [footWord.style.fontStretch, footWord.style.fontWeight] = keep;
  }
  foot.addEventListener("pointermove", (e) => {
    const b = foot.getBoundingClientRect();
    footWord.style.fontStretch = lerp(WD[0], WD[1], clamp((e.clientX - b.left) / b.width, 0, 1)) + "%";
    footWord.style.fontWeight = Math.round(lerp(WG[1], WG[0] + 200, clamp((e.clientY - b.top) / b.height, 0, 1)));
  });
  foot.addEventListener("pointerleave", () => { footWord.style.fontStretch = ""; footWord.style.fontWeight = ""; });

  /* ---------- start ---------- */
  function layout() { footFit(); rulerLabels(); paintHero(); paintSplit(); measureSplit(); drawChart(); if (cur.id === "sign") fitSign(); if (cur.id === "poster") fitPoster(); }
  const released = Promise.all(['400 20px "Admiralty Sans Released"', '400 20px "Admiralty Serif Released"'].map((f) => document.fonts.load(f)));
  syncBench();
  Promise.all([document.fonts.ready, released]).then(() => { layout(); heroIntro(); });
  let rz; addEventListener("resize", () => { clearTimeout(rz); rz = setTimeout(layout, 120); });
})();
