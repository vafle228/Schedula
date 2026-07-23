/**
 * UI state + behaviour of the «Расписание» module. Module-scoped so the
 * grid, pool panel and modals share it without prop drilling; survives
 * navigation between sections.
 */
import { reactive, computed } from 'vue'
import { store } from '../../store/index.js'
import { slotStatus, isHoliday } from '../../utils/conflicts.js'
import { ALL_DAYS, kindHours } from '../../utils/kinds.js'
import { slotBells } from '../../utils/slots.js'

/** Weeks shown per page in the week pager (Расписание v8). */
export const WEEK_PAGE = 6

export const ui = reactive({
  view: 'group', // 'group' | 'teacher' | 'room'
  ent: { group: 'ИС-31', teacher: 't1', room: '214' },
  week: 1, // 1-based, current week of the semester
  weekPage: 0,
  q: '',
  kindF: 'all',
  sel: [],
  cursor: null, // { d, s }
  dragId: null,
  poolOver: false, // pool drop-zone is hovered by a placed lesson being dragged
  flashId: null,
  /* modals */
  prob: false,
  ov: false,
  gen: null, // { phase: 'prep'|'run'|'done', mode, jobId, pct, stage, live, summary, readiness }
  lf: null, // lesson form
  co: null, // { tid } — teacher availability
  rooms: false,
  ex: null, // { step, view, scope }
})

let flashTimer = null
export function flash(id) {
  ui.flashId = id
  clearTimeout(flashTimer)
  flashTimer = setTimeout(() => { ui.flashId = null }, 2500)
}

/* ---------- period config ---------- */

export const cfg = computed(() => store.state.periods[store.state.period] || { activeDays: [1, 1, 1, 1, 1, 0, 0], acadMin: 45, slots: [], slotsPerDay: 0 })
export const dayIdxs = computed(() => {
  const out = []
  cfg.value.activeDays.forEach((on, i) => { if (on) out.push(i) })
  return out
})
export const dayHeads = computed(() => dayIdxs.value.map((i) => ALL_DAYS[i]))
export const slots = computed(() => cfg.value.slots || [])
export const slotsN = computed(() => slots.value.length || cfg.value.slotsPerDay || 0)
export const bells = computed(() => slotBells(cfg.value.slots, cfg.value.acadMin || 45))

/* ---------- weeks (Расписание v8) ---------- */

export const weeksCount = computed(() => cfg.value.weeksCount || 16)

/** True when (week, day) is a holiday in the current period. */
export function isHol(w, d) {
  return isHoliday(cfg.value, w, d)
}

/** Date "dd.mm" for week (1-based) and day index, counted from period start. */
export function dateFor(w, d) {
  const base = cfg.value.startDate
  if (!base) return ''
  const dt = new Date(base + 'T00:00:00')
  dt.setDate(dt.getDate() + (w - 1) * 7 + d)
  return String(dt.getDate()).padStart(2, '0') + '.' + String(dt.getMonth() + 1).padStart(2, '0')
}

/** Pager of week buttons for the current page. */
export const weekBtns = computed(() => {
  const total = weeksCount.value
  const from = ui.weekPage * WEEK_PAGE + 1
  const to = Math.min(total, from + WEEK_PAGE - 1)
  const out = []
  for (let n = from; n <= to; n++) {
    const hol = dayIdxs.value.some((d) => isHol(n, d))
    out.push({ n, hol, on: n === ui.week })
  }
  return out
})
export const weekPagesN = computed(() => Math.ceil(weeksCount.value / WEEK_PAGE))
export const weekRangeLabel = computed(() => {
  const from = ui.weekPage * WEEK_PAGE + 1
  const to = Math.min(weeksCount.value, from + WEEK_PAGE - 1)
  return from + '–' + to + ' из ' + weeksCount.value
})

export function selectWeek(n) {
  ui.week = n
  ui.weekPage = Math.floor((n - 1) / WEEK_PAGE)
  ui.cursor = null
  ui.sel = []
}
export function weekPagePrev() { if (ui.weekPage > 0) ui.weekPage-- }
export function weekPageNext() { if (ui.weekPage < weekPagesN.value - 1) ui.weekPage++ }

/* ---------- lessons ---------- */

export const enriched = store.enriched
export const analysis = store.scheduleAnalysis

export const visible = computed(() => enriched.value.filter(entMatch))

/** Placed lessons matching the entity in the current week — what the grid draws. */
export const weekVisible = computed(() => visible.value.filter((l) => l.d != null && l.w === ui.week))

export function entMatch(l) {
  if (ui.view === 'group') return l.g === ui.ent.group
  if (ui.view === 'teacher') return (l.subBy || l.t) === ui.ent.teacher
  return l.room === ui.ent.room
}

export const placedN = computed(() => enriched.value.filter((l) => l.d != null).length)
export const totalN = computed(() => enriched.value.length)
export const problemsN = computed(() => analysis.value.hardN + analysis.value.orphanN)

/* ---------- entity navigation ---------- */

export function entList() {
  if (ui.view === 'group') return store.state.groups.map((g) => ({ v: g.name, label: g.name }))
  if (ui.view === 'teacher') return store.state.teachers.map((t) => ({ v: t.id, label: t.name }))
  return store.state.rooms.map((r) => ({ v: r.id, label: r.id + ', ' + r.type }))
}

export const entVal = computed({
  get: () => (ui.view === 'group' ? ui.ent.group : ui.view === 'teacher' ? ui.ent.teacher : ui.ent.room),
  set: (v) => { ui.ent[ui.view] = v },
})

export function entStep(dir) {
  const list = entList()
  if (!list.length) return
  const i = Math.max(0, list.findIndex((o) => o.v === entVal.value))
  entVal.value = list[(i + dir + list.length) % list.length].v
}

/** Options with a ⚠ marker when the entity has problem lessons. */
export const entOptions = computed(() => {
  const probEnt = { group: {}, teacher: {}, room: {} }
  enriched.value.forEach((l) => {
    if (analysis.value.byId[l.id]) {
      probEnt.group[l.g] = 1
      probEnt.teacher[l.t] = 1
      probEnt.room[l.room] = 1
    }
  })
  return entList().map((o) => (probEnt[ui.view][o.v] ? { v: o.v, label: o.label + '  ⚠' } : o))
})

/* ---------- placement ---------- */

export function statusFor(L, w, d, s, r) {
  return slotStatus(L, w, d, s, r, enriched.value, store.state.teachers, cfg.value)
}

export async function place(id, w, d, s, room) {
  const L = enriched.value.find((l) => l.id === id)
  if (!L) return
  const slot = cfg.value.slots && cfg.value.slots[s]
  if (slot && kindHours(L.kind) > slot.hours) return // 2 ак.ч нельзя в слот на 1 ак.ч
  if (isHol(w, d)) return // праздник — слот не принимает пару
  if (ui.view === 'group' && L.g !== ui.ent.group) ui.ent.group = L.g
  ui.dragId = null
  ui.sel = []
  await store.placeLesson(id, w, d, s, room)
  flash(id)
}

export async function setSubstitute(id, subBy) {
  await store.setSubstitute(id, subBy)
}

export async function removeLessons(ids) {
  if (!ids.length) return
  await store.unplaceLessons(ids)
  ui.sel = []
}

/** True while a *placed* lesson is being dragged — shows the pool drop-zone. */
export const dragPlaced = computed(() => {
  if (!ui.dragId) return false
  const L = enriched.value.find((l) => l.id === ui.dragId)
  return !!(L && L.d != null)
})

/** Drag a placed lesson back onto the pool → снять с сетки (Итерация 8). */
export async function unplaceToPool(id) {
  const L = enriched.value.find((l) => l.id === id)
  ui.poolOver = false
  ui.dragId = null
  if (!L || L.d == null) return
  await store.unplaceLessons([id])
}

export async function pinLessons(ids) {
  await store.togglePin(ids)
}

/* ---------- dialogs ---------- */

/** Unique «группа + дисциплина + преподаватель» combos from «Распределение». */
export const asgOptions = computed(() => {
  const seen = {}
  const out = []
  store.assignedTopics(store.state.period).forEach(({ topic, discipline, group, teacherId }) => {
    const key = group.id + '|' + discipline.id + '|' + teacherId
    if (!seen[key]) {
      seen[key] = { discipline, group, teacherId, topics: [] }
      out.push(seen[key])
    }
    seen[key].topics.push(topic)
  })
  return out.map((a, i) => {
    const t = store.teacherById(a.teacherId)
    const sibling = store.state.lessons.find(
      (l) => l.disciplineId === a.discipline.id && l.groupId === a.group.id,
    )
    return {
      v: String(i),
      label: a.discipline.name + ', ' + a.group.name + ', ' + (t ? t.name : ''),
      discipline: a.discipline,
      groupId: a.group.id,
      groupName: a.group.name,
      teacherId: a.teacherId,
      teacherName: t ? t.name : '',
      topics: a.topics,
      defaultRoom: sibling ? sibling.roomId : (store.state.rooms[0] ? store.state.rooms[0].id : ''),
    }
  })
})

export function openLf(pos, id) {
  if (id) {
    const L = enriched.value.find((l) => l.id === id)
    if (!L) return
    ui.lf = {
      id,
      asg: null,
      kind: L.kind,
      topic: L.topic || '',
      question: L.question || '',
      placed: L.d != null,
      w: String(L.w != null ? L.w : ui.week),
      d: String(L.d != null ? L.d : dayIdxs.value[0] || 0),
      s: String(L.s != null ? L.s : 0),
      r: L.room,
      teacher: L.subBy || L.t, // effective teacher; ≠ штатный ⇒ замена
      staffTeacher: L.t,
      pin: !!L.pin,
      err: '',
    }
    ui.sel = []
    return
  }
  const opts = asgOptions.value
  if (!opts.length) return
  let asg = 0
  if (ui.view === 'group') {
    const i = opts.findIndex((a) => a.groupName === ui.ent.group)
    if (i >= 0) asg = i
  }
  ui.lf = {
    id: null,
    asg: String(asg),
    kind: 'lec',
    topic: '',
    question: '',
    placed: !!pos,
    w: String(pos ? pos.w || ui.week : ui.week),
    d: String(pos ? pos.d : dayIdxs.value[0] || 0),
    s: String(pos ? pos.s : 0),
    r: opts[asg].defaultRoom,
    err: '',
  }
  ui.sel = []
  if (pos) ui.cursor = pos
}

/** Colors of the free/soft/hard status box in placement dialogs. */
export const ST_COLORS = {
  free: { color: '#1F8A5B', border: 'rgba(31,138,91,0.25)', bg: 'rgba(31,138,91,0.04)', icon: '✓' },
  soft: { color: '#B07C1F', border: 'rgba(176,124,31,0.35)', bg: 'rgba(176,124,31,0.05)', icon: '◐' },
  hard: { color: '#C24536', border: 'rgba(194,69,54,0.35)', bg: 'rgba(194,69,54,0.04)', icon: '⚠' },
  unfit: { color: '#8A857C', border: 'rgba(0,0,0,0.14)', bg: 'rgba(0,0,0,0.03)', icon: '✕' },
}

export function closeAllModals() {
  if (ui.gen && ui.gen.phase === 'run') {
    // running generation stays: cancel is explicit
  } else {
    ui.gen = null
  }
  ui.co = null
  ui.ex = null
  ui.rooms = false
  ui.lf = null
  ui.ov = false
  ui.prob = false
  ui.sel = []
  ui.dragId = null
  ui.poolOver = false
}
