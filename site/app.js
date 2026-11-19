(() => {
  "use strict";
  const T = window.TYPE;
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const reduce = matchMedia("(prefers-reduced-motion: reduce)");
  const clamp = (v, a, b) => Math.min(b, Math.max(a, v));
  const R = T.radiusTag;

  /* ---------- type helpers ---------- */
  // Style for one family at given settings. Weight and width use the standard CSS
  // properties; radius and slant (custom or extra axes) use font-variation-settings.
  function typeStyle(famKey, s) {
    const f = T.families[famKey], ax = f.axes, out = { fontFamily: f.css };
    out.fontWeight = String(Math.round(clamp(s.w ?? 400, ...(ax.wght || [400, 400]))));
    out.fontStretch = (ax.wdth ? clamp(s.d ?? 100, ...ax.wdth) : 100).toFixed(1) + "%";
    const fvs = [];
    if (ax.radius) fvs.push(`"${R}" ${Math.round(clamp(s.r ?? 0, ...ax.radius))}`);
    const ital = s.ital || 0;
    if (f.italic === "face") out.fontStyle = ital > 0.5 ? "italic" : "normal";
    else out.fontStyle = "normal";
    if (f.italic === "slnt") fvs.push(`"slnt" ${(f.slnt * ital).toFixed(2)}`);
    out.fontVariationSettings = fvs.length ? fvs.join(", ") : "normal";
    return out;
  }
  const apply = (el, famKey, s) => Object.assign(el.style, typeStyle(famKey, s));

  // Elements that ask for a radius in the markup (poster, footer)
  $$("[data-radius]").forEach((el) => {
    if (T.families.sans.axes.radius) el.style.fontVariationSettings = `"${R}" ${el.dataset.radius}`;
  });

  /* ---------- symbols as glyphs ---------- */
  const SYM = new Map(window.SYMBOLS.map(([name, label, cp, cat, tags]) => [name, { name, label, cp, cat, tags }]));
  const symChar = (n) => (SYM.has(n) ? String.fromCodePoint(SYM.get(n).cp) : "");
  const paintSyms = (root = document) => $$("[data-sym]", root).forEach((el) => el.setAttribute("data-char", symChar(el.dataset.sym)));
  paintSyms();

  /* ---------- toast ---------- */
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
  const isDark = () => root.dataset.theme ? root.dataset.theme === "dark" : matchMedia("(prefers-color-scheme: dark)").matches;
  function paintTheme() {
    const icon = $(".sym", themeBtn);
    icon.dataset.sym = isDark() ? "light-mode" : "dark-mode";
    paintSyms(themeBtn);
    themeBtn.setAttribute("aria-label", isDark() ? "Switch to day colours" : "Switch to night colours");
  }
  try { const t = localStorage.getItem("adm-theme"); if (t) root.dataset.theme = t; } catch {}
  themeBtn.addEventListener("click", () => {
    root.dataset.theme = isDark() ? "light" : "dark";
    try { localStorage.setItem("adm-theme", root.dataset.theme); } catch {}
    paintTheme(); drawChart();
  });
  paintTheme();

  /* ---------- hero ---------- */
  const stage = $("#stage"), word = $("#heroWord"), rdW = $("#rdW"), rdD = $("#rdD"), rdR = $("#rdR"), heroR = $("#heroRadius");
  const sax = T.families.sans.axes;
  const cur = { w: 400, d: 100, r: 0 }, tgt = { w: 400, d: 100, r: 0 };
  let heroRAF = 0;
  if (!sax.radius) heroR.closest(".radius-ctl").hidden = true;

  // The word always fills the width: narrow settings make it taller, wide ones shorter.
  let heroSize = 160;
  function availWidth() {
    const cs = getComputedStyle(stage);
    return stage.clientWidth - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight);
  }
  function paintHero() {
    apply(word, "sans", cur);
    word.style.fontSize = heroSize + "px";
    const wNow = word.getBoundingClientRect().width;
    if (wNow > 0) {
      const maxByHeight = (window.innerHeight * 0.58) / 0.86;
      heroSize = Math.min((heroSize * availWidth()) / wNow, maxByHeight);
      word.style.fontSize = heroSize + "px";
    }
    rdW.textContent = Math.round(cur.w);
    rdD.textContent = Math.round(cur.d);
    rdR.textContent = Math.round(cur.r);
  }
  const fitHero = paintHero;
  function stepHero() {
    let moving = false;
    for (const k of ["w", "d", "r"]) {
      const dv = tgt[k] - cur[k];
      if (Math.abs(dv) > 0.2) { cur[k] += dv * 0.14; moving = true; } else cur[k] = tgt[k];
    }
    paintHero();
    heroRAF = moving ? requestAnimationFrame(stepHero) : 0;
  }
  function setTarget(v, instant) {
    Object.assign(tgt, v);
    tgt.w = clamp(tgt.w, ...sax.wght); if (sax.wdth) tgt.d = clamp(tgt.d, ...sax.wdth);
    if (instant || reduce.matches) { Object.assign(cur, tgt); paintHero(); return; }
    if (!heroRAF) heroRAF = requestAnimationFrame(stepHero);
  }
  stage.addEventListener("pointermove", (e) => {
    if (e.pointerType === "touch" && !e.isPrimary) return;
    const b = stage.getBoundingClientRect();
    const fx = clamp((e.clientX - b.left) / b.width, 0, 1), fy = clamp((e.clientY - b.top) / b.height, 0, 1);
    const v = { w: sax.wght[1] - fy * (sax.wght[1] - sax.wght[0]) };
    if (sax.wdth) v.d = sax.wdth[0] + fx * (sax.wdth[1] - sax.wdth[0]);
    setTarget(v);
  });
  stage.addEventListener("keydown", (e) => {
    const step = e.shiftKey ? 50 : 10, m = { ArrowUp: [0, step], ArrowDown: [0, -step], ArrowRight: [step / 5, 0], ArrowLeft: [-step / 5, 0] }[e.key];
    if (!m) return;
    e.preventDefault();
    setTarget({ d: tgt.d + m[0] * 2, w: tgt.w + m[1] });
  });
  heroR.addEventListener("input", () => setTarget({ r: +heroR.value }));
  if (matchMedia("(pointer: coarse)").matches) $("#hint").textContent = "Drag across the word to change its width. Use the radius slider to round its corners.";

  /* chart: soundings, depth contours and a strip of land, drawn once per size */
  function rng(seed) { return () => ((seed = (seed * 16807) % 2147483647) / 2147483647); }
  function drawChart() {
    const svg = $("#chart"), w = svg.clientWidth, h = svg.clientHeight;
    if (!w || !h) return;
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    const rand = rng(7), cx = w * 0.86, cy = h * 0.08;
    const blob = (rad, wob, ph) => {
      let d = "";
      for (let i = 0; i <= 96; i++) {
        const a = (i / 96) * Math.PI * 2;
        const rr = rad * (1 + wob * (0.5 * Math.sin(3 * a + ph) + 0.3 * Math.sin(5 * a + ph * 1.7) + 0.2 * Math.sin(9 * a - ph)));
        d += (i ? "L" : "M") + (cx + Math.cos(a) * rr * 1.35).toFixed(1) + " " + (cy + Math.sin(a) * rr).toFixed(1);
      }
      return d + "Z";
    };
    const s = Math.max(w, h);
    let out = `<path class="shoal" d="${blob(s * 0.34, 0.12, 1.1)}"/>`;
    out += `<path class="land" d="${blob(s * 0.17, 0.16, 2.3)}"/>`;
    [0.26, 0.42, 0.58, 0.76].forEach((k, i) => (out += `<path class="iso" d="${blob(s * k, 0.08 + i * 0.015, 0.6 + i)}"/>`));
    const placed = [], stageBottom = stage.offsetTop + stage.offsetHeight;
    for (let i = 0; i < 60; i++) {
      const x = rand() * w, y = rand() * h;
      if (y > stageBottom - 10 || y < 18) continue;      // keep the soundings clear of the text below
      if (placed.some(([px, py]) => Math.hypot(px - x, py - y) < 70)) continue;
      placed.push([x, y]);
      if (Math.hypot((x - cx) / 1.35, y - cy) < s * 0.2) continue;
      const depth = Math.round(4 + Math.hypot((x - cx) / 1.35, y - cy) / s * 40);
      out += `<text class="snd" x="${x.toFixed(0)}" y="${y.toFixed(0)}">${depth}<tspan dy="3" font-size="8">${Math.round(rand() * 9)}</tspan></text>`;
    }
    svg.innerHTML = out;
  }

  /* ---------- same widths ---------- */
  const vText = $("#voiceText"), marks = $("#lineMarks"), vCheck = $("#voiceCheck");
  let voice = "sans";
  function lineEnds() {
    // index of the last word on each line, measured from the rendered text
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
    const cur = voice === "serif" ? b : a;
    const box = vText.parentElement.getBoundingClientRect();
    marks.innerHTML = cur.rects.map((r) => `<span style="left:${(box.width - 26).toFixed(1)}px;top:${(r.top - box.top + r.height / 2 - 1).toFixed(1)}px"></span>`).join("");
    const same = a.ends.length === b.ends.length && a.ends.every((v, i) => v === b.ends[i]);
    vCheck.textContent = same
      ? `Measured now: all ${a.ends.length} lines end on the same word in Sans and in Serif.`
      : `Measured now: ${a.ends.filter((v, i) => v === b.ends[i]).length} of ${a.ends.length} lines end on the same word.`;
  }
  $$("[data-voice]").forEach((b) => b.addEventListener("click", () => {
    voice = b.dataset.voice;
    $$("[data-voice]").forEach((x) => x.setAttribute("aria-checked", String(x === b)));
    checkVoices();
  }));
  $(".trio-sans").style.fontFamily = T.families.sans.css;

  /* ---------- tester ---------- */
  const PRESETS = [
    { name: "Interface", fam: "sans", w: 500, d: 100, r: 0, ital: 0, size: 22, lh: 1.35, text: "Notifications  Privacy  Sign out" },
    { name: "Reading", fam: "serif", w: 400, d: 100, r: 0, ital: 0, size: 22, lh: 1.6, text: "The ferry leaves Central at seven and crosses the harbour in nine minutes. On the way back the light changes over Kowloon." },
    { name: "Code", fam: "mono", w: 400, d: 100, r: 0, ital: 0, size: 18, lh: 1.5, text: "const next = await ferry.depart('Central', 'Mui Wo'); // 0O1lI" },
    { name: "Dashboard", fam: "sans", w: 650, d: 82, r: 0, ital: 0, size: 72, lh: 1.05, text: "1,284 crossings  98.6%" },
    { name: "Poster", fam: "sans", w: 900, d: 150, r: 100, ital: 0, size: 120, lh: 0.9, text: "Harbour Nights" },
    { name: "Signage", fam: "sans", w: 600, d: 88, r: 0, ital: 0, size: 76, lh: 1.05, text: "Exit C Queensway" },
  ];
  const st = { ...PRESETS[4] };
  const tW = $("#tW"), tD = $("#tD"), tR = $("#tR"), tS = $("#tS"), tL = $("#tL"), proof = $("#proof"), cssOut = $("#cssOut");
  const presetBox = $("#presets");
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
    const f = T.families[st.fam];
    const s = { w: +tW.value, d: f.axes.wdth ? +tD.value : 100, r: f.axes.radius ? +tR.value : 0, ital: f.italic ? st.ital : 0 };
    Object.assign(st, s, { size: +tS.value, lh: +tL.value });
    apply(proof, st.fam, s);
    // on narrow screens big sizes are scaled down so whole words still fit; the CSS keeps the chosen size
    const fit = Math.min(1, (proof.clientWidth || 800) / 820);
    proof.style.fontSize = Math.max(12, st.size * (st.size > 40 ? fit : 1)) + "px"; proof.style.lineHeight = st.lh;
    $("#oW").textContent = Math.round(s.w); $("#oD").textContent = f.axes.wdth ? s.d + "%" : "fixed";
    $("#oR").textContent = f.axes.radius ? Math.round(s.r) : "none"; $("#oS").textContent = st.size + " px"; $("#oL").textContent = st.lh.toFixed(2);
    const famName = { sans: "Admiralty Sans", serif: "Admiralty Serif", mono: "Admiralty Mono" }[st.fam];
    const lines = [`font-family: "${famName}";`, `font-weight: ${Math.round(s.w)};`];
    if (f.axes.wdth) lines.push(`font-stretch: ${s.d}%;`);
    if (s.ital) lines.push("font-style: italic;");
    if (f.axes.radius && s.r) lines.push(`font-variation-settings: "${R}" ${Math.round(s.r)};`);
    lines.push(`font-size: ${st.size}px;`, `line-height: ${st.lh};`);
    cssOut.textContent = lines.join("\n");
  }
  presetBox.addEventListener("click", (e) => {
    const b = e.target.closest("button"); if (!b) return;
    const p = PRESETS[+b.dataset.p]; Object.assign(st, p); proof.textContent = p.text;
    $$("button", presetBox).forEach((x) => x.setAttribute("aria-pressed", String(x === b)));
    syncControls();
  });
  $$("#famSeg button").forEach((b) => b.addEventListener("click", () => { st.fam = b.dataset.fam; syncControls(); }));
  $$("#italSeg button").forEach((b) => b.addEventListener("click", () => { if (!b.disabled) { st.ital = +b.dataset.ital; syncControls(); } }));
  [tW, tD, tR, tS, tL].forEach((i) => i.addEventListener("input", () => {
    $$("button", presetBox).forEach((x) => x.setAttribute("aria-pressed", "false"));
    renderProof();
  }));
  $("#copyCss").addEventListener("click", () => copy(cssOut.textContent, "Copied the CSS"));
  proof.textContent = st.text;
  syncControls();
  addEventListener("resize", () => renderProof());

  /* ---------- range rows ---------- */
  const rows = $$(".rrow");
  let rangeOn = !reduce.matches, rangeVisible = false, rangeRAF = 0;
  const toggle = $("#rangeToggle");
  function paintRows(t) {
    rows.forEach((row, i) => {
      const k = (1 - Math.cos((t / 4200 + i * 0.18) * Math.PI * 2)) / 2, el = $(".rword", row), ax = row.dataset.axis;
      const s = { w: 400, d: 100, r: 0, ital: 0 };
      if (ax === "wght") s.w = sax.wght[0] + k * (sax.wght[1] - sax.wght[0]);
      if (ax === "wdth" && sax.wdth) s.d = sax.wdth[0] + k * (sax.wdth[1] - sax.wdth[0]);
      if (ax === "radius") { s.w = 800; if (sax.radius) s.r = sax.radius[0] + k * (sax.radius[1] - sax.radius[0]); }
      if (ax === "ital") s.ital = T.families.sans.italic === "slnt" ? k : (k > 0.5 ? 1 : 0);
      apply(el, "sans", s);
    });
  }
  function loop(t) { paintRows(t); rangeRAF = rangeOn && rangeVisible ? requestAnimationFrame(loop) : 0; }
  function kick() { if (rangeOn && rangeVisible && !rangeRAF) rangeRAF = requestAnimationFrame(loop); }
  new IntersectionObserver((es) => { rangeVisible = es[0].isIntersecting; kick(); }).observe($("#ranges"));
  toggle.addEventListener("click", () => {
    rangeOn = !rangeOn; toggle.textContent = rangeOn ? "Pause" : "Play"; kick();
  });
  if (!rangeOn) { toggle.textContent = "Play"; paintRows(0.5 * 4200 / 1); }
  if (!T.families.sans.axes.radius) rows.find((r) => r.dataset.axis === "radius").hidden = true;
  if (!T.families.sans.italic) rows.find((r) => r.dataset.axis === "ital").hidden = true;

  /* ---------- uses: small bar chart ---------- */
  const hours = [12, 30, 62, 88, 70, 48, 40, 44, 46, 50, 58, 84, 92, 66, 42, 28];
  $("#barsG").innerHTML = hours.map((v, i) => `<rect x="${i * 15}" y="${90 - v}" width="11" height="${v}" ${v > 80 ? 'class="hi"' : ""}/>`).join("");

  /* ---------- symbols ---------- */
  const grid = $("#symGrid"), search = $("#symSearch"), count = $("#symCount"), symW = $("#symW");
  grid.innerHTML = window.SYMBOLS.map(([n, l]) => `<button type="button" data-n="${n}" title="${l}"><i class="sym" aria-hidden="true" data-char="${symChar(n)}"></i><small>${n}</small></button>`).join("");
  const btns = $$("button", grid), more = $("#symMore");
  let showAll = false;
  function filterSyms() {
    const q = search.value.trim().toLowerCase();
    let shown = 0;
    btns.forEach((b, i) => {
      const s = SYM.get(b.dataset.n), hay = `${s.name} ${s.label} ${s.cat} ${s.tags}`.toLowerCase();
      const ok = q ? q.split(/\s+/).every((w) => hay.includes(w)) : (showAll || i < 48);
      b.hidden = !ok; if (ok) shown++;
    });
    more.hidden = !!q || showAll;
    count.textContent = q ? (shown ? `${shown} of ${btns.length} symbols match “${search.value.trim()}”` : `No symbol matches “${search.value.trim()}”. Try a shorter word, such as file or user.`)
      : showAll ? `All ${btns.length} symbols` : `48 of ${btns.length} symbols`;
  }
  search.addEventListener("input", filterSyms);
  more.addEventListener("click", () => { showAll = true; filterSyms(); btns[48].focus(); });
  grid.addEventListener("click", (e) => { const b = e.target.closest("button"); if (b) copy(b.dataset.n, `Copied ${b.dataset.n}`); });
  symW.addEventListener("input", () => { grid.style.setProperty("--symW", symW.value); $("#oSW").textContent = symW.value; });
  filterSyms();

  /* ---------- characters ---------- */
  const CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789&@#%?!*()[]{}$€£¥₫" +
    "ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÑÒÓÔÕÖØÙÚÛÜÝßàáâãäåæçèéêëìíîïñòóôõöøùúûüýÿ" +
    "ĀāĂăĄąĆćČčĎďĐđĒēĘęĚěĞğĪīİıŁłŃńŇňŌōŐőŒœŘřŚśŠšŤťŪūŮůŰűŸŹźŻżŽž" +
    "ẠạẢảẤấẦầẨẩẪẫẬậẮắẰằẲẳẴẵẶặẸẹẺẻẼẽẾếỀềỂểỄễỆệỈỉỊịỌọỎỏỐốỒồỔổỖỗỘộỚớỜờỞởỠỡỢợỤụỦủỨứỪừỬửỮữỰựỲỳỴỵỶỷỸỹƠơƯư" +
    "ǍǎǏǐǑǒǓǔǕǖǗǘǙǚǛǜ";
  const cGrid = $("#charGrid"), big = $("#charBig"), info = $("#charInfo");
  cGrid.innerHTML = [...CHARS].map((c) => `<button type="button" aria-label="${c}, U+${c.codePointAt(0).toString(16).toUpperCase().padStart(4, "0")}">${c}</button>`).join("");
  function show(b) {
    const c = b.textContent; big.textContent = c;
    info.textContent = "U+" + c.codePointAt(0).toString(16).toUpperCase().padStart(4, "0");
    $$("button[aria-pressed]", cGrid).forEach((x) => x.removeAttribute("aria-pressed")); b.setAttribute("aria-pressed", "true");
  }
  cGrid.addEventListener("pointerover", (e) => { const b = e.target.closest("button"); if (b) show(b); });
  cGrid.addEventListener("focusin", (e) => { const b = e.target.closest("button"); if (b) show(b); });

  /* ---------- install tabs ---------- */
  const tabs = $$('[role="tab"]');
  tabs.forEach((t) => t.addEventListener("click", () => {
    tabs.forEach((x) => { const on = x === t; x.setAttribute("aria-selected", String(on)); $("#" + x.getAttribute("aria-controls")).hidden = !on; });
  }));

  /* ---------- footer ---------- */
  $("#standin").textContent = T.standinNote || "";

  /* ---------- start ---------- */
  function layout() { fitHero(); drawChart(); checkVoices(); }
  const released = Promise.all(['400 20px "Admiralty Sans Released"', '400 20px "Admiralty Serif Released"'].map((f) => document.fonts.load(f)));
  Promise.all([document.fonts.ready, released]).then(() => {
    layout();
    if (reduce.matches) { setTarget({ w: 400, d: 100, r: 0 }, true); return; }
    // one opening move: from Thin Compressed to Regular
    setTarget({ w: sax.wght[0], d: sax.wdth ? sax.wdth[0] : 100, r: 0 }, true);
    setTimeout(() => setTarget({ w: 400, d: 100 }), 250);
  });
  let rz; addEventListener("resize", () => { clearTimeout(rz); rz = setTimeout(layout, 120); });
  paintHero();
})();
