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
  dragGroupId: null, // group the dragged topic/discipline is being assigned for
  dragOver: null, // teacher id under the dragged item
  menu: null, // { ids, groupId, x, y, title }
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

/** Teacher assigned to teach ``topicId`` to ``groupId`` — null when unassigned. */
export function teacherOfTopic(groupId, topicId) {
  const g = store.state.assignments[groupId]
  const a = g ? g[topicId] : null
  return a ? a.teacherId : null
}

export function courseOfGroup(groupId) {
  const g = store.groupById(groupId)
  return g ? g.course : null
}

/** Assigned hours of a teacher within a period, summed over every group. */
export function hoursOf(tid, period) {
  const { topicById, discOfTopic } = topicIndex.value
  let h = 0
  const asg = store.state.assignments
  for (const gid in asg) {
    for (const topId in asg[gid]) {
      if (asg[gid][topId].teacherId !== tid) continue
      const d = discOfTopic[topId]
      if (d && d.period === period && topicById[topId]) h += topicById[topId].hours
    }
  }
  return h
}

/* ---------- pool rows ---------- */

/**
 * The pool works in (group, discipline) rows: a discipline belongs to a
 * (major, course), so it surfaces under every group of that major and course,
 * where its teachers are assigned per group.
 */
export const planRows = computed(() => {
  const period = store.state.period
  const rows = []
  store.state.groups.forEach((g) => {
    store.state.disciplines.forEach((d) => {
      if (d.period === period && d.majorId === g.majorId && d.course === g.course) {
        rows.push({ group: g, d })
      }
    })
  })
  return rows
})

export const filtered = computed(() => {
  const q = dui.search.trim().toLowerCase()
  return planRows.value.filter(({ group, d }) => {
    if (q && !(
      d.name.toLowerCase().includes(q)
      || group.name.toLowerCase().includes(q)
      || d.topics.some((tp) => tp.name.toLowerCase().includes(q))
    )) return false
    if (dui.fKind !== 'all' && !d.topics.some((tp) => tp.kind === dui.fKind)) return false
    const total = d.topics.length
    const asg = d.topics.filter((tp) => teacherOfTopic(group.id, tp.id)).length
    if (dui.fStatus === 'open' && asg >= total) return false
    if (dui.fStatus === 'done' && asg < total) return false
    if (dui.fCourse !== 'all' && group.course !== Number(dui.fCourse)) return false
    return true
  })
})

export const progress = computed(() => {
  let tot = 0
  let don = 0
  planRows.value.forEach(({ group, d }) => {
    d.topics.forEach((tp) => { tot++; if (teacherOfTopic(group.id, tp.id)) don++ })
  })
  return { tot, don }
})

/* ---------- drag payload ---------- */

export const dragTopicIds = computed(() => {
  if (dui.dragId && dui.dragKind === 'topic') return [dui.dragId]
  if (dui.dragId && dui.dragKind === 'disc' && dui.dragGroupId != null) {
    const d = store.state.disciplines.find((x) => x.id === dui.dragId)
    if (d) return d.topics.filter((tp) => !teacherOfTopic(dui.dragGroupId, tp.id)).map((tp) => tp.id)
  }
  return []
})

export const dragH = computed(() => {
  const { topicById } = topicIndex.value
  return dragTopicIds.value.reduce((h, id) => h + (topicById[id] ? topicById[id].hours : 0), 0)
})

/* ---------- assign menu ---------- */

export function openMenuAt(ids, x, y, title, groupId) {
  x = Math.max(8, Math.min(x, window.innerWidth - 315))
  y = Math.max(8, Math.min(y, window.innerHeight - 400))
  dui.menu = { ids, groupId, x, y, title }
  dui.menuSearch = ''
}

export function openMenuEv(ids, e, title, groupId) {
  const r = e.currentTarget.getBoundingClientRect()
  openMenuAt(ids, r.left, r.bottom + 6, title, groupId)
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

/**
 * Lesson-type catalogue lives in utils/kinds.js — the single source shared with
 * «Расписание». Re-exported here (as the array `KINDS`) so this module's views
 * keep their existing imports. Add new kinds in utils/kinds.js.
 */
export { KIND_LIST as KINDS, kindLabel, kindColor, kindShort, dotRadius } from '../../utils/kinds.js'
