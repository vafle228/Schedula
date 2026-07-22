/**
 * UI state + behaviour of the «Расписание» module. Module-scoped so the
 * grid, pool panel and modals share it without prop drilling; survives
 * navigation between sections.
 */
import { reactive, computed } from 'vue'
import { store } from '../../store/index.js'
import { slotStatus } from '../../utils/conflicts.js'
import { ALL_DAYS, kindHours } from '../../utils/kinds.js'
import { slotBells } from '../../utils/slots.js'

export const ui = reactive({
  view: 'group', // 'group' | 'teacher' | 'room'
  ent: { group: 'ИС-31', teacher: 't1', room: '214' },
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
  dlg: null, // { id, d, s, r }
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

/* ---------- lessons ---------- */

export const enriched = store.enriched
export const analysis = store.scheduleAnalysis

export const visible = computed(() => enriched.value.filter(entMatch))

export function entMatch(l) {
  if (ui.view === 'group') return l.g === ui.ent.group
  if (ui.view === 'teacher') return l.t === ui.ent.teacher
  return l.room === ui.ent.room
}

export const placedN = computed(() => enriched.value.filter((l) => l.d != null).length)
export const totalN = computed(() => enriched.value.length)
export const problemsN = computed(() => analysis.value.hardN + analysis.value.orphanN)

/* ---------- entity navigation ---------- */

export function entList() {
  if (ui.view === 'group') return store.state.groups.map((g) => ({ v: g.id, label: g.id }))
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

/* ---------- pool ---------- */

export const entUnplaced = computed(() => enriched.value.filter((l) => l.d == null).filter(entMatch))

export const poolCards = computed(() => {
  const q = ui.q.trim().toLowerCase()
  return entUnplaced.value.filter((l) => {
    if (ui.kindF !== 'all' && l.kind !== ui.kindF) return false
    if (q) {
      const t = store.teacherById(l.t)
      const hay = (l.disc + ' ' + l.g + ' ' + (t ? t.name : '')).toLowerCase()
      if (hay.indexOf(q) < 0) return false
    }
    return true
  })
})

/* ---------- placement ---------- */

export function statusFor(L, d, s, r) {
  return slotStatus(L, d, s, r, enriched.value, store.state.teachers, cfg.value)
}

export async function place(id, d, s, room) {
  const L = enriched.value.find((l) => l.id === id)
  if (!L) return
  const slot = cfg.value.slots && cfg.value.slots[s]
  if (slot && kindHours(L.kind) > slot.hours) return // 2 ак.ч нельзя в слот на 1 ак.ч
  if (ui.view === 'group' && L.g !== ui.ent.group) ui.ent.group = L.g
  ui.dragId = null
  ui.sel = []
  await store.placeLesson(id, d, s, room)
  flash(id)
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

export function openDlg(id) {
  const L = enriched.value.find((l) => l.id === id)
  if (!L) return
  ui.dlg = {
    id,
    d: String(L.d != null ? L.d : dayIdxs.value[0] || 0),
    s: String(L.s != null ? L.s : 0),
    r: L.room,
  }
}

/** Unique «дисциплина + преподаватель» combos coming from «Распределение». */
export const asgOptions = computed(() => {
  const seen = {}
  const out = []
  store.assignedTopics(store.state.period).forEach(({ topic, discipline, teacherId }) => {
    const key = discipline.id + '|' + teacherId
    if (!seen[key]) {
      seen[key] = { discipline, teacherId, topics: [] }
      out.push(seen[key])
    }
    seen[key].topics.push(topic)
  })
  return out.map((a, i) => {
    const t = store.teacherById(a.teacherId)
    const sibling = store.state.lessons.find((l) => l.disciplineId === a.discipline.id)
    return {
      v: String(i),
      label: a.discipline.name + ', ' + a.discipline.groupId + ', ' + (t ? t.name : ''),
      discipline: a.discipline,
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
      d: String(L.d != null ? L.d : dayIdxs.value[0] || 0),
      s: String(L.s != null ? L.s : 0),
      r: L.room,
      err: '',
    }
    ui.sel = []
    return
  }
  const opts = asgOptions.value
  if (!opts.length) return
  let asg = 0
  if (ui.view === 'group') {
    const i = opts.findIndex((a) => a.discipline.groupId === ui.ent.group)
    if (i >= 0) asg = i
  }
  ui.lf = {
    id: null,
    asg: String(asg),
    kind: 'lec',
    topic: '',
    question: '',
    placed: !!pos,
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
  ui.dlg = null
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
