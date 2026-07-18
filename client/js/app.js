'use strict';

/* Schedula — модуль «Расписание», главный экран.
   Данные пока мок-наборы из вайрфрейма; при подключении API сервера
   заменяются загрузкой (структуры state.lessons/teachers/rooms сохраняются). */

const DAYS = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт'];
const SLOTS = 7;
const GROUPS = ['ИС-31', 'ИС-32', 'ПКС-21', 'ПКС-22', 'ЭК-11'];
const ROOMTYPES = ['Лекционная', 'Семинарская', 'Комп. класс', 'Лаборатория', 'Спортивный зал', 'Актовый зал'];
const GEN_STAGES = ['Готовлю данные…', 'Размещаю лекции…', 'Размещаю практики…', 'Разрешаю конфликты аудиторий…', 'Проверяю пожелания…'];

function initialTeachers() {
  return [
    { id: 't1', name: 'Орлова И.К.', c: { hard: ['0-6', '1-6'], soft: [], method: 2, max: 4 } },
    { id: 't2', name: 'Ким Д.С.', c: { hard: ['0-0', '0-1'], soft: ['4-5', '4-6'], method: null, max: 3 } },
    { id: 't3', name: 'Стеклов П.А.', c: { hard: [], soft: ['0-0'], method: 4, max: 4 } },
    { id: 't4', name: 'Белов А.Н.', c: null },
    { id: 't5', name: 'Юсупова Р.М.', c: { hard: ['3-5', '3-6', '4-5', '4-6'], soft: [], method: null, max: null } },
    { id: 't6', name: 'Дроздова Е.В.', c: { hard: [], soft: ['0-5', '0-6'], method: null, max: 4 } },
    { id: 't7', name: 'Гарин О.Л.', c: null },
    { id: 't8', name: 'Мельник С.С.', c: { hard: ['2-0', '2-1', '2-2'], soft: [], method: null, max: 4 } },
    { id: 't9', name: 'Ахматова Л.Р.', c: null },
    { id: 't10', name: 'Козлов В.П.', c: null }
  ];
}

function initialRooms() {
  return [
    { id: '214', type: 'Лекционная', cap: 80 }, { id: '118', type: 'Лекционная', cap: 120 },
    { id: '301', type: 'Лекционная', cap: 60 }, { id: '305', type: 'Лекционная', cap: 40 },
    { id: '220', type: 'Лекционная', cap: 50 }, { id: 'к.412', type: 'Комп. класс', cap: 25 },
    { id: 'к.413', type: 'Комп. класс', cap: 25 }, { id: 'лаб.2', type: 'Лаборатория', cap: 20 }
  ];
}

function initialLessons() {
  // [группа, дисциплина, вид, преподаватель, аудитория, размещено[[d,s]...], ещё в пуле, opts]
  const SPEC = [
    ['ИС-31', 'Матанализ', 'lec', 't1', '214', [[0, 0]], 0],
    ['ИС-31', 'Матанализ', 'prac', 't1', '214', [[0, 1]], 1],
    ['ИС-31', 'Программирование', 'prac', 't2', 'к.412', [[1, 0]], 1],
    ['ИС-31', 'Программирование', 'lec', 't2', '214', [[4, 5]], 0],
    ['ИС-31', 'Физика', 'lec', 't3', '118', [[3, 0]], 0],
    ['ИС-31', 'История', 'lec', 't4', '301', [[1, 1]], 0],
    ['ИС-31', 'БЖД', 'lec', 't5', '220', [[2, 1]], 0, { pin: true }],
    ['ИС-31', 'Англ. язык', 'prac', 't6', '305', [[4, 1]], 1],
    ['ИС-31', 'Базы данных', 'prac', 't2', 'к.413', [], 2],
    ['ИС-32', 'История', 'lec', 't4', '301', [[1, 1]], 0],
    ['ИС-32', 'Матанализ', 'lec', 't1', '214', [[1, 0]], 1],
    ['ИС-32', 'Философия', 'lec', 't9', '305', [[3, 2]], 0, { orphan: true }],
    ['ИС-32', 'Программирование', 'prac', 't2', 'к.412', [[2, 3]], 1],
    ['ИС-32', 'Физика', 'lec', 't3', '118', [[3, 1]], 0],
    ['ИС-32', 'Англ. язык', 'prac', 't6', '305', [[0, 2]], 1],
    ['ПКС-21', 'Веб-разработка', 'prac', 't7', 'к.413', [[0, 0], [2, 0]], 1],
    ['ПКС-21', 'ОС и сети', 'lec', 't8', '220', [[1, 2]], 1],
    ['ПКС-21', 'Матанализ', 'lec', 't1', '118', [[3, 2]], 0],
    ['ПКС-21', 'История', 'lec', 't4', '301', [[4, 0]], 0],
    ['ПКС-21', 'Базы данных', 'prac', 't10', 'к.412', [], 2],
    ['ПКС-22', 'Веб-разработка', 'prac', 't7', 'к.413', [[0, 1], [2, 1]], 0],
    ['ПКС-22', 'ОС и сети', 'lec', 't8', '220', [[4, 2]], 1],
    ['ПКС-22', 'Англ. язык', 'prac', 't6', '305', [[1, 3]], 1],
    ['ПКС-22', 'Физика', 'lec', 't3', '118', [[2, 4]], 0],
    ['ПКС-22', 'История', 'lec', 't4', '301', [], 1],
    ['ЭК-11', 'Статистика', 'lec', 't8', '214', [[0, 0]], 0],
    ['ЭК-11', 'Экономика', 'lec', 't9', '301', [[0, 3], [2, 2]], 1],
    ['ЭК-11', 'Матанализ', 'prac', 't1', '305', [[1, 2]], 1],
    ['ЭК-11', 'Англ. язык', 'prac', 't6', '305', [[3, 3]], 0],
    ['ЭК-11', 'Информатика', 'prac', 't10', 'к.412', [], 2]
  ];
  let id = 0;
  const lessons = [];
  SPEC.forEach(row => {
    const [g, disc, kind, t, room, placed, extra] = row;
    const opts = row[7] || {};
    const total = placed.length + extra;
    placed.forEach((pos, i) => {
      lessons.push({ id: 'l' + (++id), g, disc, kind, t, room, d: pos[0], s: pos[1], pin: !!opts.pin, orphan: !!opts.orphan, ni: i + 1, nt: total });
    });
    for (let i = 0; i < extra; i++) {
      lessons.push({ id: 'l' + (++id), g, disc, kind, t, room, d: null, s: null, pin: false, orphan: false, ni: placed.length + i + 1, nt: total });
    }
  });
  return lessons;
}

const state = {
  period: 'a', view: 'group',
  ent: { group: 'ИС-31', teacher: 't1', room: '214' },
  lessons: initialLessons(), teachers: initialTeachers(), rooms: initialRooms(),
  undo: [], redo: [],
  tab: 'pool', q: '', kindF: 'all', scopeAll: true,
  dragId: null, sel: [], cursor: null,
  newIds: [], flashId: null,
  gen: null, dlg: null, co: null, ex: null, rm: null
};

let genTimer = null;
let flashTimer = null;

/* ---------- helpers ---------- */

const $ = s => document.querySelector(s);
const esc = s => String(s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const clone = o => JSON.parse(JSON.stringify(o));
const lOf = id => state.lessons.find(l => l.id === id);
const plural = (n, one, few, many) => n === 1 ? one : n < 5 ? few : many;
const teacherMap = () => { const m = {}; state.teachers.forEach(t => m[t.id] = t); return m; };

/* ---------- undo / redo ---------- */

function mutate(fn, extra) {
  const lessons = clone(state.lessons);
  fn(lessons);
  state.undo = [...state.undo.slice(-49), JSON.stringify(state.lessons)];
  state.redo = [];
  state.newIds = [];
  state.lessons = lessons;
  Object.assign(state, extra || {});
  render();
}

function doUndo() {
  if (!state.undo.length) return;
  const prev = state.undo[state.undo.length - 1];
  state.redo = [...state.redo, JSON.stringify(state.lessons)];
  state.undo = state.undo.slice(0, -1);
  state.lessons = JSON.parse(prev);
  state.newIds = []; state.sel = [];
  render();
}

function doRedo() {
  if (!state.redo.length) return;
  const nx = state.redo[state.redo.length - 1];
  state.undo = [...state.undo, JSON.stringify(state.lessons)];
  state.redo = state.redo.slice(0, -1);
  state.lessons = JSON.parse(nx);
  state.newIds = []; state.sel = [];
  render();
}

/* ---------- анализ конфликтов ---------- */

function analyze(lessons, teachers) {
  const byId = {};
  const add = (id, sev, text) => { (byId[id] = byId[id] || []).push({ sev, text }); };
  const tMap = {}; teachers.forEach(t => tMap[t.id] = t);
  lessons.filter(l => l.orphan && l.d != null).forEach(l => add(l.id, 'orphan', 'Назначение снято в «Распределении» — пара осиротела'));
  const placed = lessons.filter(l => l.d != null && !l.orphan);
  const grp = fn => { const m = {}; placed.forEach(l => { const k = fn(l); (m[k] = m[k] || []).push(l); }); return m; };
  Object.values(grp(l => l.t + '|' + l.d + '|' + l.s)).forEach(a => { if (a.length > 1) a.forEach(l => add(l.id, 'hard', 'Преподаватель в двух местах одновременно')); });
  Object.values(grp(l => l.g + '|' + l.d + '|' + l.s)).forEach(a => { if (a.length > 1) a.forEach(l => add(l.id, 'hard', 'Группа в двух местах одновременно')); });
  Object.values(grp(l => l.room + '|' + l.d + '|' + l.s)).forEach(a => { if (a.length > 1) a.forEach(l => add(l.id, 'hard', 'Аудитория ' + l.room + ' занята')); });
  placed.forEach(l => {
    const c = tMap[l.t] && tMap[l.t].c;
    if (!c) return;
    const k = l.d + '-' + l.s;
    if (c.method === l.d) add(l.id, 'hard', 'Методический день преподавателя');
    else if (c.hard.indexOf(k) >= 0) add(l.id, 'hard', 'Преподаватель недоступен в этот слот');
    else if (c.soft.indexOf(k) >= 0) add(l.id, 'soft', 'Нежелательный слот преподавателя');
  });
  Object.values(grp(l => l.t + '|' + l.d)).forEach(a => {
    const c = tMap[a[0].t] && tMap[a[0].t].c;
    if (c && c.max && a.length > c.max) a.forEach(l => add(l.id, 'hard', 'Превышен максимум пар в день (' + c.max + ')'));
  });
  let hardN = 0, softN = 0, orphanN = 0;
  Object.keys(byId).forEach(id => {
    const sevs = byId[id].map(x => x.sev);
    if (sevs.indexOf('hard') >= 0) hardN++;
    else if (sevs.indexOf('orphan') >= 0) orphanN++;
    else softN++;
  });
  return { byId, hardN, softN, orphanN };
}

// статус постановки пары L в слот (d,s) с аудиторией r
function slotStatus(L, d, s, r, lessons, teachers) {
  lessons = lessons || state.lessons; teachers = teachers || state.teachers;
  const tMap = {}; teachers.forEach(t => tMap[t.id] = t);
  const others = lessons.filter(x => x.id !== L.id && x.d === d && x.s === s && !x.orphan);
  if (others.some(x => x.t === L.t)) return { kind: 'hard', text: 'Преподаватель ' + tMap[L.t].name + ' уже занят в этом слоте' };
  if (others.some(x => x.g === L.g)) return { kind: 'hard', text: 'Группа ' + L.g + ' уже занята в этом слоте' };
  if (others.some(x => x.room === (r || L.room))) return { kind: 'hard', text: 'Аудитория ' + (r || L.room) + ' занята' };
  const c = (tMap[L.t] || {}).c;
  if (c) {
    const k = d + '-' + s;
    if (c.method === d) return { kind: 'hard', text: 'Методический день преподавателя' };
    if (c.hard.indexOf(k) >= 0) return { kind: 'hard', text: 'Преподаватель недоступен в этот слот' };
    if (c.max) {
      const n = lessons.filter(x => x.id !== L.id && x.t === L.t && x.d === d && !x.orphan).length;
      if (n + 1 > c.max) return { kind: 'hard', text: 'Превышен максимум пар в день (' + c.max + ')' };
    }
    if (c.soft.indexOf(k) >= 0) return { kind: 'soft', text: 'Нежелательный слот преподавателя — можно, но генератор бы избегал' };
  }
  return { kind: 'free', text: 'Слот свободен, конфликтов нет' };
}

/* ---------- операции с парами ---------- */

function place(id, d, s, room) {
  const L = lOf(id);
  if (!L) return;
  const extra = { flashId: id, dragId: null, sel: [] };
  if (state.view === 'group' && L.g !== state.ent.group) extra.ent = Object.assign({}, state.ent, { group: L.g });
  mutate(ls => { const x = ls.find(l => l.id === id); x.d = d; x.s = s; if (room) x.room = room; }, extra);
  clearTimeout(flashTimer);
  flashTimer = setTimeout(() => { state.flashId = null; render(); }, 2500);
}

function removeLessons(ids) {
  if (!ids.length) return;
  mutate(ls => ls.forEach(l => { if (ids.indexOf(l.id) >= 0) { l.d = null; l.s = null; l.pin = false; } }), { sel: [] });
}

function pinLessons(ids) {
  if (!ids.length) return;
  mutate(ls => ls.forEach(l => { if (ids.indexOf(l.id) >= 0 && l.d != null) l.pin = !l.pin; }));
}

function visibleLessons() {
  if (state.view === 'group') return state.lessons.filter(l => l.g === state.ent.group);
  if (state.view === 'teacher') return state.lessons.filter(l => l.t === state.ent.teacher);
  return state.lessons.filter(l => l.room === state.ent.room);
}

function entList() {
  if (state.view === 'group') return GROUPS.map(g => ({ v: g, label: g }));
  if (state.view === 'teacher') return state.teachers.map(t => ({ v: t.id, label: t.name }));
  return state.rooms.map(r => ({ v: r.id, label: r.id + ' · ' + r.type }));
}

function entStep(dir) {
  const list = entList();
  const cur = state.view === 'group' ? state.ent.group : state.view === 'teacher' ? state.ent.teacher : state.ent.room;
  const i = Math.max(0, list.findIndex(o => o.v === cur));
  const nx = list[(i + dir + list.length) % list.length].v;
  const ent = Object.assign({}, state.ent); ent[state.view] = nx;
  state.ent = ent;
  render();
}

function openDlg(id) {
  const L = lOf(id);
  if (!L) return;
  state.dlg = { id, d: String(L.d != null ? L.d : 0), s: String(L.s != null ? L.s : 0), r: L.room };
  render();
}

function problemGo(id) {
  const l = lOf(id);
  if (!l) return;
  state.view = 'group';
  state.ent = Object.assign({}, state.ent, { group: l.g });
  state.cursor = l.d != null ? { d: l.d, s: l.s } : null;
  state.flashId = id;
  state.sel = [id];
  render();
  clearTimeout(flashTimer);
  flashTimer = setTimeout(() => { state.flashId = null; render(); }, 2500);
}

/* ---------- генерация ---------- */

function computeGen(mode) {
  const lessons = clone(state.lessons);
  const teachers = state.teachers;
  let moved = 0;
  if (mode === 'rebuild') lessons.forEach(l => { if (l.d != null && !l.pin && !l.orphan) { l.d = null; l.s = null; moved++; } });
  const todo = lessons.filter(l => l.d == null).sort((a, b) => (a.kind === b.kind ? 0 : a.kind === 'lec' ? -1 : 1));
  const newIds = []; let softUsed = 0;
  todo.forEach(L => {
    let softBest = null;
    outer:
    for (let d = 0; d < DAYS.length; d++) {
      for (let s = 0; s < SLOTS; s++) {
        const st = slotStatus(L, d, s, null, lessons, teachers);
        if (st.kind === 'hard') continue;
        if (st.kind === 'soft') { if (!softBest) softBest = [d, s]; continue; }
        L.d = d; L.s = s; newIds.push(L.id); break outer;
      }
    }
    if (L.d == null && softBest) { L.d = softBest[0]; L.s = softBest[1]; newIds.push(L.id); softUsed++; }
  });
  const unplaced = lessons.filter(l => l.d == null);
  return { lessons, newIds, placedN: newIds.length, unplacedN: unplaced.length, softN: softUsed, moved, unplaced };
}

function openGen() {
  state.gen = { phase: 'prep', mode: 'rebuild' };
  state.sel = [];
  render();
}

function genRun() {
  const result = computeGen(state.gen.mode);
  state.gen = { phase: 'run', mode: state.gen.mode, pct: 0, stage: 0, result };
  render();
  clearInterval(genTimer);
  genTimer = setInterval(() => {
    if (!state.gen || state.gen.phase !== 'run') { clearInterval(genTimer); return; }
    const pct = Math.min(100, state.gen.pct + 3 + Math.random() * 7);
    if (pct >= 100) {
      clearInterval(genTimer);
      state.gen = Object.assign({}, state.gen, { phase: 'done', pct: 100 });
    } else {
      state.gen = Object.assign({}, state.gen, { pct, stage: Math.min(GEN_STAGES.length - 1, Math.floor(pct / 20)) });
    }
    render();
  }, 130);
}

function genCancel() {
  clearInterval(genTimer);
  state.gen = null;
  render();
}

function genAccept() {
  const r = state.gen.result;
  mutate(ls => { ls.length = 0; r.lessons.forEach(l => ls.push(l)); }, { gen: null, newIds: r.newIds });
}

/* ---------- справочники ---------- */

function coSetC(fn) {
  const teachers = clone(state.teachers);
  const t = teachers.find(x => x.id === state.co.tid);
  if (!t.c) t.c = { hard: [], soft: [], method: null, max: 4 };
  fn(t.c);
  state.teachers = teachers;
  render();
}

function coSlotClick(k) {
  coSetC(c => {
    const hi = c.hard.indexOf(k), si = c.soft.indexOf(k);
    if (hi >= 0) { c.hard.splice(hi, 1); c.soft.push(k); }
    else if (si >= 0) { c.soft.splice(si, 1); }
    else { c.hard.push(k); }
  });
}

function rmAdd() {
  const rm = state.rm;
  if (!rm) return;
  const idv = (rm.id || '').trim();
  if (!idv) { state.rm = Object.assign({}, rm, { err: 'Укажите номер или название аудитории' }); render(); return; }
  if (state.rooms.some(r => r.id.toLowerCase() === idv.toLowerCase())) {
    state.rm = Object.assign({}, rm, { err: 'Аудитория «' + idv + '» уже есть в справочнике' }); render(); return;
  }
  const cap = Math.max(1, parseInt(rm.cap, 10) || 1);
  state.rooms = [...state.rooms, { id: idv, type: rm.type, cap }];
  state.rm = { id: '', type: rm.type, cap: rm.cap, err: '' };
  render();
}

function rmDel(id) {
  const used = state.lessons.filter(l => l.room === id).length;
  if (used) return;
  state.rooms = state.rooms.filter(r => r.id !== id);
  if (state.ent.room === id) state.ent = Object.assign({}, state.ent, { room: state.rooms.length ? state.rooms[0].id : '' });
  render();
}

/* ---------- рендер ---------- */

const appEl = document.getElementById('app');
const overlaysEl = document.getElementById('overlays');

function captureFocus() {
  const el = document.activeElement;
  if (!el || !el.id) return null;
  const f = { id: el.id };
  if (el.tagName === 'INPUT') { f.s = el.selectionStart; f.e = el.selectionEnd; }
  return f;
}

function restoreFocus(f) {
  if (!f) return;
  const el = document.getElementById(f.id);
  if (!el) return;
  el.focus();
  if (f.s != null && el.setSelectionRange) { try { el.setSelectionRange(f.s, f.e); } catch (_) { } }
}

function captureScrolls() {
  const m = {};
  document.querySelectorAll('[data-keep-scroll]').forEach(el => m[el.dataset.keepScroll] = { t: el.scrollTop, l: el.scrollLeft });
  return m;
}

function restoreScrolls(m) {
  document.querySelectorAll('[data-keep-scroll]').forEach(el => {
    const s = m[el.dataset.keepScroll];
    if (s) { el.scrollTop = s.t; el.scrollLeft = s.l; }
  });
}

function render() {
  const foc = captureFocus();
  const scr = captureScrolls();
  const an = analyze(state.lessons, state.teachers);
  const tMap = teacherMap();
  const isSpring = state.period === 's';
  appEl.innerHTML = railHtml(an)
    + '<div class="main">' + headerHtml(an) + (isSpring ? springHtml() : workspaceHtml(an, tMap)) + '</div>';
  overlaysEl.innerHTML = genHtml() + dlgHtml(tMap) + coHtml() + rmHtml() + exHtml(an);
  restoreScrolls(scr);
  restoreFocus(foc);
}

function railHtml(an) {
  const badge = an.orphanN > 0 ? `<span class="rail-badge">${an.orphanN}</span>` : '';
  return `<nav class="rail">
    <div class="rail-logo">УП</div>
    <button class="rail-item" type="button" title="Модуль «Распределение» (в разработке)">
      <span class="rail-ico"></span><span class="rail-label">Распр.</span>
    </button>
    <div class="rail-item active" title="Расписание (текущий модуль)">
      <span class="rail-ico"><span class="rail-dash"></span></span>
      <span class="rail-label">Расп.</span>${badge}
    </div>
  </nav>`;
}

function headerHtml(an) {
  const placedN = state.lessons.filter(l => l.d != null).length;
  const totalN = state.lessons.length;
  const problemsN = an.hardN + an.orphanN;
  const pct = totalN ? Math.round(placedN / totalN * 100) : 0;
  const seg = (items, cur, act) => '<div class="seg">' + items.map(i =>
    `<button class="seg-btn${cur === i.k ? ' active' : ''}" data-act="${act}" data-k="${i.k}">${i.label}</button>`).join('') + '</div>';
  const confHas = problemsN > 0;
  const confLabel = confHas ? `⚠ ${problemsN} ${plural(problemsN, 'проблема', 'проблемы', 'проблем')}` : '✓ нет проблем';
  return `<header class="app-header">
    <span class="app-title">Расписание · 2026/27</span>
    ${seg([{ k: 'a', label: 'Осень' }, { k: 's', label: 'Весна' }], state.period, 'period')}
    ${seg([{ k: 'group', label: 'Группы' }, { k: 'teacher', label: 'Преподаватели' }, { k: 'room', label: 'Аудитории' }], state.view, 'view')}
    <div class="progress">
      <div class="progress-label">выставлено ${placedN} из ${totalN} пар</div>
      <div class="progress-track"><div class="progress-fill" style="width:${pct}%"></div></div>
    </div>
    <span class="spacer"></span>
    <button class="conf${confHas ? ' has' : ''}" data-act="open-problems" title="Открыть панель проблем">${confLabel}</button>
    <div class="hgroup">
      <button class="iconbtn${state.undo.length ? '' : ' dim'}" data-act="undo" title="Отменить (Ctrl+Z)">↶</button>
      <button class="iconbtn${state.redo.length ? '' : ' dim'}" data-act="redo" title="Повторить (Ctrl+Shift+Z)">↷</button>
    </div>
    <button class="btn" data-act="open-rooms">Аудитории</button>
    <button class="btn" data-act="open-constraints">Ограничения</button>
    <button class="btn btn--primary" data-act="open-gen">⟳ Сгенерировать</button>
    <button class="btn" data-act="open-export">Экспорт</button>
  </header>`;
}

function springHtml() {
  return `<div class="spring">
    <span class="spring-ico">∅</span>
    <span class="spring-title">На весенний период нет назначений</span>
    <span class="spring-text">В сетку попадают только дисциплины, назначенные преподавателям. Сделайте назначения на весну в модуле «Распределение».</span>
    <button class="spring-cta" type="button" title="Модуль «Распределение» (в разработке)">Перейти к распределению →</button>
  </div>`;
}

function workspaceHtml(an, tMap) {
  return `<div class="workspace">${gridPanelHtml(an, tMap)}${rightPanelHtml(an, tMap)}</div>`;
}

function cardHtml(l, an, tMap, d, s) {
  const issues = an.byId[l.id] || [];
  const isHard = issues.some(x => x.sev === 'hard');
  const isSoft = issues.some(x => x.sev === 'soft');
  const cls = ['card'];
  if (l.orphan) cls.push('card--orphan');
  else if (isHard) cls.push('card--hard');
  else if (l.kind === 'lec') cls.push('card--lec');
  else cls.push('card--prac');
  if (state.sel.indexOf(l.id) >= 0) cls.push('card--sel');
  if (state.flashId === l.id || state.newIds.indexOf(l.id) >= 0) cls.push('card--new');
  if (state.dragId === l.id) cls.push('card--drag');
  const icons = [(l.pin ? '⌖' : ''), (isHard ? '⚠' : ''), (isSoft && !isHard ? '◐' : ''), (l.orphan ? '◌' : '')].filter(Boolean).join(' ');
  const icCls = isHard ? ' ic-red' : (l.orphan || isSoft) ? ' ic-amber' : '';
  const who = state.view === 'group' ? tMap[l.t].name : l.g;
  const sub = who + ' · ' + l.room + (state.view === 'room' ? ' · ' + tMap[l.t].name : '');
  const tip = issues.length ? issues.map(x => x.text).join(' · ')
    : (l.pin ? 'Закреплена — перегенерация не тронет' : 'Перетащите, кликните для выбора, двойной клик — диалог');
  return `<div class="${cls.join(' ')}" draggable="true" data-act="card" data-id="${l.id}" data-drag="${l.id}" data-d="${d}" data-s="${s}" title="${esc(tip)}">
    <div class="card-head"><span class="card-title">${(l.kind === 'lec' ? '● ' : '▪ ') + esc(l.disc)}</span>${icons ? `<span class="card-icons${icCls}">${icons}</span>` : ''}</div>
    <div class="card-sub">${esc(sub)}</div>
  </div>`;
}

function gridPanelHtml(an, tMap) {
  const vis = visibleLessons();
  const entOpts = entList();
  const entVal = state.view === 'group' ? state.ent.group : state.view === 'teacher' ? state.ent.teacher : state.ent.room;
  const entPlaced = vis.filter(l => l.d != null).length;
  const curT = state.view === 'teacher' ? tMap[state.ent.teacher] : null;
  const entWarn = !!(curT && !curT.c);
  const dragL = state.dragId ? lOf(state.dragId) : null;
  const meta = state.view === 'group' ? `${entPlaced} / ${vis.length} пар` : `${entPlaced} пар в неделю`;

  let selbar = '';
  if (state.sel.length) {
    selbar = `<div class="selbar">
      <span class="selbar-label">Выбрано: ${state.sel.length}</span>
      <button class="selbar-btn" data-act="sel-pin" title="Закрепить / открепить (P)">⌖ Pin</button>
      <button class="selbar-btn" data-act="sel-move" title="Разместить через диалог (Enter)">Разместить…</button>
      <button class="selbar-btn" data-act="sel-remove" title="Снять в пул (Del)">✕ Снять</button>
      <button class="selbar-x" data-act="sel-clear" title="Esc">×</button>
    </div>`;
  }

  let cellsHtml = '<span></span>' + DAYS.map(d => `<span class="grid-day">${d}</span>`).join('');
  for (let s = 0; s < SLOTS; s++) {
    cellsHtml += `<span class="grid-slot">${s + 1}</span>`;
    for (let d = 0; d < DAYS.length; d++) {
      const here = vis.filter(l => l.d === d && l.s === s);
      const cls = ['cell'];
      let tag = '';
      if (curT && curT.c) {
        const k = d + '-' + s;
        if (curT.c.method === d || curT.c.hard.indexOf(k) >= 0) cls.push('cell--blocked');
        else if (curT.c.soft.indexOf(k) >= 0) cls.push('cell--softslot');
      }
      if (dragL) {
        const stt = slotStatus(dragL, d, s);
        if (stt.kind === 'free') cls.push('cell--drop-free');
        else if (stt.kind === 'soft') { cls.push('cell--drop-soft'); if (!here.length) tag = '<span class="cell-tag cell-tag--soft">◐ пожелание</span>'; }
        else { cls.push('cell--drop-hard'); if (!here.length) tag = '<span class="cell-tag cell-tag--hard">⚠ конфликт</span>'; }
      } else if (!here.length) {
        cls.push('cell--empty');
      }
      if (state.cursor && state.cursor.d === d && state.cursor.s === s) cls.push('cell--cursor');
      const cards = here.map(l => cardHtml(l, an, tMap, d, s)).join('');
      cellsHtml += `<div class="${cls.join(' ')}" data-act="cell" data-d="${d}" data-s="${s}">${cards}${tag}</div>`;
    }
  }

  return `<section class="panel grid-panel">
    <div class="grid-toolbar">
      <button class="navbtn" data-act="ent-prev" title="Предыдущая (PgUp)">‹</button>
      <select id="entSelect" class="ent-select" data-act="ent-pick">${entOpts.map(o =>
        `<option value="${esc(o.v)}"${o.v === entVal ? ' selected' : ''}>${esc(o.label)}</option>`).join('')}</select>
      <button class="navbtn" data-act="ent-next" title="Следующая (PgDn)">›</button>
      <span class="ent-meta">${meta}</span>
      ${entWarn ? '<span class="warn-chip">ограничения не заданы — считается полностью доступным</span>' : ''}
      <span class="spacer"></span>
      ${selbar}
    </div>
    <div id="gridScroll" class="grid-scroll" tabindex="0" data-keep-scroll="grid">
      <div class="grid">${cellsHtml}</div>
      <div class="grid-hint">перетаскивание пары · клик — выбрать · двойной клик — разместить через диалог · стрелки + Enter · P — pin · Del — снять · / — поиск · Ctrl+Z — отмена</div>
    </div>
  </section>`;
}

function problemList(an, tMap) {
  const items = [];
  state.lessons.forEach(l => {
    const issues = an.byId[l.id];
    if (!issues) return;
    const isHard = issues.some(x => x.sev === 'hard');
    const isOrphan = issues.some(x => x.sev === 'orphan');
    items.push({
      id: l.id,
      title: (l.kind === 'lec' ? '● ' : '▪ ') + l.disc + ' · ' + l.g,
      icon: isHard ? '⚠' : isOrphan ? '◌' : '◐',
      sevCls: isHard ? 'hard' : 'soft',
      hard: isHard,
      text: issues.map(x => x.text).join(' · '),
      loc: l.d != null ? (DAYS[l.d] + ', ' + (l.s + 1) + ' пара · ' + tMap[l.t].name) : 'в пуле'
    });
  });
  items.sort((a, b) => (a.hard ? 0 : 1) - (b.hard ? 0 : 1));
  return items;
}

function rightPanelHtml(an, tMap) {
  const unplaced = state.lessons.filter(l => l.d == null);
  const problems = problemList(an, tMap);
  const tabs = [
    { k: 'pool', label: 'Пул · ' + unplaced.length, alert: false },
    { k: 'problems', label: 'Проблемы · ' + problems.length, alert: problems.length > 0 }
  ].map(t => `<button class="tab${state.tab === t.k ? ' active' : ''}${t.alert ? ' alert' : ''}" data-act="tab" data-k="${t.k}">${t.label}</button>`).join('');

  let body = '';
  if (state.tab === 'pool') {
    const q = state.q.trim().toLowerCase();
    const pool = unplaced.filter(l => {
      if (state.kindF !== 'all' && l.kind !== state.kindF) return false;
      if (!state.scopeAll && state.view === 'group' && l.g !== state.ent.group) return false;
      if (q && (l.disc + ' ' + l.g + ' ' + tMap[l.t].name).toLowerCase().indexOf(q) < 0) return false;
      return true;
    });
    const chips = [
      { label: 'Все', active: state.kindF === 'all', act: 'chip-kind', k: 'all' },
      { label: '● Лекции', active: state.kindF === 'lec', act: 'chip-kind', k: 'lec' },
      { label: '▪ Практики', active: state.kindF === 'prac', act: 'chip-kind', k: 'prac' },
      { label: state.scopeAll ? 'Все группы' : 'Текущая группа', active: true, act: 'chip-scope', k: '' }
    ].map(c => `<button class="chip${c.active ? ' active' : ''}" data-act="${c.act}" data-k="${c.k}">${c.label}</button>`).join('');
    const cards = pool.map(l => `<div class="pool-card" draggable="true" data-drag="${l.id}" title="Перетащите в сетку или нажмите «Разместить»">
      <div class="pool-row">
        <span class="kind kind--${l.kind}">${l.kind === 'lec' ? '●' : '▪'}</span>
        <span class="pool-title">${esc(l.disc + ' · ' + l.g)}</span>
        <span class="pool-norm">пара ${l.ni} из ${l.nt}</span>
      </div>
      <div class="pool-row">
        <span class="pool-sub">${esc(tMap[l.t].name + ' · ' + l.room)}</span>
        <button class="pool-place" data-act="pool-place" data-id="${l.id}">Разместить</button>
      </div>
    </div>`).join('');
    let emptyMsg = '';
    if (unplaced.length === 0) {
      emptyMsg = `<div class="empty empty--ok"><span class="empty-ico">✓</span><span class="empty-title">Всё расставлено</span>
        <span class="empty-text">Все пары периода стоят в сетке. Проверьте панель проблем перед экспортом.</span></div>`;
    } else if (pool.length === 0) {
      emptyMsg = `<div class="empty empty--filter"><span style="font-size:13px">Ничего не найдено</span>
        <button class="smallbtn" data-act="reset-filters">Сбросить фильтры</button></div>`;
    }
    body = `<div class="pool-filters">
        <input id="poolSearch" class="search" value="${esc(state.q)}" placeholder="Поиск: дисциплина, группа, ФИО…  ( / )">
        <div class="chips">${chips}</div>
      </div>
      <div class="pool-list" data-keep-scroll="pool">${cards}${emptyMsg}</div>`;
  } else {
    const items = problems.map(p => `<div class="problem problem--${p.sevCls}" data-act="problem-go" data-id="${p.id}">
      <div class="problem-head"><span class="problem-ico">${p.icon}</span><span class="problem-title">${esc(p.title)}</span></div>
      <div class="problem-text">${esc(p.text)}</div>
      <div class="problem-loc">${esc(p.loc)}</div>
    </div>`).join('');
    const none = problems.length === 0 ? `<div class="empty empty--ok"><span class="empty-ico">✓</span><span class="empty-title">Проблем нет</span>
      <span class="empty-text">Конфликтов, осиротевших пар и нарушенных пожеланий не найдено.</span></div>` : '';
    body = `<div class="pool-list" data-keep-scroll="problems">${items}${none}</div>`;
  }
  return `<aside class="panel right-panel"><div class="tabs-wrap"><div class="tabs">${tabs}</div></div>${body}</aside>`;
}

/* ---------- оверлеи ---------- */

function genHtml() {
  const gen = state.gen;
  if (!gen) return '';
  const totalN = state.lessons.length;
  const placedN = state.lessons.filter(l => l.d != null).length;
  const unplacedN = state.lessons.filter(l => l.d == null).length;
  const noConstraints = state.teachers.filter(t => !t.c).length;
  const pinnedN = state.lessons.filter(l => l.pin && l.d != null).length;
  const placedActive = state.lessons.filter(l => l.d != null && !l.pin && !l.orphan).length;
  const title = gen.phase === 'done' ? 'Результат генерации' : gen.phase === 'run' ? 'Генерация…' : 'Генерация расписания';
  let body = '';

  if (gen.phase === 'prep') {
    const checks = [
      { ok: true, text: `Назначено пар: ${totalN} (из «Распределения»), в сетке ${placedN}` },
      {
        ok: noConstraints === 0,
        text: noConstraints ? `У ${noConstraints} преподавателей не заданы ограничения — генератор считает их полностью доступными` : 'Ограничения заданы у всех преподавателей',
        fix: 'gen-fix-co', fixLabel: 'Задать'
      },
      { ok: true, text: `Справочник аудиторий: ${state.rooms.length} аудиторий, типы заданы`, fix: 'gen-fix-rooms', fixLabel: 'Открыть' },
      { ok: true, text: 'Нормы пар/нед: авто из часов плана, ручных правок нет' },
      { ok: pinnedN === 0, text: pinnedN ? `Закреплено пар: ${pinnedN} — генератор их не тронет` : 'Закреплённых пар нет' }
    ];
    const checksHtml = checks.map(c => `<div class="check ${c.ok ? 'check--ok' : 'check--warn'}">
      <span class="check-ico">${c.ok ? '✓' : '⚠'}</span>
      <div class="check-text">${esc(c.text)}</div>
      ${c.fix ? `<button class="check-fix" data-act="${c.fix}">${c.fixLabel}</button>` : ''}
    </div>`).join('');
    const mode = gen.mode || 'rebuild';
    const modes = [
      { k: 'rebuild', title: 'Пересобрать всё, кроме закреплённых', desc: `Снимет ${placedActive} незакреплённых пар и расставит заново вместе с пулом. ${pinnedN} закреплённых не изменятся.` },
      { k: 'fill', title: 'Только доразместить', desc: `Расставленные пары не трогаются; генератор заполнит пустые слоты парами из пула (${unplacedN}).` }
    ].map(m => `<div class="mode${mode === m.k ? ' active' : ''}" data-act="gen-mode" data-k="${m.k}">
      <span class="mode-dot"><span></span></span>
      <div><div class="mode-title">${m.title}</div><div class="mode-desc">${m.desc}</div></div>
    </div>`).join('');
    const warn = mode === 'rebuild' && placedActive > 0
      ? `<div class="alertbox alertbox--red"><span>⚠</span><span>Будет переставлено ${placedActive} незакреплённых пар; ${pinnedN} закреплённых не изменятся. Результат можно откатить одним шагом.</span></div>`
      : '';
    body = `<div class="sheet">
      <div class="note">Генератор — черновик: он расставит пары с учётом ограничений, дальше — доводка руками. Результат можно откатить целиком одним Ctrl+Z.</div>
      <div class="vgroup"><div class="mono-label">ГОТОВНОСТЬ ДАННЫХ</div>${checksHtml}</div>
      <div class="vgroup"><div class="mono-label">РЕЖИМ</div>${modes}</div>
      ${warn}
    </div>
    <div class="modal-foot"><button class="btn" data-act="gen-close">Отмена</button><span class="spacer"></span><button class="btn btn--primary" data-act="gen-run">Запустить генерацию</button></div>`;
  } else if (gen.phase === 'run') {
    const r = gen.result;
    const pct = Math.round(gen.pct || 0);
    body = `<div class="gen-run">
      <span class="spinner"></span>
      <div class="gen-progress">
        <div class="gen-stage"><span>${GEN_STAGES[Math.min(gen.stage || 0, GEN_STAGES.length - 1)]}</span><span class="gen-pct">${pct} %</span></div>
        <div class="gen-track"><div class="gen-fill" style="width:${pct}%"></div></div>
        <div class="gen-live">размещено ${Math.round(pct / 100 * r.placedN)} / ${r.placedN + r.unplacedN}</div>
      </div>
      <button class="btn" data-act="gen-cancel">Отменить</button>
      <div class="gen-note">Отмена вернёт сетку к состоянию до запуска. Сетка на время генерации доступна только для чтения.</div>
    </div>`;
  } else {
    const r = gen.result;
    const issues = [];
    r.unplaced.slice(0, 4).forEach(l => issues.push({
      icon: '✕', cls: 'ic-red',
      text: `${l.disc} (${l.kind === 'lec' ? 'лекция' : 'практика'}) · ${l.g} — не нашлось слота без конфликта; пара осталась в пуле`
    }));
    if (r.softN) issues.push({ icon: '◐', cls: 'ic-amber', text: `Нарушено мягких пожеланий: ${r.softN} — см. панель проблем после принятия` });
    const issuesHtml = issues.map(i => `<div class="issue"><span class="issue-ico ${i.cls}">${i.icon}</span><div class="issue-text">${esc(i.text)}</div></div>`).join('');
    body = `<div class="sheet">
      <div class="stats">
        <div class="stat stat--green"><div class="stat-n">${r.placedN}</div><div class="stat-cap">размещено</div></div>
        <div class="stat ${r.unplacedN ? 'stat--red' : 'stat--mute'}"><div class="stat-n">${r.unplacedN}</div><div class="stat-cap">не размещено</div></div>
        <div class="stat ${r.softN ? 'stat--amber' : 'stat--mute'}"><div class="stat-n">${r.softN}</div><div class="stat-cap">пожеланий нарушено</div></div>
      </div>
      <div class="note">${gen.mode === 'rebuild' ? 'Пересобрано ' + r.moved + ' пар. ' : ''}Жёсткие ограничения не нарушены. Неразмещённые пары остались в пуле с причиной.</div>
      ${issuesHtml}
      <div class="subnote">Новые пары подсвечены в сетке. «Принять» фиксирует результат (откат — Ctrl+Z одним шагом), «Откатить» возвращает всё как было.</div>
    </div>
    <div class="modal-foot"><button class="btn" data-act="gen-rollback">Откатить всё</button><span class="spacer"></span><button class="btn btn--green" data-act="gen-accept">Принять результат</button></div>`;
  }

  return `<div class="backdrop backdrop--drawer" data-act="gen-backdrop">
    <div class="drawer">
      <div class="modal-head"><span class="modal-title">${title}</span><button class="modal-x" data-act="gen-close" title="Закрыть (Esc)">×</button></div>
      ${body}
    </div>
  </div>`;
}

function dlgHtml(tMap) {
  const dlg = state.dlg;
  if (!dlg) return '';
  const L = lOf(dlg.id);
  if (!L) return '';
  const stt = slotStatus(L, parseInt(dlg.d), parseInt(dlg.s), dlg.r);
  const icons = { free: '✓', soft: '◐', hard: '⚠' };
  return `<div class="backdrop" data-act="dlg-backdrop">
    <div class="modal modal--place">
      <div class="modal-head"><span class="modal-title">Разместить пару</span><button class="modal-x" data-act="dlg-close" title="Закрыть (Esc)">×</button></div>
      <div class="dlg-body">
        <div class="dlg-lesson">
          <span class="kind kind--${L.kind}">${L.kind === 'lec' ? '●' : '▪'}</span>
          <span class="dlg-lesson-title">${esc(L.disc + ' · ' + L.g)}</span>
          <span class="dlg-lesson-sub">${esc(tMap[L.t].name)}</span>
        </div>
        <div class="grid3">
          <div class="field"><span class="opt-label">День</span>
            <select id="dlgD" data-act="dlg-d">${DAYS.map((d, i) => `<option value="${i}"${String(i) === dlg.d ? ' selected' : ''}>${d}</option>`).join('')}</select>
          </div>
          <div class="field"><span class="opt-label">Пара</span>
            <select id="dlgS" data-act="dlg-s">${Array.from({ length: SLOTS }, (_, i) => `<option value="${i}"${String(i) === dlg.s ? ' selected' : ''}>${i + 1} пара</option>`).join('')}</select>
          </div>
          <div class="field"><span class="opt-label">Аудитория</span>
            <select id="dlgR" data-act="dlg-r">${state.rooms.map(r => `<option value="${esc(r.id)}"${r.id === dlg.r ? ' selected' : ''}>${esc(r.id + ' · ' + r.type + ' · ' + r.cap)}</option>`).join('')}</select>
          </div>
        </div>
        <div class="status status--${stt.kind}"><span class="status-ico">${icons[stt.kind]}</span><span class="status-text">${esc(stt.text)}</span></div>
        <div class="hint-note">Конфликт не блокирует размещение — он будет подсвечен в сетке и попадёт в панель проблем.</div>
      </div>
      <div class="modal-foot"><button class="btn" data-act="dlg-close">Отмена</button><span class="spacer"></span><button class="btn btn--primary" data-act="dlg-confirm">Разместить</button></div>
    </div>
  </div>`;
}

function coHtml() {
  const co = state.co;
  if (!co) return '';
  const t = state.teachers.find(x => x.id === co.tid);
  const c = t.c || { hard: [], soft: [], method: null, max: null };
  const list = state.teachers.map(x => `<div class="co-item${x.id === co.tid ? ' active' : ''}" data-act="co-teacher" data-id="${x.id}">
    <span class="co-name">${esc(x.name)}</span>
    <span class="co-st ${x.c ? 'co-st--set' : 'co-st--unset'}">${x.c ? 'заданы' : 'не заданы'}</span>
  </div>`).join('');
  let grid = '<span></span>' + DAYS.map(d => `<span class="co-dh">${d}</span>`).join('');
  for (let s = 0; s < SLOTS; s++) {
    grid += `<span class="co-rl">${s + 1}</span>`;
    for (let d = 0; d < DAYS.length; d++) {
      const k = d + '-' + s;
      const isM = c.method === d, isH = c.hard.indexOf(k) >= 0, isS = c.soft.indexOf(k) >= 0;
      const cls = isM ? 'slot slot--m' : isH ? 'slot slot--h' : isS ? 'slot slot--s' : 'slot';
      const tip = isM ? 'Методический день' : isH ? 'Недоступен' : isS ? 'Нежелательно' : 'Свободно';
      grid += `<span class="${cls}" title="${tip}"${isM ? '' : ` data-act="co-slot" data-k="${k}"`}></span>`;
    }
  }
  const days = DAYS.map((d, i) => `<button class="daybtn${c.method === i ? ' active' : ''}" data-act="co-method" data-i="${i}">${d}</button>`).join('');
  return `<div class="backdrop" data-act="co-backdrop">
    <div class="modal modal--co">
      <div class="modal-head"><span class="modal-title">Ограничения преподавателей</span><button class="modal-x" data-act="co-close" title="Закрыть (Esc)">×</button></div>
      <div class="co-body">
        <div class="co-list" data-keep-scroll="co">${list}</div>
        <div class="co-main">
          <div class="co-title">${esc(t.name)}</div>
          <div class="vgroup">
            <div class="mono-label">НЕДОСТУПНЫЕ И НЕЖЕЛАТЕЛЬНЫЕ СЛОТЫ · клик циклит: свободно → недоступно → нежелательно</div>
            <div class="co-grid">${grid}</div>
            <div class="legend">
              <span><span class="sw sw--h"></span> недоступен</span>
              <span><span class="sw sw--s"></span> нежелательно</span>
              <span><span class="sw sw--m"></span> методический день</span>
            </div>
          </div>
          <div class="co-opts">
            <div class="co-opt"><span class="opt-label">МЕТОДИЧЕСКИЙ ДЕНЬ</span><div class="daybtns">${days}</div></div>
            <div class="co-opt"><span class="opt-label">МАКСИМУМ ПАР В ДЕНЬ</span>
              <div class="stepper">
                <button class="step-btn" data-act="co-max-dec">−</button>
                <span class="step-val">${c.max ? c.max : '—'}</span>
                <button class="step-btn" data-act="co-max-inc">＋</button>
              </div>
            </div>
          </div>
          <div class="co-foot-note">Жёсткие ограничения генератор не нарушает; нежелательные слоты постарается избежать и покажет, где не смог. Изменения сразу учитываются в проверке конфликтов. Преподаватель без ограничений считается полностью доступным.</div>
        </div>
      </div>
    </div>
  </div>`;
}

function rmHtml() {
  const rm = state.rm;
  if (!rm) return '';
  const usage = {};
  state.lessons.forEach(l => { usage[l.room] = (usage[l.room] || 0) + 1; });
  const rows = state.rooms.map(r => {
    const used = usage[r.id] || 0;
    return `<div class="rm-grid rm-row">
      <span class="rm-id">${esc(r.id)}</span>
      <span class="rm-type">${esc(r.type)}</span>
      <span class="rm-usage" style="color:${used ? '#5C574E' : '#A8A399'}">${used ? used + ' ' + plural(used, 'пара', 'пары', 'пар') : 'свободна'}</span>
      <button class="rm-del" data-act="rm-del" data-id="${esc(r.id)}" title="${used ? 'Нельзя удалить: на аудиторию назначено пар — ' + used : 'Удалить аудиторию'}" style="color:${used ? '#C9C5BB' : '#C24536'};cursor:${used ? 'not-allowed' : 'pointer'}">✕</button>
    </div>`;
  }).join('');
  const types = ROOMTYPES.map(x => `<option value="${esc(x)}"${x === rm.type ? ' selected' : ''}>${esc(x)}</option>`).join('');
  return `<div class="backdrop" data-act="rm-backdrop">
    <div class="modal modal--rooms">
      <div class="modal-head"><span class="modal-title">Аудитории · ${state.rooms.length}</span><button class="modal-x" data-act="rm-close" title="Закрыть (Esc)">×</button></div>
      <div class="rm-form">
        <div class="mono-label">НОВАЯ АУДИТОРИЯ</div>
        <div class="rm-row-form">
          <input id="rmId" class="rm-input" value="${esc(rm.id)}" placeholder="Номер / название">
          <div class="rm-selwrap"><select id="rmType" class="rm-select" data-act="rm-type">${types}</select><span class="rm-arrow">▾</span></div>
          <button class="rm-add" data-act="rm-add">＋ Добавить</button>
        </div>
        ${rm.err ? `<div class="rm-err"><span>⚠</span><span>${esc(rm.err)}</span></div>` : ''}
      </div>
      <div class="rm-list" data-keep-scroll="rooms">
        <div class="rm-grid rm-head"><span>АУДИТОРИЯ</span><span>ТИП</span><span>ЗАНЯТОСТЬ</span><span></span></div>
        ${rows}
      </div>
      <div class="rm-note">Новая аудитория сразу доступна в диалоге размещения, представлении «Аудитории» и учитывается генератором. Удалить можно только аудиторию без назначенных пар.</div>
    </div>
  </div>`;
}

function exHtml(an) {
  const ex = state.ex;
  if (!ex) return '';
  const unplaced = state.lessons.filter(l => l.d == null).length;
  const problemsN = an.hardN + an.orphanN;
  let body;
  if (ex.step === 'config') {
    const viewBtns = [{ k: 'group', label: 'По группам' }, { k: 'teacher', label: 'По преподавателям' }]
      .map(b => `<button class="opt${ex.view === b.k ? ' active' : ''}" data-act="ex-view" data-k="${b.k}">${b.label}</button>`).join('');
    const scopeBtns = [
      { k: 'all', label: 'Все (' + (ex.view === 'teacher' ? state.teachers.length : GROUPS.length) + ')' },
      { k: 'cur', label: 'Только текущая' }
    ].map(b => `<button class="opt${ex.scope === b.k ? ' active' : ''}" data-act="ex-scope" data-k="${b.k}">${b.label}</button>`).join('');
    const warn = (unplaced > 0 || problemsN > 0)
      ? `<div class="alertbox alertbox--amber"><span>⚠</span><span>Расписание неполное: не размещено пар — ${unplaced}, проблем — ${problemsN}. Выгрузка не блокируется.</span></div>`
      : '';
    body = `<div class="ex-body">
      <div class="vgroup"><span class="opt-label">ПРЕДСТАВЛЕНИЕ</span><div class="optrow">${viewBtns}</div></div>
      <div class="vgroup"><span class="opt-label">ОХВАТ</span><div class="optrow">${scopeBtns}</div></div>
      ${warn}
      <div class="ex-preview">предпросмотр листа: сетка дни × пары, ${ex.view === 'teacher' ? 'один преподаватель = один лист' : 'одна группа = один лист'}</div>
    </div>
    <div class="modal-foot"><button class="btn" data-act="ex-close">Отмена</button><span class="spacer"></span><button class="btn btn--primary" data-act="ex-run">Выгрузить в Excel</button></div>`;
  } else {
    body = `<div class="ex-done">
      <span class="ex-check">✓</span>
      <span class="ex-done-title">Файл сформирован (мок)</span>
      <span class="ex-file">расписание_${ex.view === 'teacher' ? 'преподаватели' : 'группы'}_осень.xlsx</span>
      <button class="btn" data-act="ex-close">Закрыть</button>
    </div>`;
  }
  return `<div class="backdrop" data-act="ex-backdrop">
    <div class="modal modal--ex">
      <div class="modal-head"><span class="modal-title">Экспорт расписания</span><button class="modal-x" data-act="ex-close" title="Закрыть (Esc)">×</button></div>
      ${body}
    </div>
  </div>`;
}

/* ---------- события ---------- */

// клик по этим областям закрывает оверлей только если попал в сам фон, не в контент
const BACKDROP_ACTS = { 'gen-backdrop': 1, 'dlg-backdrop': 1, 'co-backdrop': 1, 'rm-backdrop': 1, 'ex-backdrop': 1 };

function onClick(e) {
  const el = e.target.closest('[data-act]');
  if (!el) return;
  const act = el.dataset.act;
  if (BACKDROP_ACTS[act] && e.target !== el) return;
  switch (act) {
    case 'period': state.period = el.dataset.k; render(); break;
    case 'view': state.view = el.dataset.k; state.cursor = null; state.sel = []; render(); break;
    case 'open-problems': state.tab = 'problems'; render(); break;
    case 'undo': doUndo(); break;
    case 'redo': doRedo(); break;
    case 'open-rooms': case 'gen-fix-rooms': state.rm = { id: '', type: ROOMTYPES[0], cap: '40', err: '' }; render(); break;
    case 'open-constraints': state.co = { tid: state.teachers[0].id }; render(); break;
    case 'gen-fix-co': {
      const t = state.teachers.find(x => !x.c) || state.teachers[0];
      state.co = { tid: t.id }; render(); break;
    }
    case 'open-gen': openGen(); break;
    case 'open-export': state.ex = { step: 'config', view: 'group', scope: 'all' }; render(); break;
    case 'ent-prev': entStep(-1); break;
    case 'ent-next': entStep(1); break;
    case 'sel-pin': pinLessons(state.sel); break;
    case 'sel-move': if (state.sel.length) openDlg(state.sel[0]); break;
    case 'sel-remove': removeLessons(state.sel); break;
    case 'sel-clear': state.sel = []; render(); break;
    case 'cell': state.cursor = { d: +el.dataset.d, s: +el.dataset.s }; state.sel = []; render(); break;
    case 'card': {
      const id = el.dataset.id;
      const multi = e.shiftKey || e.ctrlKey || e.metaKey;
      state.sel = multi
        ? (state.sel.indexOf(id) >= 0 ? state.sel.filter(x => x !== id) : [...state.sel, id])
        : [id];
      state.cursor = { d: +el.dataset.d, s: +el.dataset.s };
      render(); break;
    }
    case 'tab': state.tab = el.dataset.k; render(); break;
    case 'chip-kind': state.kindF = el.dataset.k; render(); break;
    case 'chip-scope': state.scopeAll = !state.scopeAll; render(); break;
    case 'reset-filters': state.q = ''; state.kindF = 'all'; state.scopeAll = true; render(); break;
    case 'pool-place': openDlg(el.dataset.id); break;
    case 'problem-go': problemGo(el.dataset.id); break;
    case 'gen-backdrop': if (state.gen && state.gen.phase !== 'run') genCancel(); break;
    case 'gen-close': case 'gen-cancel': case 'gen-rollback': genCancel(); break;
    case 'gen-mode': state.gen = Object.assign({}, state.gen, { mode: el.dataset.k }); render(); break;
    case 'gen-run': genRun(); break;
    case 'gen-accept': genAccept(); break;
    case 'dlg-backdrop': case 'dlg-close': state.dlg = null; render(); break;
    case 'dlg-confirm': {
      const dlg = state.dlg;
      if (dlg) { state.dlg = null; place(dlg.id, parseInt(dlg.d), parseInt(dlg.s), dlg.r); }
      break;
    }
    case 'co-backdrop': case 'co-close': state.co = null; render(); break;
    case 'co-teacher': state.co = { tid: el.dataset.id }; render(); break;
    case 'co-slot': coSlotClick(el.dataset.k); break;
    case 'co-method': coSetC(c => { const i = +el.dataset.i; c.method = c.method === i ? null : i; }); break;
    case 'co-max-dec': coSetC(c => { c.max = Math.max(1, (c.max || 4) - 1); }); break;
    case 'co-max-inc': coSetC(c => { c.max = Math.min(8, (c.max || 4) + 1); }); break;
    case 'rm-backdrop': case 'rm-close': state.rm = null; render(); break;
    case 'rm-add': rmAdd(); break;
    case 'rm-del': rmDel(el.dataset.id); break;
    case 'ex-backdrop': case 'ex-close': state.ex = null; render(); break;
    case 'ex-view': state.ex = Object.assign({}, state.ex, { view: el.dataset.k }); render(); break;
    case 'ex-scope': state.ex = Object.assign({}, state.ex, { scope: el.dataset.k }); render(); break;
    case 'ex-run': state.ex = Object.assign({}, state.ex, { step: 'done' }); render(); break;
  }
}

function onDblClick(e) {
  const card = e.target.closest('.card[data-id]');
  if (card) openDlg(card.dataset.id);
}

function onChange(e) {
  const el = e.target.closest('[data-act]');
  if (!el) return;
  switch (el.dataset.act) {
    case 'ent-pick': {
      const ent = Object.assign({}, state.ent);
      ent[state.view] = el.value;
      state.ent = ent; render(); break;
    }
    case 'dlg-d': state.dlg = Object.assign({}, state.dlg, { d: el.value }); render(); break;
    case 'dlg-s': state.dlg = Object.assign({}, state.dlg, { s: el.value }); render(); break;
    case 'dlg-r': state.dlg = Object.assign({}, state.dlg, { r: el.value }); render(); break;
    case 'rm-type': state.rm = Object.assign({}, state.rm, { type: el.value, err: '' }); render(); break;
  }
}

function onInput(e) {
  if (e.target.id === 'poolSearch') { state.q = e.target.value; render(); }
  else if (e.target.id === 'rmId') { state.rm = Object.assign({}, state.rm, { id: e.target.value, err: '' }); render(); }
}

/* drag & drop: во время перетаскивания подсветка наносится на готовый DOM,
   без перерисовки — иначе браузер оборвёт начатый drag исходной карточки */
function applyDragHighlights() {
  const L = state.dragId ? lOf(state.dragId) : null;
  if (!L) return;
  document.querySelectorAll('.cell').forEach(cell => {
    cell.classList.remove('cell--empty');
    const d = +cell.dataset.d, s = +cell.dataset.s;
    const stt = slotStatus(L, d, s);
    const empty = !cell.querySelector('.card');
    if (stt.kind === 'free') cell.classList.add('cell--drop-free');
    else if (stt.kind === 'soft') {
      cell.classList.add('cell--drop-soft');
      if (empty) cell.insertAdjacentHTML('beforeend', '<span class="cell-tag cell-tag--soft">◐ пожелание</span>');
    } else {
      cell.classList.add('cell--drop-hard');
      if (empty) cell.insertAdjacentHTML('beforeend', '<span class="cell-tag cell-tag--hard">⚠ конфликт</span>');
    }
  });
}

function onDragStart(e) {
  const el = e.target.closest && e.target.closest('[data-drag]');
  if (!el) return;
  state.dragId = el.dataset.drag;
  e.dataTransfer.effectAllowed = 'move';
  try { e.dataTransfer.setData('text/plain', state.dragId); } catch (_) { }
  setTimeout(() => { el.classList.add('card--drag'); applyDragHighlights(); }, 0);
}

function onDragEnd() {
  if (state.dragId != null) { state.dragId = null; render(); }
}

function onDragOver(e) {
  if (state.dragId && e.target.closest && e.target.closest('.cell')) e.preventDefault();
}

function onDrop(e) {
  const cell = e.target.closest && e.target.closest('.cell');
  if (!cell || !state.dragId) return;
  e.preventDefault();
  place(state.dragId, +cell.dataset.d, +cell.dataset.s);
}

function onKey(e) {
  const tag = (e.target.tagName || '').toLowerCase();
  const inInput = tag === 'input' || tag === 'select' || tag === 'textarea';
  if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'z') { e.preventDefault(); e.shiftKey ? doRedo() : doUndo(); return; }
  if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'y') { e.preventDefault(); doRedo(); return; }
  if (e.key === 'Escape') {
    if (state.gen && state.gen.phase !== 'run') state.gen = null;
    state.dlg = null; state.co = null; state.ex = null; state.rm = null;
    state.sel = []; state.dragId = null;
    render(); return;
  }
  if (e.key === 'Enter' && e.target.id === 'rmId') { rmAdd(); return; }
  if (inInput) return;
  if (e.key === '/') {
    e.preventDefault();
    state.tab = 'pool'; render();
    const s = $('#poolSearch'); if (s) s.focus();
    return;
  }
  if (e.key === 'PageUp') { e.preventDefault(); entStep(-1); return; }
  if (e.key === 'PageDown') { e.preventDefault(); entStep(1); return; }
  const arrows = { ArrowLeft: [-1, 0], ArrowRight: [1, 0], ArrowUp: [0, -1], ArrowDown: [0, 1] };
  if (arrows[e.key]) {
    e.preventDefault();
    const c = state.cursor || { d: 0, s: 0 };
    state.cursor = {
      d: Math.max(0, Math.min(DAYS.length - 1, c.d + arrows[e.key][0])),
      s: Math.max(0, Math.min(SLOTS - 1, c.s + arrows[e.key][1]))
    };
    render();
    const g = $('#gridScroll'); if (g) g.focus();
    return;
  }
  const cur = state.cursor;
  const cellLessons = cur ? visibleLessons().filter(l => l.d === cur.d && l.s === cur.s) : [];
  if (e.key === 'Enter') {
    e.preventDefault();
    if (state.sel.length === 1 && cur && cellLessons.length === 0) { place(state.sel[0], cur.d, cur.s); return; }
    if (cellLessons.length) openDlg(cellLessons[0].id);
    return;
  }
  if (e.key.toLowerCase() === 'p') { pinLessons(state.sel.length ? state.sel : cellLessons.map(l => l.id)); return; }
  if (e.key === 'Delete' || e.key === 'Backspace') { removeLessons(state.sel.length ? state.sel : cellLessons.map(l => l.id)); return; }
}

document.addEventListener('click', onClick);
document.addEventListener('dblclick', onDblClick);
document.addEventListener('change', onChange);
document.addEventListener('input', onInput);
document.addEventListener('dragstart', onDragStart);
document.addEventListener('dragend', onDragEnd);
document.addEventListener('dragover', onDragOver);
document.addEventListener('drop', onDrop);
document.addEventListener('keydown', onKey);

render();
