const $ = (id) => document.getElementById(id);
const svgNS = 'http://www.w3.org/2000/svg';
const families = Object.keys(fonts);
const weights = [100, 200, 300, 400, 500, 600, 700, 800, 900];
function matrixAxes() {
  const intermediate = $('sampling').value === 'intermediate';
  const radii = intermediate ? [0, 50, 100] : [0, 100];
  return {
    widths: intermediate ? [65, 82.5, 100, 125, 150] : [65, 100, 150],
    radii: radii.filter((r) => !$('radius').value || +$('radius').value === r),
  };
}
const issuePrefix = 'admiralty.glyph-review.v1.issue/';
const positionKey = 'admiralty.glyph-review.v1.position';
const annotationFrame = {
  units: 'normalized',
  origin: 'top left',
  viewBox: [0, 0, 1440, 1440],
  fontSize: 1000,
  baseline: 1030,
  textAnchor: 'middle',
  textX: 720,
};
const catalogue = new Map(),
  marks = new Map();
const label = (f) => f.replace('Admiralty', '').replace('-Italic', ' Italic');
const ucode = (cp) => 'U+' + cp.toString(16).toUpperCase().padStart(4, '0');
const tag = (name, text) => Object.assign(document.createElement(name), { textContent: text ?? '' });

for (const [index, family] of families.entries()) {
  const font = fonts[family];
  font.face = 'Family' + index;
  font.ids = new Map(font.order.map((n, i) => [n, i]));
  for (const name of font.order) {
    if (!catalogue.has(name)) catalogue.set(name, { name, families: [], codes: new Set() });
    catalogue.get(name).families.push(family);
  }
  for (const [cp, name] of Object.entries(font.cmap)) catalogue.get(name).codes.add(Number(cp));
}
const pages = [...catalogue.values()];
function warn(message) {
  $('notice').textContent = message;
  $('notice').hidden = false;
}
let restored;
try {
  restored = localStorage.getItem(positionKey);
  for (let i = 0; i < localStorage.length; i++) {
    const key = localStorage.key(i);
    if (key?.startsWith(issuePrefix)) {
      try {
        const item = JSON.parse(localStorage.getItem(key));
        if (item?.schema === 1) marks.set(key, item);
      } catch {
        warn('有一条本地记录无法读取。其他标记仍可导出。');
      }
    }
  }
} catch {
  warn('浏览器限制了本地存储。本次标记可以导出，请在关闭页面前保存文件。');
}
const requested = new URLSearchParams(location.search).get('glyph');
let page = catalogue.get(requested) || catalogue.get(restored) || catalogue.get('A') || pages[0];
let mode = 'flag',
  selected = null,
  drag = null,
  generation = 0;
const ready = new Map();
function faceReady(family) {
  if (!ready.has(family)) {
    const f = fonts[family];
    ready.set(
      family,
      document.fonts
        .load('32px ' + f.face, String.fromCodePoint(0xf0000 + 1))
        .then((loaded) => {
          if (!loaded.length) throw Error(label(family));
        })
        .catch((err) => {
          ready.delete(family);
          throw err;
        }),
    );
  }
  return ready.get(family);
}
function spec(name, family, wght, wdth, RADI) {
  return { name, family, wght, wdth, RADI };
}
function keyFor(v) {
  return (
    issuePrefix +
    [fonts[v.family].sha256, v.family, v.name, v.wght, v.wdth, v.RADI].map(encodeURIComponent).join('/')
  );
}
function infoFor(v) {
  return label(v.family) + ' · ' + v.wght + ' / ' + v.wdth + '% / R' + v.RADI;
}
// A shared ink frame preserves width and baseline differences between all visible cases.
function specimenFrame(shown) {
  if (shown.some((family) => fonts[family].operators[page.name])) return [-656, -630, 1312, 660];
  const boxes = shown.map((f) => fonts[f].inkBounds[fonts[f].ids.get(page.name)]).filter(Boolean);
  if (!boxes.length) return [-500, -800, 1000, 1000];
  const left = Math.min(...boxes.map((b) => b[0])),
    top = Math.min(...boxes.map((b) => b[1]));
  const width = Math.max(...boxes.map((b) => b[2])) - left;
  const height = Math.max(...boxes.map((b) => b[3])) - top;
  const pad = Math.max(width, height) * 0.045 + 2;
  return [left - pad, top - pad, width + 2 * pad, height + 2 * pad];
}

function sample(v, frame) {
  const f = fonts[v.family],
    gid = f.ids.get(v.name);
  const svg = document.createElementNS(svgNS, 'svg');
  svg.setAttribute('viewBox', (frame || annotationFrame.viewBox).join(' '));
  svg.classList.add('sample');
  svg.setAttribute('aria-hidden', 'true');
  const txt = document.createElementNS(svgNS, 'text');
  txt.setAttribute('x', frame ? 0 : annotationFrame.textX);
  txt.setAttribute('y', frame ? 0 : annotationFrame.baseline);
  txt.setAttribute('text-anchor', annotationFrame.textAnchor);
  txt.style.fontFamily = f.face;
  txt.style.fontSize = annotationFrame.fontSize + 'px';
  txt.setAttribute('fill', 'currentColor');
  txt.style.fontVariationSettings = '"wght" ' + v.wght + ', "wdth" ' + v.wdth + ', "RADI" ' + v.RADI;
  const sequence = frame && f.operators[v.name];
  txt.textContent = sequence || String.fromCodePoint(0xf0000 + gid);
  if (sequence) txt.style.fontFeatureSettings = '"ss01" 1';
  svg.append(txt);
  return svg;
}
function persist(v, change) {
  const key = keyFor(v),
    now = new Date().toISOString();
  const old = marks.get(key);
  const item = {
    schema: 1,
    ...v,
    fontFile: fonts[v.family].file,
    fontSha256: fonts[v.family].sha256,
    glyphID: fonts[v.family].ids.get(v.name),
    unicode: [...catalogue.get(v.name).codes].map(ucode),
    sequence: fonts[v.family].operators[v.name] || null,
    regions: [],
    note: '',
    createdAt: now,
    ...old,
    ...change,
    updatedAt: now,
  };
  marks.set(key, item);
  let stored = true;
  try {
    localStorage.setItem(key, JSON.stringify(item));
  } catch {
    stored = false;
    warn('标记暂存在本页内存。请导出问题文件后再关闭页面。');
  }
  syncFlags();
  if ($('lens').open)
    $('detailStatus').textContent = item.active
      ? stored
        ? '已保存到本机'
        : '已标记，可导出'
      : '当前组合未标记';
}
function toggle(v) {
  persist(v, { active: !marks.get(keyFor(v))?.active });
}
const activeMarks = () => [...marks.values()].filter((v) => v.active);
function syncFlags() {
  const n = activeMarks().length;
  $('count').textContent = n;
  $('export').disabled = $('exportList').disabled = !(n || previousObservations.length);
  for (const btn of $('matrices').querySelectorAll('.case'))
    btn.setAttribute('aria-pressed', !!marks.get(btn.dataset.key)?.active);
  if (selected) {
    const record = marks.get(keyFor(selected));
    $('flagDetail').textContent = record?.active ? '撤销此组合标记' : '标记此组合';
    $('undoRegion').disabled = !record?.regions?.length;
  }
}
function matrix(family, frame) {
  const section = tag('section');
  section.className = 'family';
  const column = ['Sans', 'Serif', 'Mono', 'Symbols'].indexOf(label(family).split(' ')[0]);
  section.style.setProperty('--order', column + (family.endsWith('-Italic') ? 3 : 0));
  const title = tag('h2', label(family).replace(' Italic', ''));
  if (family.endsWith('-Italic')) title.append(tag('em', ' Italic'));
  section.append(title);
  const scroll = tag('div');
  scroll.className = 'scroll';
  const table = tag('table');
  table.setAttribute('aria-label', label(family) + ' 的字重、字宽和圆角');
  const head = table.createTHead().insertRow();
  for (const value of ['宽 / 角', ...weights]) {
    const th = tag('th', value);
    th.scope = 'col';
    head.append(th);
  }
  const body = table.createTBody();
  const { widths, radii } = matrixAxes();
  for (const r of radii) {
    for (const d of widths) {
      const row = body.insertRow();
      if (r !== radii[0] && d === 65) row.className = 'second';
      const h = tag('th', d + '%');
      h.scope = 'row';
      h.className = 'axis';
      h.append(tag('small', 'R' + r));
      row.append(h);
      for (const w of weights) {
        const v = spec(page.name, family, w, d, r),
          button = tag('button');
        button.className = 'case';
        button.setAttribute('aria-label', page.name + ' · ' + infoFor(v));
        button.dataset.key = keyFor(v);
        button.setAttribute('aria-pressed', !!marks.get(keyFor(v))?.active);
        button.append(sample(v, frame));
        button.onclick = (e) => {
          if (mode === 'zoom' || e.shiftKey) openLens(v);
          else toggle(v);
        };
        button.onkeydown = (e) => {
          if (e.key.toLowerCase() === 'z') {
            e.preventDefault();
            openLens(v);
          }
        };
        row.insertCell().append(button);
      }
    }
  }
  scroll.append(table);
  section.append(scroll);
  return section;
}
const grid = $('matrices');
let layout = null;

function fitMatrix() {
  if (!layout || !grid.classList.contains('overview')) return;
  const { width, height } = grid.getBoundingClientRect();
  const { faces, rows, frame } = layout;
  if (width < 1 || height < 1) return;
  const css = getComputedStyle(grid);
  const gap = parseFloat(css.columnGap),
    axis = parseFloat(css.getPropertyValue('--axis-width'));
  const headings =
    parseFloat(css.getPropertyValue('--face-height')) +
    parseFloat(css.getPropertyValue('--weight-height'));
  let best = -1,
    columns = 1,
    cellWidth = 0,
    cellHeight = 0;
  for (let cols = 1; cols <= faces; cols++) {
    const bands = Math.ceil(faces / cols);
    const w = ((width - gap * (cols - 1)) / cols - axis) / weights.length;
    const h = ((height - gap * (bands - 1)) / bands - headings - 2) / rows;
    if (cols > 1 && w < 10) continue;
    const scale = Math.min((w - 3) / frame[2], (h - 2) / frame[3]);
    if (scale > best) {
      best = scale;
      columns = cols;
      cellWidth = w;
      cellHeight = h;
    }
  }
  grid.style.setProperty('--columns', columns);
  grid.style.setProperty('--bands', Math.ceil(faces / columns));
  const captionSize = Math.max(7, Math.min(11, (cellWidth - 1) / 2));
  grid.style.setProperty('--caption-size', captionSize + 'px');
  grid.style.setProperty('--label-size', Math.min(captionSize, Math.max(5, cellHeight - 1.5)) + 'px');
  grid.classList.toggle('by-style', columns === 3);
}

const preview = $('hoverPreview');
let previewCell = null,
  hoverTimer = 0;
function hidePreview() {
  clearTimeout(hoverTimer);
  preview.hidden = true;
  previewCell = null;
}
function showPreview(cell) {
  if (!cell.isConnected || document.querySelector('dialog[open], #settings:popover-open')) return;
  const anchor = cell.getBoundingClientRect();
  preview.style.setProperty('--preview-width', Math.max(250, anchor.width * 1.75) + 'px');
  preview.style.setProperty('--preview-height', Math.max(216, anchor.height * 1.75) + 'px');
  $('hoverSample').replaceChildren(cell.querySelector('svg').cloneNode(true));
  $('hoverLabel').textContent = cell.getAttribute('aria-label');
  preview.hidden = false;
  const panel = preview.getBoundingClientRect();
  const margin = 6,
    gap = 12;
  const right = anchor.right + gap,
    left = anchor.left - gap - panel.width;
  let x = right,
    y = anchor.top + (anchor.height - panel.height) / 2;
  if (right + panel.width > innerWidth - margin) {
    if (left >= margin) x = left;
    else {
      x = anchor.left + (anchor.width - panel.width) / 2;
      y =
        anchor.top > innerHeight - anchor.bottom ? anchor.top - panel.height - gap : anchor.bottom + gap;
    }
  }
  preview.style.left = Math.max(margin, Math.min(x, innerWidth - panel.width - margin)) + 'px';
  preview.style.top = Math.max(margin, Math.min(y, innerHeight - panel.height - margin)) + 'px';
  previewCell = cell;
}
grid.addEventListener('pointerover', (e) => {
  if (e.pointerType !== 'mouse' && !(e.pointerType === 'pen' && e.buttons === 0)) return;
  const cell = e.target.closest('.case');
  if (!cell || cell === previewCell) return;
  clearTimeout(hoverTimer);
  if (preview.hidden) hoverTimer = setTimeout(() => showPreview(cell), 90);
  else showPreview(cell);
});
grid.addEventListener('pointerout', (e) => {
  const cell = e.target.closest('.case');
  if (cell && !e.relatedTarget?.closest?.('.case')) hidePreview();
});
grid.addEventListener('focusin', (e) => {
  if (e.target.matches('.case:focus-visible')) showPreview(e.target);
});
grid.addEventListener('focusout', hidePreview);
grid.addEventListener('pointerdown', hidePreview);
window.addEventListener('blur', hidePreview);
window.addEventListener('scroll', hidePreview, true);
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') hidePreview();
});
new ResizeObserver(() => {
  hidePreview();
  fitMatrix();
}).observe(grid);

async function render() {
  const id = ++generation,
    i = pages.indexOf(page),
    shown = page.families.filter((f) => !$('family').value || f === $('family').value);
  $('pageNumber').textContent = i + 1 + ' / ' + pages.length;
  $('prev').disabled = i === 0;
  $('next').disabled = i === pages.length - 1;
  $('name').textContent = page.name;
  $('name').title = page.name;
  document.title = page.name + ' · Admiralty 逐字审稿';
  const codes = [...page.codes];
  const op = fonts[page.families[0]].operators[page.name];
  $('unicode').textContent = codes.length
    ? codes.map(ucode).join(' · ')
    : op
      ? '无独立码位 · ' + op + ' 的连字部件'
      : '无独立码位';
  const blank = shown.every((f) => fonts[f].blank.includes(page.name));
  const { widths, radii } = matrixAxes();
  const num = shown.length * weights.length * widths.length * radii.length;
  $('coverage').textContent =
    shown.length + ' 个字型 · ' + num + ' 个组合' + (blank ? ' · 此字形为空白' : '');
  $('matrices').replaceChildren();
  hidePreview();
  $('status').textContent = '正在载入校样字体…';
  try {
    await Promise.all(shown.map(faceReady));
  } catch {
    if (id !== generation) return;
    $('status').replaceChildren(
      '字体载入失败。 ',
      Object.assign(tag('button', '重新载入'), { onclick: render }),
    );
    return;
  }
  if (id !== generation) return;
  const frame = specimenFrame(shown);
  layout = { faces: shown.length, rows: widths.length * radii.length, frame };
  grid.replaceChildren(...shown.map((family) => matrix(family, frame)));
  fitMatrix();
  $('status').textContent = '';
  syncFlags();
}
function go(name, remember = true) {
  const next = catalogue.get(name);
  if (!next) return;
  const preferred = $('family').value;
  page = next;
  $('family').replaceChildren(
    new Option('全部字型', ''),
    ...page.families.map((f) => new Option(label(f), f)),
  );
  if (page.families.includes(preferred)) $('family').value = preferred;
  const u = new URL(location.href);
  u.searchParams.set('glyph', name);
  try {
    history.replaceState(null, '', u);
  } catch {
    /* file origins may restrict history */
  }
  if (remember) {
    try {
      localStorage.setItem(positionKey, name);
    } catch {
      /* storage status is shown when marking */
    }
  }
  render();
}
function turn(n) {
  const next = pages[pages.indexOf(page) + n];
  if (next) go(next.name);
}
$('prev').onclick = () => turn(-1);
$('next').onclick = () => turn(1);
$('family').onchange = $('radius').onchange = render;
$('sampling').onchange = () => {
  const old = $('radius').value;
  const values = $('sampling').value === 'intermediate' ? [0, 50, 100] : [0, 100];
  $('radius').replaceChildren(new Option('全部', ''), ...values.map((r) => new Option(r, r)));
  if (values.map(String).includes(old)) $('radius').value = old;
  render();
};
$('overview').onclick = () => {
  const on = $('matrices').classList.toggle('overview');
  $('overview').setAttribute('aria-pressed', on);
  fitMatrix();
};
function setMode(value) {
  mode = value;
  $('flagMode').setAttribute('aria-pressed', value === 'flag');
  $('zoomMode').setAttribute('aria-pressed', value === 'zoom');
}
$('flagMode').onclick = () => setMode('flag');
$('zoomMode').onclick = () => setMode('zoom');

const initialExamples = [...new Set(previousObservations.flatMap((item) => item.glyphs))];
function searchResults() {
  const q = $('query').value.trim(),
    lower = q.toLowerCase();
  const cp = /^u\+[\da-f]{1,6}$/i.test(q)
    ? parseInt(q.slice(2), 16)
    : [...q].length === 1
      ? q.codePointAt(0)
      : null;
  function rank(p) {
    if (p.codes.has(cp) || p.name === q) return 0;
    const n = p.name.toLowerCase();
    if (n === lower) return 1;
    if (n.startsWith(lower)) return 2;
    if (n.includes(lower)) return 3;
    if (p.families.some((f) => fonts[f].operators[p.name] === q)) return 4;
    return 5;
  }
  const results = q
    ? pages
        .map((p) => [rank(p), p])
        .filter(([r]) => r < 5)
        .sort((a, b) => a[0] - b[0])
        .slice(0, 70)
        .map((row) => row[1])
    : initialExamples.map((n) => catalogue.get(n)).filter(Boolean);
  $('matches').replaceChildren(
    ...results.map((p) => {
      const b = tag('button', p.name);
      b.append(tag('small', [...p.codes].map(ucode).join(' · ')));
      b.onclick = () => {
        $('finder').close();
        go(p.name);
        window.scrollTo(0, 0);
      };
      return b;
    }),
  );
  if (!results.length) $('matches').append(tag('p', '没有匹配的字形。可以输入字符、字形名或 U+ 码位。'));
}
function findGlyph() {
  hidePreview();
  $('query').value = '';
  searchResults();
  $('finder').showModal();
  $('query').focus();
}
$('search').onclick = findGlyph;
$('query').oninput = searchResults;
$('query').onkeydown = (e) => {
  if (e.isComposing) return;
  if (e.key === 'Enter') {
    e.preventDefault();
    $('matches').querySelector('button')?.click();
  }
  if (e.key === 'ArrowDown') {
    e.preventDefault();
    $('matches').querySelector('button')?.focus();
  }
};
document.addEventListener('keydown', (e) => {
  if (
    e.defaultPrevented ||
    e.isComposing ||
    e.metaKey ||
    e.ctrlKey ||
    e.altKey ||
    document.querySelector('dialog[open], #settings:popover-open') ||
    e.target.closest('input,textarea,select,[contenteditable]')
  )
    return;
  if (['ArrowRight', 'ArrowLeft', '/'].includes(e.key)) {
    e.preventDefault();
    if (e.key === '/') findGlyph();
    else turn(e.key === 'ArrowRight' ? 1 : -1);
  }
});
for (const b of document.querySelectorAll('[data-close]')) b.onclick = () => b.closest('dialog').close();

function renderRegions(extra) {
  const regions = marks.get(keyFor(selected))?.regions || [];
  $('regions').replaceChildren(
    ...[...regions, ...(extra ? [extra] : [])].map(({ x, y, w, h }) => {
      const region = tag('span');
      region.className = 'region';
      Object.assign(region.style, {
        left: x * 100 + '%',
        top: y * 100 + '%',
        width: w * 100 + '%',
        height: h * 100 + '%',
      });
      return region;
    }),
  );
}
function showDetail(v) {
  endDrag();
  selected = v;
  $('lensTitle').textContent = v.name + ' · ' + label(v.family);
  $('lensMeta').textContent = '字重 ' + v.wght + ' · 字宽 ' + v.wdth + '% · 圆角 ' + v.RADI;
  $('customWeight').value = v.wght;
  $('customWidth').value = v.wdth;
  $('customRadius').value = v.RADI;
  $('large').replaceChildren(sample(v));
  $('reference').replaceChildren(sample({ ...v, wght: 400 }));
  selectReference(false);
  const sequence = fonts[v.family].operators[v.name];
  $('operatorContext').hidden = !sequence;
  if (sequence) {
    const line = sample(v, specimenFrame([v.family]));
    $('operatorContext').replaceChildren('完整连字 ' + sequence, line);
  }
  const record = marks.get(keyFor(v));
  $('note').value = record?.note || '';
  $('detailStatus').textContent = record?.active ? '此组合已标记' : '可直接拖动圈注，或写下问题。';
  renderRegions();
  syncFlags();
}
function selectReference(ref) {
  $('pair').classList.toggle('show-ref', ref);
  $('showCurrent').setAttribute('aria-pressed', !ref);
  $('showRef').setAttribute('aria-pressed', ref);
}
$('showCurrent').onclick = () => selectReference(false);
$('showRef').onclick = () => selectReference(true);
async function openLens(v) {
  hidePreview();
  try {
    await faceReady(v.family);
  } catch {
    warn('这个字型尚未载入，请重试。');
    return;
  }
  showDetail(v);
  if (!$('lens').open) $('lens').showModal();
}
$('lens').onclose = () => {
  endDrag();
  selected = null;
};
$('flagDetail').onclick = () => toggle(selected);
$('note').oninput = () => {
  if ($('note').value || marks.get(keyFor(selected)))
    persist(selected, { active: true, note: $('note').value });
};
$('applyAxes').onclick = () => {
  const nums = [$('customWeight'), $('customWidth'), $('customRadius')];
  for (const el of nums) if (!el.value || !el.reportValidity()) return;
  showDetail(spec(selected.name, selected.family, ...nums.map((el) => el.valueAsNumber)));
};
function point(e) {
  const el = $('board'),
    r = el.getBoundingClientRect(),
    clamp = (v) => Math.max(0, Math.min(1, v));
  return [
    clamp((e.clientX - r.left - el.clientLeft) / el.clientWidth),
    clamp((e.clientY - r.top - el.clientTop) / el.clientHeight),
  ];
}
function boundsOf(a, b) {
  const [x, y] = a,
    [u, v] = b;
  return { x: Math.min(x, u), y: Math.min(y, v), w: Math.abs(x - u), h: Math.abs(y - v) };
}
const board = $('board');
function endDrag() {
  if (!drag) return;
  const id = drag.id;
  drag = null;
  $('lens').classList.remove('is-drawing');
  if (board.hasPointerCapture(id)) board.releasePointerCapture(id);
}
board.onselectstart = board.ondragstart = (e) => e.preventDefault();
board.onpointerdown = (e) => {
  if (e.button !== 0 || drag) return;
  e.preventDefault();
  board.focus({ preventScroll: true });
  document.getSelection()?.removeAllRanges();
  drag = { id: e.pointerId, start: point(e) };
  $('lens').classList.add('is-drawing');
  board.setPointerCapture(e.pointerId);
};
board.onpointermove = (e) => {
  if (drag?.id !== e.pointerId) return;
  e.preventDefault();
  renderRegions(boundsOf(drag.start, point(e)));
};
board.onpointerup = (e) => {
  if (drag?.id !== e.pointerId) return;
  const r = boundsOf(drag.start, point(e));
  endDrag();
  if (r.w > 0.012 && r.h > 0.012)
    persist(selected, { active: true, regions: [...(marks.get(keyFor(selected))?.regions || []), r] });
  renderRegions();
};
board.onlostpointercapture = board.onpointercancel = (e) => {
  if (drag?.id !== e.pointerId) return;
  endDrag();
  if (selected) renderRegions();
};
$('undoRegion').onclick = () => {
  const m = marks.get(keyFor(selected));
  if (!m?.regions.length) return;
  persist(selected, { regions: m.regions.slice(0, -1) });
  renderRegions();
};

function renderList() {
  const items = activeMarks().sort(
    (a, b) =>
      a.name.localeCompare(b.name) ||
      a.family.localeCompare(b.family) ||
      a.wght - b.wght ||
      a.wdth - b.wdth ||
      a.RADI - b.RADI,
  );
  $('ledgerMeta').textContent =
    items.length + ' 个组合 · ' + new Set(items.map((v) => v.name)).size + ' 个字形';
  $('entries').replaceChildren(
    ...items.map((v) => {
      const button = tag('button'),
        left = tag('span', v.name + ' · ' + infoFor(v));
      if (v.note || v.regions.length) {
        left.append(
          tag('br'),
          tag(
            'small',
            [v.regions.length ? v.regions.length + ' 处圈注' : '', v.note].filter(Boolean).join(' · '),
          ),
        );
      }
      const current = fonts[v.family]?.sha256 === v.fontSha256 && catalogue.has(v.name);
      button.append(left, tag('span', current ? '↗' : '旧版'));
      button.disabled = !current;
      button.onclick = () => {
        $('ledger').close();
        go(v.name);
        openLens(v);
      };
      return button;
    }),
  );
  if (!items.length) $('entries').append(tag('p', '还没有标记。看到问题时，点一下对应的格子即可。'));
}
$('issues').onclick = () => {
  hidePreview();
  renderList();
  $('ledger').showModal();
};
$('previousCount').textContent = previousObservations.length + ' 组';
for (const item of previousObservations) {
  const p = tag('p', item.note),
    shortcuts = tag('div');
  for (const name of item.glyphs) {
    const b = tag('button', name);
    b.onclick = () => {
      $('ledger').close();
      go(name);
      window.scrollTo(0, 0);
    };
    shortcuts.append(b);
  }
  $('previousEntries').append(shortcuts, p);
}
function exportReport() {
  const issues = activeMarks();
  if (!issues.length && !previousObservations.length) return;
  const report = {
    schema: 'admiralty-glyph-review/1',
    exportedAt: new Date().toISOString(),
    issueCount: issues.length,
    annotationFrame,
    previousScreenshotObservations: previousObservations,
    issues: issues.map(({ schema, active, name, ...rest }) => ({ glyph: name, ...rest })),
  };
  const url = URL.createObjectURL(
    new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' }),
  );
  const a = tag('a');
  a.href = url;
  a.download = 'Admiralty-字形问题-' + report.exportedAt.replace(/[:.]/g, '-') + '.json';
  document.body.append(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 30000);
}
$('export').onclick = $('exportList').onclick = exportReport;
window.addEventListener('storage', (e) => {
  if (!e.key?.startsWith(issuePrefix)) return;
  try {
    if (e.newValue) marks.set(e.key, JSON.parse(e.newValue));
    else marks.delete(e.key);
  } catch {
    return;
  }
  syncFlags();
  if ($('ledger').open) renderList();
  if (selected && keyFor(selected) === e.key && document.activeElement !== $('note'))
    showDetail(selected);
});
go(page.name, false);
syncFlags();
