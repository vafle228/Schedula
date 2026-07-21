/**
 * UI state + behaviour of the «Распределение» module.
 */
import { reactive, computed } from 'vue'
import { store, NORM_HOURS } from '../../store/index.js'

export const dui = reactive({
  search: '',
  tSearch: '',
  fStatus: 'all', // all | open | done
  fKind: 'all', // all | lec | prac
  fCourse: 'all', // all | 1..4
  expDisc: {},
  expTeacher: {},
  dragKind: null, // 'topic' | 'disc'
  dragId: null,
  dragOver: null, // teacher id under the dragged item
  menu: null, // { ids, x, y, title }
  menuSearch: '',
  leftW: 560,
  ov: false,
  exp: null, // { step: 'config'|'gen'|'done', period, fileName }
  cd: null, // create-discipline form
  addTopic: null, // { discId, kind, name, hours }
})

export const norm = NORM_HOURS

/* ---------- indexes ---------- */

export const topicIndex = computed(() => {
  const topicById = {}
  const discOfTopic = {}
  store.state.disciplines.forEach((d) => {
    d.topics.forEach((tp) => { topicById[tp.id] = tp; discOfTopic[tp.id] = d })
  })
  return { topicById, discOfTopic }
})

export function teacherOfTopic(topicId) {
  const a = store.state.assignments[topicId]
  return a ? a.teacherId : null
}

export function courseOfGroup(groupId) {
  const g = store.groupById(groupId)
  return g ? g.course : null
}

/** Assigned hours of a teacher within a period. */
export function hoursOf(tid, period) {
  const { topicById, discOfTopic } = topicIndex.value
  let h = 0
  for (const topId in store.state.assignments) {
    if (store.state.assignments[topId].teacherId !== tid) continue
    const d = discOfTopic[topId]
    if (d && d.period === period && topicById[topId]) h += topicById[topId].hours
  }
  return h
}

/* ---------- pool filtering ---------- */

export const filtered = computed(() => {
  const q = dui.search.trim().toLowerCase()
  const period = store.state.period
  return store.state.disciplines.filter((d) => {
    if (d.period !== period) return false
    if (q && !(
      d.name.toLowerCase().includes(q)
      || d.groupId.toLowerCase().includes(q)
      || d.topics.some((tp) => tp.name.toLowerCase().includes(q))
    )) return false
    if (dui.fKind !== 'all' && !d.topics.some((tp) => tp.kind === dui.fKind)) return false
    const total = d.topics.length
    const asg = d.topics.filter((tp) => teacherOfTopic(tp.id)).length
    if (dui.fStatus === 'open' && asg >= total) return false
    if (dui.fStatus === 'done' && asg < total) return false
    if (dui.fCourse !== 'all' && courseOfGroup(d.groupId) !== Number(dui.fCourse)) return false
    return true
  })
})

export const progress = computed(() => {
  let tot = 0
  let don = 0
  store.state.disciplines
    .filter((d) => d.period === store.state.period)
    .forEach((d) => d.topics.forEach((tp) => { tot++; if (teacherOfTopic(tp.id)) don++ }))
  return { tot, don }
})

/* ---------- drag payload ---------- */

export const dragTopicIds = computed(() => {
  if (dui.dragId && dui.dragKind === 'topic') return [dui.dragId]
  if (dui.dragId && dui.dragKind === 'disc') {
    const d = store.state.disciplines.find((x) => x.id === dui.dragId)
    if (d) return d.topics.filter((tp) => !teacherOfTopic(tp.id)).map((tp) => tp.id)
  }
  return []
})

export const dragH = computed(() => {
  const { topicById } = topicIndex.value
  return dragTopicIds.value.reduce((h, id) => h + (topicById[id] ? topicById[id].hours : 0), 0)
})

/* ---------- assign menu ---------- */

export function openMenuAt(ids, x, y, title) {
  x = Math.max(8, Math.min(x, window.innerWidth - 315))
  y = Math.max(8, Math.min(y, window.innerHeight - 400))
  dui.menu = { ids, x, y, title }
  dui.menuSearch = ''
}

export function openMenuEv(ids, e, title) {
  const r = e.currentTarget.getBoundingClientRect()
  openMenuAt(ids, r.left, r.bottom + 6, title)
}

/* ---------- actions ---------- */

export function commitAssign(entries) {
  return store.commitAssign(entries)
}

export function resetFilters() {
  dui.search = ''
  dui.fStatus = 'all'
  dui.fKind = 'all'
  dui.fCourse = 'all'
}

/* ---------- lesson kinds ---------- */

/** Catalogue of lesson types. Add rows here to offer more kinds everywhere. */
export const KINDS = [
  { k: 'lec', label: 'Лекция', short: 'Лек.', color: '#3B62C4', radius: '50%' },
  { k: 'prac', label: 'Практика', short: 'Практ.', color: '#1F8A5B', radius: '2px' },
  { k: 'lab', label: 'Лабораторная', short: 'Лаб.', color: '#B45309', radius: '2px' },
  { k: 'sem', label: 'Семинар', short: 'Сем.', color: '#8A3FFC', radius: '50%' },
  { k: 'consult', label: 'Консультация', short: 'Конс.', color: '#0E7490', radius: '3px' },
  { k: 'exam', label: 'Экзамен', short: 'Экз.', color: '#C0392B', radius: '3px' },
  { k: 'course', label: 'Курсовая', short: 'Курс.', color: '#7A756C', radius: '3px' },
]

const KIND_MAP = Object.fromEntries(KINDS.map((x) => [x.k, x]))
const kindOf = (k) => KIND_MAP[k] || KINDS[0]

export const kindLabel = (k) => kindOf(k).label
export const kindColor = (k) => kindOf(k).color
export const kindShort = (k) => kindOf(k).short
export const dotRadius = (k) => kindOf(k).radius
