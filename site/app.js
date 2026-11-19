(() => {
  "use strict";
  const T = window.TYPE;
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const reduce = matchMedia("(prefers-reduced-motion: reduce)");
  const clamp = (v, a, b) => Math.min(b, Math.max(a, v));
  const lerp = (a, b, t) => a + (b - a) * t;
  const R = T.radiusTag;
  const SANS = T.families.sans, sax = SANS.axes;
  const WG = sax.wght, WD = sax.wdth || [100, 100], RD = sax.radius || [0, 0];

  /* ---------- type helpers ---------- */
  // Weight and width use the standard CSS properties; radius and slant use
  // font-variation-settings (custom or extra axes).
  function typeStyle(famKey, s) {
    const f = T.families[famKey], ax = f.axes, out = { fontFamily: f.css };
    out.fontWeight = String(Math.round(clamp(s.w ?? 400, ...(ax.wght || [400, 400]))));
    out.fontStretch = (ax.wdth ? clamp(s.d ?? 100, ...ax.wdth) : 100).toFixed(1) + "%";
    const fvs = [];
    if (ax.radius) fvs.push(`"${R}" ${Math.round(clamp(s.r ?? 0, ...ax.radius))}`);
    const ital = s.ital || 0;
    out.fontStyle = f.italic === "face" && ital > 0.5 ? "italic" : "normal";
    if (f.italic === "slnt") fvs.push(`"slnt" ${(f.slnt * ital).toFixed(2)}`);
    out.fontVariationSettings = fvs.length ? fvs.join(", ") : "normal";
    return out;
  }
  const apply = (el, famKey, s) => Object.assign(el.style, typeStyle(famKey, s));
  const onScreen = (el) => { const b = el.getBoundingClientRect(); return b.bottom > 0 && b.top < innerHeight; };

  /* ---------- symbols as glyphs ---------- */
  const SYM = new Map(window.SYMBOLS.map(([name, label, cp, cat, tags]) => [name, { name, label, cp, cat, tags }]));
  const symChar = (n) => (SYM.has(n) ? String.fromCodePoint(SYM.get(n).cp) : "");
  const paintSyms = (root = document) => $$("[data-sym]", root).forEach((el) => el.setAttribute("data-char", symChar(el.dataset.sym)));
  paintSyms();

  /* ---------- toast and copy ---------- */
  const toast = $("#toast");
  let toastT;
  function say(msg) {
    toast.textContent = msg; toast.classList.add("show");
    clearTimeout(toastT); toastT = setTimeout(() => toast.classList.remove("show"), 1800);
  }
  async function copy(text, msg) {
    try { await navigator.clipboard.writeText(text); say(msg); }
    catch { say("Copy is blocked here. Select the text and copy it yourself."); }
  }

  /* ---------- theme ---------- */
  const themeBtn = $("#theme"), root = document.documentElement;
  const isDark = () => (root.dataset.theme ? root.dataset.theme === "dark" : matchMedia("(prefers-color-scheme: dark)").matches);
  function paintTheme() {
    $(".sym", themeBtn).dataset.sym = isDark() ? "light-mode" : "dark-mode";
    paintSyms(themeBtn);
    themeBtn.setAttribute("aria-label", isDark() ? "Switch to day colours" : "Switch to night colours");
  }
  try { const t = localStorage.getItem("adm-theme"); if (t) root.dataset.theme = t; } catch {}
  themeBtn.addEventListener("click", () => {
    root.dataset.theme = isDark() ? "light" : "dark";
    try { localStorage.setItem("adm-theme", root.dataset.theme); } catch {}
    paintTheme();
  });
  paintTheme();
  const top = $(".top");
  addEventListener("scroll", () => top.classList.toggle("scrolled", scrollY > $("#hero").offsetHeight - 70), { passive: true });

  /* ---------- magnetic words: each letter reacts to the pointer ---------- */
  // base: settings far from the pointer; peak: settings right under it.
  function magnetic(wordEl, stageEl, opts) {
    const text = wordEl.textContent;
    wordEl.textContent = "";
    const letters = [...text].map((c) => {
      const s = document.createElement("span"); s.className = "ch"; s.textContent = c; s.setAttribute("aria-hidden", "true");
      wordEl.appendChild(s); return { el: s, w: opts.base.w, d: opts.base.d, tw: opts.base.w, td: opts.base.d, cx: 0 };
    });
    const st = { px: null, py: 0.5, r: 0, idle: true, raf: 0, size: 100, t0: performance.now(), focus: -1 };
    function measure(set) {
      letters.forEach((L) => apply(L.el, "sans", { w: set.w, d: set.d, r: st.r }));
      wordEl.style.fontSize = "100px";
      return wordEl.getBoundingClientRect().width;
    }
    function fit() {
      // size so that the base word plus about three letters at peak still fits the width
      const wb = measure(opts.base), wp = measure(opts.peak);
      const worst = wb + (wp - wb) * Math.min(1, 2.2 / letters.length);
      const cs = getComputedStyle(stageEl);
      const avail = stageEl.clientWidth - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight);
      st.size = st.maxSize = Math.min((avail / worst) * 100, opts.maxH ? opts.maxH() : 1e9);
      st.avail = avail;
      wordEl.style.fontSize = st.size + "px";
      letters.forEach((L) => apply(L.el, "sans", { w: L.w, d: L.d, r: st.r }));
      centers();
    }
    function centers() {
      const b = stageEl.getBoundingClientRect();
      letters.forEach((L) => { const r = L.el.getBoundingClientRect(); L.cx = (r.left + r.width / 2 - b.left) / b.width; });
    }
    function targets(now) {
      let px = st.px;
      if (st.focus >= 0) px = letters[st.focus].cx;
      else if (px === null) {
        // idle: a slow swell travels along the word
        if (reduce.matches) { letters.forEach((L) => { L.tw = opts.rest.w; L.td = opts.rest.d; }); return; }
        px = 0.5 + 0.62 * Math.sin((now - st.t0) / 2600);
      }
      const spread = opts.spread / letters.length;
      const lift = st.px === null && st.focus < 0 ? 0.75 : lerp(1, 0.55, st.py);   // higher pointer, heavier peak
      letters.forEach((L) => {
        const f = Math.exp(-(((L.cx - px) / spread) ** 2));
        L.tw = lerp(opts.base.w, lerp(opts.base.w, opts.peak.w, lift), f);
        L.td = lerp(opts.base.d, opts.peak.d, f);
      });
    }
    let nearest = 0;
    function frame(now) {
      targets(now);
      let moving = st.px === null && st.focus < 0 && !reduce.matches, best = 1e9;
      letters.forEach((L, i) => {
        const k = reduce.matches ? 1 : 0.16;
        const dw = L.tw - L.w, dd = L.td - L.d;
        if (Math.abs(dw) > 0.3 || Math.abs(dd) > 0.1) moving = true;
        L.w += dw * k; L.d += dd * k;
        apply(L.el, "sans", { w: L.w, d: L.d, r: st.r });
        const dist = st.px === null ? Math.abs(L.tw - opts.peak.w) : Math.abs(L.cx - (st.focus >= 0 ? letters[st.focus].cx : st.px));
        if (dist < best) { best = dist; nearest = i; }
      });
      // keep the whole word inside the width: shrink at once when it grows too wide, recover slowly
      const wNow = wordEl.getBoundingClientRect().width;
      if (st.avail && wNow > st.avail) { st.size *= st.avail / wNow; moving = true; }
      else if (st.size < st.maxSize - 0.5 && wNow * 1.01 <= st.avail) { st.size = Math.min(st.maxSize, st.size * 1.01); moving = true; }
      wordEl.style.fontSize = st.size + "px";
      if (opts.onFrame) opts.onFrame(letters[nearest], st);
      st.raf = moving && onScreen(stageEl) ? requestAnimationFrame(frame) : 0;
      if (moving && !st.raf) setTimeout(kick, 400);
    }
    function kick() { if (!st.raf) st.raf = requestAnimationFrame(frame); }
    stageEl.addEventListener("pointermove", (e) => {
      const b = stageEl.getBoundingClientRect();
      st.px = (e.clientX - b.left) / b.width; st.py = clamp((e.clientY - b.top) / b.height, 0, 1); st.focus = -1; kick();
      if (opts.onMove) opts.onMove(e, b);
    });
    stageEl.addEventListener("pointerleave", () => { st.px = null; kick(); });
    addEventListener("scroll", kick, { passive: true });
    return { st, fit, kick, letters, centers, setRadius(r) { st.r = r; kick(); },
      focusStep(dir) { st.px = null; st.focus = (st.focus < 0 ? (dir > 0 ? -1 : letters.length) : st.focus) + dir; st.focus = clamp(st.focus, 0, letters.length - 1); kick(); } };
  }

  /* ---------- hero ---------- */
  const stage = $("#stage"), rdW = $("#rdW"), rdD = $("#rdD"), rdR = $("#rdR"), heroR = $("#heroRadius");
  const ring = document.createElementNS("http://www.w3.org/2000/svg", "g");
  const hero = magnetic($("#heroWord"), stage, {
    base: { w: Math.max(WG[0], 200), d: WD[0] + (WD[1] - WD[0]) * 0.18 },
    peak: { w: WG[1], d: WD[1] - (WD[1] - WD[0]) * 0.12 },
    rest: { w: 500, d: 100 }, spread: 2.4,
    maxH: () => (stage.clientHeight * 0.92) / 0.84,
    onFrame(L) { rdW.textContent = Math.round(L.w); rdD.textContent = Math.round(L.d); rdR.textContent = Math.round(hero ? hero.st.r : 0); },
    onMove(e) {
      const c = $("#chart").getBoundingClientRect();
      ring.setAttribute("transform", `translate(${(e.clientX - c.left).toFixed(0)} ${(e.clientY - c.top).toFixed(0)})`);
      ring.style.opacity = 1;
    },
  });
  stage.addEventListener("pointerleave", () => (ring.style.opacity = 0));
  stage.addEventListener("keydown", (e) => {
    if (e.key === "ArrowRight" || e.key === "ArrowLeft") { e.preventDefault(); hero.focusStep(e.key === "ArrowRight" ? 1 : -1); }
    if (e.key === "ArrowUp" || e.key === "ArrowDown") { e.preventDefault(); heroR.value = clamp(+heroR.value + (e.key === "ArrowUp" ? 10 : -10), 0, 100); hero.setRadius(+heroR.value); }
  });
  stage.addEventListener("blur", () => { hero.st.focus = -1; hero.kick(); });
  heroR.addEventListener("input", () => hero.setRadius(+heroR.value));
  if (!sax.radius) heroR.closest(".radius-ctl").hidden = true;
  if (matchMedia("(pointer: coarse)").matches) $("#hint").textContent = "Drag across the word to make each letter heavier and wider.";

  function drawChart() {
    const svg = $("#chart"), w = svg.clientWidth, h = svg.clientHeight;
    if (!w || !h) return;
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    const cx = w * 0.82, cy = h * 0.12, s = Math.max(w, h);
    const blob = (rad, wob, ph) => {
      let d = "";
      for (let i = 0; i <= 96; i++) {
        const a = (i / 96) * Math.PI * 2;
        const rr = rad * (1 + wob * (0.5 * Math.sin(3 * a + ph) + 0.3 * Math.sin(5 * a + ph * 1.7) + 0.2 * Math.sin(9 * a - ph)));
        d += (i ? "L" : "M") + (cx + Math.cos(a) * rr * 1.35).toFixed(1) + " " + (cy + Math.sin(a) * rr).toFixed(1);
      }
      return d + "Z";
    };
    svg.innerHTML = [0.12, 0.22, 0.34, 0.48, 0.64, 0.82].map((k, i) => `<path class="iso" d="${blob(s * k, 0.07 + i * 0.012, 0.6 + i)}"/>`).join("");
    ring.innerHTML = [28, 56, 92].map((r) => `<circle class="ring" r="${r}"/>`).join("");
    ring.style.opacity = 0; ring.style.transition = "opacity .3s";
    svg.appendChild(ring);
  }

  /* ---------- ticker: speed follows scrolling ---------- */
  const WORDS = ["Interfaces", "Reading", "Code", "Data", "Brands", "Signs", "Posters", "Chat", "Wayfinding", "Dashboards", "Editorial", "Packaging"];
  const tracks = [$("#tk1"), $("#tk2")];
  tracks.forEach((tr, ti) => {
    const one = WORDS.map((w, i) => {
      const k = (i * 7 + ti * 3) % 10 / 9;
      const s = typeStyle("sans", { w: lerp(WG[0] + 100, WG[1], k), d: lerp(WD[0], WD[1], 1 - k), r: i % 3 === 0 ? RD[1] : 0, ital: i % 4 === 1 ? 1 : 0 });
      const style = `font-weight:${s.fontWeight};font-stretch:${s.fontStretch};font-variation-settings:${s.fontVariationSettings.replace(/"/g, "'")}`;
      return `<span style="${style}">${w}</span><span class="dot" aria-hidden="true">${symChar("sparkle")}</span>`;
    }).join("");
    tr.innerHTML = one + one;
  });
  const tk = { x: [0, 0], v: 0, lastY: scrollY, raf: 0 };
  function tick() {
    const dy = scrollY - tk.lastY; tk.lastY = scrollY;
    tk.v = lerp(tk.v, dy, 0.1);
    const speed = 0.7 + Math.min(Math.abs(tk.v) * 0.6, 22);
    tracks.forEach((tr, i) => {
      const half = tr.scrollWidth / 2, dir = i ? 1 : -1;
      tk.x[i] = (tk.x[i] + dir * speed + half) % half - (dir > 0 ? half : 0);
      if (dir < 0 && tk.x[i] > 0) tk.x[i] -= half;
      tr.style.transform = `translate3d(${tk.x[i].toFixed(1)}px,0,0)`;
    });
    tk.raf = tickerOn ? requestAnimationFrame(tick) : 0;
  }
  let tickerOn = false;
  new IntersectionObserver((es) => {
    tickerOn = es[0].isIntersecting && !reduce.matches;
    if (tickerOn && !tk.raf) { tk.lastY = scrollY; tk.raf = requestAnimationFrame(tick); }
  }).observe($(".ticker"));

  /* ---------- same widths ---------- */
  const vText = $("#voiceText"), marks = $("#lineMarks"), vCheck = $("#voiceCheck");
  let voice = "sans", autoT = 0;
  function lineEnds() {
    const node = vText.firstChild, txt = node.textContent, ends = [], rects = [];
    const re = /\S+/g; let m, lastTop = null, lastIdx = -1, lastRect = null, idx = 0;
    const range = document.createRange();
    while ((m = re.exec(txt))) {
      range.setStart(node, m.index); range.setEnd(node, m.index + m[0].length);
      const r = range.getClientRects()[0];
      if (lastTop !== null && r.top > lastTop + 2) { ends.push(lastIdx); rects.push(lastRect); }
      lastTop = r.top; lastIdx = idx; lastRect = r; idx++;
    }
    ends.push(lastIdx); rects.push(lastRect);
    return { ends, rects };
  }
  function checkVoices() {
    vText.classList.remove("serif"); const a = lineEnds();
    vText.classList.add("serif"); const b = lineEnds();
    vText.classList.toggle("serif", voice === "serif");
    const cur = voice === "serif" ? b : a, box = vText.parentElement.getBoundingClientRect();
    marks.innerHTML = cur.rects.map((r) => `<span style="left:${(box.width - 30).toFixed(1)}px;top:${(r.top - box.top + r.height / 2 - 1.5).toFixed(1)}px"></span>`).join("");
    const same = a.ends.length === b.ends.length && a.ends.every((v, i) => v === b.ends[i]);
    vCheck.textContent = same
      ? `Measured now: all ${a.ends.length} lines end on the same word in Sans and in Serif.`
      : `Measured now: ${a.ends.filter((v, i) => v === b.ends[i]).length} of ${a.ends.length} lines end on the same word.`;
  }
  function setVoice(v) {
    voice = v;
    $$("[data-voice]").forEach((x) => x.setAttribute("aria-checked", String(x.dataset.voice === v)));
    checkVoices();
  }
  $$("[data-voice]").forEach((b) => b.addEventListener("click", () => setVoice(b.dataset.voice)));
  $("#voiceAuto").addEventListener("change", (e) => {
    clearInterval(autoT);
    if (e.target.checked) autoT = setInterval(() => setVoice(voice === "sans" ? "serif" : "sans"), 2000);
  });
  $(".trio-sans").style.fontFamily = SANS.css;

  /* ---------- tester ---------- */
  const PRESETS = [
    { name: "Interface", fam: "sans", w: 500, d: 100, r: 0, ital: 0, size: 26, lh: 1.35, text: "Notifications  Privacy  Sign out" },
    { name: "Reading", fam: "serif", w: 400, d: 100, r: 0, ital: 0, size: 24, lh: 1.6, text: "The ferry leaves Central at seven and crosses the harbour in nine minutes. On the way back the light changes over Kowloon." },
    { name: "Code", fam: "mono", w: 400, d: 100, r: 0, ital: 0, size: 20, lh: 1.5, text: "const next = await ferry.depart('Central', 'Mui Wo'); // 0O1lI" },
    { name: "Dashboard", fam: "sans", w: 650, d: 82, r: 0, ital: 0, size: 88, lh: 1.02, text: "1,284 crossings 98.6%" },
    { name: "Poster", fam: "sans", w: 900, d: 150, r: 100, ital: 0, size: 150, lh: 0.88, text: "Harbour Nights" },
    { name: "Signage", fam: "sans", w: 600, d: 88, r: 0, ital: 0, size: 96, lh: 1.02, text: "Exit C Queensway" },
  ];
  const st = { ...PRESETS[4] };
  const tW = $("#tW"), tD = $("#tD"), tR = $("#tR"), tS = $("#tS"), tL = $("#tL"), proof = $("#proof"), cssOut = $("#cssOut");
  const presetBox = $("#presets"), pad = $("#pad"), padDot = $("#padDot");
  presetBox.innerHTML = PRESETS.map((p, i) => `<button type="button" aria-pressed="${i === 4}" data-p="${i}">${p.name}</button>`).join("");
  function setRange(input, ax, val) {
    const row = input.closest(".slider");
    if (!ax) { input.disabled = true; row.classList.add("disabled"); return; }
    input.disabled = false; row.classList.remove("disabled");
    input.min = ax[0]; input.max = ax[1]; input.value = clamp(val, ax[0], ax[1]);
  }
  function syncControls() {
    const f = T.families[st.fam];
    setRange(tW, f.axes.wght, st.w); setRange(tD, f.axes.wdth, st.d); setRange(tR, f.axes.radius, st.r);
    tS.value = st.size; tL.value = st.lh;
    $$("#famSeg button").forEach((b) => b.setAttribute("aria-checked", String(b.dataset.fam === st.fam)));
    $$("#italSeg button").forEach((b) => {
      b.disabled = b.dataset.ital === "1" && !f.italic;
      b.setAttribute("aria-checked", String(+b.dataset.ital === (f.italic ? st.ital : 0)));
    });
    renderProof();
  }
  function renderProof() {
    const f = T.families[st.fam], wa = f.axes.wght, da = f.axes.wdth;
    const s = { w: +tW.value, d: da ? +tD.value : 100, r: f.axes.radius ? +tR.value : 0, ital: f.italic ? st.ital : 0 };
    Object.assign(st, s, { size: +tS.value, lh: +tL.value });
    apply(proof, st.fam, s);
    proof.style.fontSize = st.size + "px"; proof.style.lineHeight = st.lh;
    fitProof();
    $("#oW").textContent = Math.round(s.w); $("#oD").textContent = da ? s.d + "%" : "fixed";
    $("#oR").textContent = f.axes.radius ? Math.round(s.r) : "none"; $("#oS").textContent = st.size + " px"; $("#oL").textContent = st.lh.toFixed(2);
    const fx = da ? (s.d - da[0]) / (da[1] - da[0]) : 0.5, fy = 1 - (s.w - wa[0]) / (wa[1] - wa[0]);
    padDot.style.left = `calc(${fx * 100}% - ${fx * 26}px)`; padDot.style.top = `calc(${fy * 100}% - ${fy * 26}px)`;
    pad.setAttribute("aria-valuetext", `weight ${Math.round(s.w)}, width ${da ? s.d + "%" : "fixed"}`);
    const famName = { sans: "Admiralty Sans", serif: "Admiralty Serif", mono: "Admiralty Mono" }[st.fam];
    const lines = [`font-family: "${famName}";`, `font-weight: ${Math.round(s.w)};`];
    if (da) lines.push(`font-stretch: ${s.d}%;`);
    if (s.ital) lines.push("font-style: italic;");
    if (f.axes.radius && s.r) lines.push(`font-variation-settings: "${R}" ${Math.round(s.r)};`);
    lines.push(`font-size: ${st.size}px;`, `line-height: ${st.lh};`);
    cssOut.textContent = lines.join("\n");
  }
  // Big sizes shrink on screen until the longest word fits on one line; the CSS keeps the chosen size.
  const probe = document.createElement("span");
  Object.assign(probe.style, { position: "absolute", visibility: "hidden", whiteSpace: "nowrap", left: "-9999px", top: "0" });
  document.body.appendChild(probe);
  function fitProof() {
    const longest = (proof.textContent.split(/\s+/).sort((a, b) => b.length - a.length)[0] || "W");
    Object.assign(probe.style, typeStyle(st.fam, { w: st.w, d: st.d, r: st.r, ital: st.ital }), { fontSize: st.size + "px" });
    probe.textContent = longest;
    const ww = probe.getBoundingClientRect().width, avail = proof.clientWidth;
    if (ww > avail && avail > 0) proof.style.fontSize = Math.max(12, Math.floor(st.size * avail / ww * 0.98)) + "px";
  }
  proof.addEventListener("input", fitProof);
  const unpress = () => $$("button", presetBox).forEach((x) => x.setAttribute("aria-pressed", "false"));
  presetBox.addEventListener("click", (e) => {
    const b = e.target.closest("button"); if (!b) return;
    const p = PRESETS[+b.dataset.p]; Object.assign(st, p); proof.textContent = p.text;
    $$("button", presetBox).forEach((x) => x.setAttribute("aria-pressed", String(x === b)));
    syncControls();
  });
  $$("#famSeg button").forEach((b) => b.addEventListener("click", () => { st.fam = b.dataset.fam; syncControls(); }));
  $$("#italSeg button").forEach((b) => b.addEventListener("click", () => { if (!b.disabled) { st.ital = +b.dataset.ital; syncControls(); } }));
  [tW, tD, tR, tS, tL].forEach((i) => i.addEventListener("input", () => { unpress(); renderProof(); }));
  function padSet(fx, fy) {
    const f = T.families[st.fam], wa = f.axes.wght, da = f.axes.wdth;
    tW.value = Math.round(lerp(wa[1], wa[0], clamp(fy, 0, 1)));
    if (da) tD.value = (Math.round(lerp(da[0], da[1], clamp(fx, 0, 1)) * 2) / 2).toFixed(1);
    unpress(); renderProof();
  }
  let padDrag = false;
  pad.addEventListener("pointerdown", (e) => { padDrag = true; pad.setPointerCapture(e.pointerId); const b = pad.getBoundingClientRect(); padSet((e.clientX - b.left) / b.width, (e.clientY - b.top) / b.height); });
  pad.addEventListener("pointermove", (e) => { if (!padDrag) return; const b = pad.getBoundingClientRect(); padSet((e.clientX - b.left) / b.width, (e.clientY - b.top) / b.height); });
  pad.addEventListener("pointerup", () => (padDrag = false));
  pad.addEventListener("keydown", (e) => {
    const m = { ArrowUp: [0, 20, 0], ArrowDown: [0, -20, 0], ArrowRight: [0, 0, 2.5], ArrowLeft: [0, 0, -2.5] }[e.key];
    if (!m) return; e.preventDefault();
    tW.value = +tW.value + m[1]; if (!tD.disabled) tD.value = +tD.value + m[2]; unpress(); renderProof();
  });
  $("#copyCss").addEventListener("click", () => copy(cssOut.textContent, "Copied the CSS"));
  proof.textContent = st.text;
  syncControls();
  addEventListener("resize", () => renderProof());

  /* ---------- range rows: scroll position or pointer sets each axis ---------- */
  const rows = $$(".rrow");
  const fmt = { wght: (v) => Math.round(v), wdth: (v) => Math.round(v) + "%", radius: (v) => Math.round(v), ital: (v) => (Math.abs(SANS.slnt || 10) * v).toFixed(1) + "°" };
  function paintRow(row, k) {
    const ax = row.dataset.axis, s = { w: 500, d: 100, r: 0, ital: 0 };
    let v = 0;
    if (ax === "wght") v = s.w = lerp(WG[0], WG[1], k);
    if (ax === "wdth") v = s.d = lerp(WD[0], WD[1], k);
    if (ax === "radius") { s.w = 800; v = s.r = lerp(RD[0], RD[1], k); }
    if (ax === "ital") { s.ital = SANS.italic === "slnt" ? k : k > 0.5 ? 1 : 0; v = s.ital; }
    apply($(".rword", row), "sans", s);
    $("[data-out]", row).textContent = fmt[ax](v);
  }
  const hover = new Map();
  function paintRows() {
    rows.forEach((row) => {
      if (hover.has(row)) return paintRow(row, hover.get(row));
      const b = row.getBoundingClientRect();
      const k = clamp((innerHeight - b.top) / (innerHeight + b.height), 0, 1);
      paintRow(row, k * k * (3 - 2 * k));
    });
  }
  rows.forEach((row) => {
    row.addEventListener("pointermove", (e) => { const b = row.getBoundingClientRect(); hover.set(row, clamp((e.clientX - b.left) / b.width, 0, 1)); paintRow(row, hover.get(row)); });
    row.addEventListener("pointerleave", () => { hover.delete(row); paintRows(); });
  });
  let rowRAF = 0;
  addEventListener("scroll", () => { if (!rowRAF) rowRAF = requestAnimationFrame(() => { rowRAF = 0; paintRows(); }); }, { passive: true });
  if (!sax.radius) rows.find((r) => r.dataset.axis === "radius").hidden = true;
  if (!SANS.italic) rows.find((r) => r.dataset.axis === "ital").hidden = true;
  paintRows();

  /* ---------- uses ---------- */
  const hours = [12, 30, 62, 88, 70, 48, 40, 44, 46, 50, 58, 84, 92, 66, 42, 28];
  $("#barsG").innerHTML = hours.map((v, i) => `<rect x="${i * 15}" y="${90 - v}" width="11" height="${v}" ${v > 80 ? 'class="hi"' : ""}/>`).join("");
  $$(".tgl").forEach((t) => t.addEventListener("click", () => {
    const on = t.getAttribute("aria-checked") !== "true";
    t.setAttribute("aria-checked", String(on)); $(".sym", t).dataset.sym = on ? "toggle-on" : "toggle-off"; paintSyms(t);
  }));
  // poster: pointer sets width (x) and weight (y)
  const poster = $("#poster"), poHead = $("#poHead");
  const poRest = { w: WG[1], d: WD[1], r: RD[1] };
  apply(poHead, "sans", poRest);
  poster.addEventListener("pointermove", (e) => {
    const b = poster.getBoundingClientRect();
    apply(poHead, "sans", { w: lerp(WG[1], 300, clamp((e.clientY - b.top) / b.height, 0, 1)), d: lerp(WD[0], WD[1], clamp((e.clientX - b.left) / b.width, 0, 1)), r: RD[1] });
  });
  poster.addEventListener("pointerleave", () => apply(poHead, "sans", poRest));
  // sign: pointer sets the width of the names
  const sign = $("#sign"), names = $$(".sign-name", sign);
  const signRest = () => names.forEach((n) => apply(n, "sans", { w: 600, d: 88 }));
  signRest();
  sign.addEventListener("pointermove", (e) => {
    const b = sign.getBoundingClientRect(), d = lerp(WD[0], 115, clamp((e.clientX - b.left) / b.width, 0, 1));
    names.forEach((n) => apply(n, "sans", { w: 600, d }));
  });
  sign.addEventListener("pointerleave", signRest);

  /* ---------- symbols ---------- */
  const grid = $("#symGrid"), search = $("#symSearch"), count = $("#symCount"), symW = $("#symW"), more = $("#symMore");
  const symBig = $("#symBig"), symName = $("#symName"), symLabel = $("#symLabel"), symWeights = $("#symWeights");
  grid.innerHTML = window.SYMBOLS.map(([n, l]) => `<button type="button" data-n="${n}" aria-pressed="false" aria-label="${l}"><i class="sym" aria-hidden="true" data-char="${symChar(n)}"></i><small>${n}</small></button>`).join("");
  const btns = $$("button", grid);
  let showAll = false, chosen = "heart-filled";
  // show five full rows at first, however many columns fit
  const firstCount = () => Math.max(1, getComputedStyle(grid).gridTemplateColumns.split(" ").length) * 5;
  function choose(n) {
    chosen = n; const s = SYM.get(n);
    symBig.setAttribute("data-char", symChar(n)); symName.textContent = n; symLabel.textContent = `${s.label}, in ${s.cat}`;
    symWeights.innerHTML = [400, 500, 700].map((w) => `<span><i class="sym" style="font-weight:${w}" data-char="${symChar(n)}"></i><small>${w}</small></span>`).join("");
    btns.forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.n === n)));
  }
  function filterSyms() {
    const q = search.value.trim().toLowerCase();
    let shown = 0;
    btns.forEach((b, i) => {
      const s = SYM.get(b.dataset.n), hay = `${s.name} ${s.label} ${s.cat} ${s.tags}`.toLowerCase();
      const ok = q ? q.split(/\s+/).every((w) => hay.includes(w)) : showAll || i < firstCount();
      b.hidden = !ok; if (ok) shown++;
    });
    more.hidden = !!q || showAll;
    count.textContent = q
      ? shown ? `${shown} of ${btns.length} symbols match “${search.value.trim()}”` : `No symbol matches “${search.value.trim()}”. Try a shorter word, such as file or user.`
      : showAll ? `All ${btns.length} symbols` : `${shown} of ${btns.length} symbols`;
  }
  search.addEventListener("input", filterSyms);
  more.addEventListener("click", () => { const n = firstCount(); showAll = true; filterSyms(); btns[n] && btns[n].focus(); });
  addEventListener("resize", () => { if (!showAll && !search.value) filterSyms(); });
  grid.addEventListener("click", (e) => { const b = e.target.closest("button"); if (b) choose(b.dataset.n); });
  grid.addEventListener("pointerover", (e) => { const b = e.target.closest("button"); if (b && matchMedia("(hover: hover)").matches) choose(b.dataset.n); });
  $("#symCopy").addEventListener("click", () => copy(chosen, `Copied ${chosen}`));
  symW.addEventListener("input", () => { $("#symbols").style.setProperty("--symW", symW.value); $("#oSW").textContent = symW.value; });
  choose(chosen); filterSyms();

  /* ---------- characters ---------- */
  const CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789&@#%?!*()[]{}$€£¥₫" +
    "ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÑÒÓÔÕÖØÙÚÛÜÝßàáâãäåæçèéêëìíîïñòóôõöøùúûüýÿ" +
    "ĀāĂăĄąĆćČčĎďĐđĒēĘęĚěĞğĪīİıŁłŃńŇňŌōŐőŒœŘřŚśŠšŤťŪūŮůŰűŸŹźŻżŽž" +
    "ẠạẢảẤấẦầẨẩẪẫẬậẮắẰằẲẳẴẵẶặẸẹẺẻẼẽẾếỀềỂểỄễỆệỈỉỊịỌọỎỏỐốỒồỔổỖỗỘộỚớỜờỞởỠỡỢợỤụỦủỨứỪừỬửỮữỰựỲỳỴỵỶỷỸỹƠơƯư" +
    "ǍǎǏǐǑǒǓǔǕǖǗǘǙǚǛǜ";
  const cGrid = $("#charGrid"), big = $("#charBig"), info = $("#charInfo"), charStage = $("#charStage");
  const hex = (c) => "U+" + c.codePointAt(0).toString(16).toUpperCase().padStart(4, "0");
  cGrid.innerHTML = [...CHARS].map((c) => `<button type="button" aria-label="${c}, ${hex(c)}">${c}</button>`).join("");
  let charSet = { w: 400, d: 100 };
  function show(b) {
    const c = b.textContent; big.textContent = c; paintInfo();
    $$("button[aria-pressed]", cGrid).forEach((x) => x.removeAttribute("aria-pressed")); b.setAttribute("aria-pressed", "true");
  }
  function paintInfo() { apply(big, "sans", charSet); info.textContent = `${hex(big.textContent)}   weight ${Math.round(charSet.w)}   width ${Math.round(charSet.d)}%`; }
  cGrid.addEventListener("pointerover", (e) => { const b = e.target.closest("button"); if (b) show(b); });
  cGrid.addEventListener("focusin", (e) => { const b = e.target.closest("button"); if (b) show(b); });
  charStage.addEventListener("pointermove", (e) => {
    const b = charStage.getBoundingClientRect();
    charSet = { w: lerp(WG[1], WG[0], clamp((e.clientY - b.top) / b.height, 0, 1)), d: lerp(WD[0], WD[1], clamp((e.clientX - b.left) / b.width, 0, 1)) };
    paintInfo();
  });
  paintInfo();

  /* ---------- install tabs ---------- */
  const tabs = $$('[role="tab"]');
  tabs.forEach((t) => t.addEventListener("click", () => {
    tabs.forEach((x) => { const on = x === t; x.setAttribute("aria-selected", String(on)); $("#" + x.getAttribute("aria-controls")).hidden = !on; });
  }));

  /* ---------- footer ---------- */
  $("#standin").textContent = T.standinNote || "";
  const foot = magnetic($("#footWord"), $("#foot"), {
    base: { w: WG[0], d: WD[0] + (WD[1] - WD[0]) * 0.1 }, peak: { w: WG[1], d: WD[1] }, rest: { w: 700, d: 120 }, spread: 2.2,
  });
  if (sax.radius) foot.setRadius(RD[1]);

  /* ---------- start ---------- */
  function layout() { hero.fit(); foot.fit(); drawChart(); checkVoices(); paintRows(); hero.kick(); foot.kick(); }
  const released = Promise.all(['400 20px "Admiralty Sans Released"', '400 20px "Admiralty Serif Released"'].map((f) => document.fonts.load(f)));
  Promise.all([document.fonts.ready, released]).then(layout);
  let rz; addEventListener("resize", () => { clearTimeout(rz); rz = setTimeout(layout, 120); });
})();
