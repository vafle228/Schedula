/**
 * Shared application store (Pinia-style module built on Vue reactivity).
 * Cross-module state lives here: current period, master data, the plan
 * (disciplines / topics / assignments) and lesson slots, plus per-module
 * undo/redo stacks. Every mutation goes through the API service layer.
 */
import { reactive, computed } from 'vue'
import { api } from '../api/index.js'
import { analyze } from '../utils/conflicts.js'
import { applyTopicTypes, kindHours } from '../utils/kinds.js'

/** Weekly-hour cap per teacher and period used by the load indicators. */
export const NORM_HOURS = 240

const state = reactive({
  loaded: false,
  period: 'fall',
  periods: { fall: null, spring: null },
  years: [],
  // the academic year the whole app is currently scoped to (defaults to active)
  yearId: null,
  topicTypes: [],
  majors: [],
  groups: [],
  teachers: [],
  rooms: [],
  disciplines: [],
  assignments: {},
  lessons: [],
  /* undo/redo: Распределение works in assignment ops, Расписание in snapshots */
  planUndo: [],
  planRedo: [],
  schedUndo: [],
  schedRedo: [],
  /* lessons freshly added by the generator / placed — highlighted in the grid */
  newIds: [],
})

/* ---------- lookups ---------- */

const teacherById = (id) => state.teachers.find((t) => t.id === id)
const roomById = (id) => state.rooms.find((r) => r.id === id)
const groupById = (id) => state.groups.find((g) => g.id === id)
/** Display name of a group by its (integer) id — '' when unknown. */
const groupName = (id) => { const g = groupById(id); return g ? g.name : '' }
const disciplineById = (id) => state.disciplines.find((d) => d.id === id)
const lessonById = (id) => state.lessons.find((l) => l.id === id)

function topicById(id) {
  for (const d of state.disciplines) {
    const tp = d.topics.find((x) => x.id === id)
    if (tp) return { topic: tp, discipline: d }
  }
  return null
}

/* ---------- computed: schedule ---------- */

/** Lessons of the current period enriched for the grid / conflict engine. */
const enriched = computed(() => {
  const discName = {}
  const topicName = {}
  state.disciplines.forEach((d) => {
    discName[d.id] = d.name
    d.topics.forEach((tp) => { topicName[tp.id] = tp.name })
  })
  return state.lessons
    .filter((l) => l.period === state.period)
    .map((l) => ({
      id: l.id,
      g: groupName(l.groupId),
      groupId: l.groupId,
      disc: discName[l.disciplineId] || '',
      disciplineId: l.disciplineId,
      topicId: l.topicId,
      t: l.teacherId,
      room: l.roomId,
      kind: l.kind,
      w: l.week,
      d: l.day,
      s: l.slot,
      subBy: l.subBy || null,
      manual: l.manual,
      ni: l.ni,
      nt: l.nt,
      // Auto lessons start with a blank label — fall back to the plan topic's
      // name so the schedule reads sensibly without hand-editing every card.
      topic: l.topicLabel || topicName[l.topicId] || '',
      question: l.question,
      number: l.number ?? null,
      orphan: !(state.assignments[l.groupId] && state.assignments[l.groupId][l.topicId]),
    }))
})

const scheduleAnalysis = computed(() => {
  const cfg = state.periods[state.period]
  return analyze(enriched.value, state.teachers, cfg)
})

/** Display name of the academic year the app is currently scoped to. */
const yearName = computed(() => {
  const y = state.years.find((x) => x.id === state.yearId)
  return y ? y.name : '—'
})

/**
 * Assigned (group, topic) pairs of the given period — schedule works only with
 * these. A discipline's plan is shared by every group of its major and course,
 * but the teacher is chosen per group, so each pair is listed on its own.
 */
function assignedTopics(period) {
  const out = []
  state.groups.forEach((g) => {
    const gasg = state.assignments[g.id]
    if (!gasg) return
    state.disciplines.forEach((d) => {
      if (d.period !== period || d.majorId !== g.majorId || d.course !== g.course) return
      d.topics.forEach((tp) => {
        const a = gasg[tp.id]
        if (a) out.push({ topic: tp, discipline: d, group: g, teacherId: a.teacherId })
      })
    })
  })
  return out
}

/* ---------- plan accounting (lesson cap) ---------- */

/**
 * Planned lesson count for a topic — its total hours divided by the length of
 * one lesson of that type. A topic of 4 ч with 2-ак.ч lessons plans 2 lessons.
 */
function topicPlanCount(topicId) {
  const found = topicById(topicId)
  if (!found) return 0
  const per = kindHours(found.topic.kind) || 2
  return Math.max(1, Math.ceil(found.topic.hours / per))
}

/** Lessons already authored for a (group, topic) pair in the current period. */
function authoredCount(groupId, topicId) {
  return state.lessons.filter(
    (l) => l.groupId === groupId && l.topicId === topicId && l.period === state.period,
  ).length
}

/** How many more lessons the plan still allows for the (group, topic) pair. */
function planRemaining(groupId, topicId) {
  if (topicId == null || groupId == null) return Infinity
  return Math.max(0, topicPlanCount(topicId) - authoredCount(groupId, topicId))
}

/* ---------- data refresh helpers ---------- */

async function refreshPlan() {
  const [disciplines, assignments, lessons] = await Promise.all([
    api.getDisciplines(state.yearId), api.getAssignments(state.yearId), api.getLessons(state.yearId),
  ])
  state.disciplines = disciplines
  state.assignments = assignments
  state.lessons = lessons
  // lesson set changed structurally — schedule snapshots are no longer valid
  state.schedUndo = []
  state.schedRedo = []
}

/** Load every year-scoped slice (settings + plan + lessons) for state.yearId. */
async function loadYearData() {
  const [settings, groups, disciplines, assignments, lessons] = await Promise.all([
    api.getSettings(state.yearId), api.getGroups(state.yearId), api.getDisciplines(state.yearId),
    api.getAssignments(state.yearId), api.getLessons(state.yearId),
  ])
  state.periods = { fall: null, spring: null }
  settings.forEach((s) => { state.periods[s.id] = s })
  state.groups = groups
  state.disciplines = disciplines
  state.assignments = assignments
  state.lessons = lessons
  state.planUndo = []
  state.planRedo = []
  state.schedUndo = []
  state.schedRedo = []
  state.newIds = []
}

function upsertLesson(l) {
  const i = state.lessons.findIndex((x) => x.id === l.id)
  if (i >= 0) state.lessons[i] = l
  else state.lessons.push(l)
}

/* ---------- schedule undo (snapshots, replayed through the API) ---------- */

function schedSnapshot() {
  state.schedUndo = [...state.schedUndo.slice(-49), JSON.stringify(state.lessons)]
  state.schedRedo = []
  state.newIds = []
}

async function applyLessonsTarget(target) {
  const curById = {}
  state.lessons.forEach((l) => { curById[l.id] = l })
  const tgtById = {}
  target.forEach((l) => { tgtById[l.id] = l })
  const calls = []
  for (const id in curById) {
    if (!tgtById[id]) calls.push(api.deleteLesson(id))
  }
  for (const l of target) {
    const cur = curById[l.id]
    if (!cur) calls.push(api.createLesson({ ...l, manual: !!l.manual }))
    else if (JSON.stringify(cur) !== JSON.stringify(l)) {
      calls.push(api.patchLesson(l.id, { day: l.day, slot: l.slot, roomId: l.roomId, kind: l.kind, topicLabel: l.topicLabel, question: l.question }))
    }
  }
  await Promise.all(calls)
  state.lessons = target
}

/* ---------- store ---------- */

export const store = {
  state,
  enriched,
  scheduleAnalysis,
  yearName,
  teacherById,
  roomById,
  groupById,
  groupName,
  disciplineById,
  lessonById,
  topicById,
  assignedTopics,
  topicPlanCount,
  authoredCount,
  planRemaining,

  async init() {
    if (state.loaded) return
    // master data (global) first — then pick the active year and load its slice
    const [years, topicTypes, majors, teachers, rooms] = await Promise.all([
      api.getYears(), api.getTopicTypes(), api.getMajors(), api.getTeachers(), api.getRooms(),
    ])
    state.years = years
    state.topicTypes = topicTypes
    applyTopicTypes(topicTypes)
    state.majors = majors
    state.teachers = teachers
    state.rooms = rooms
    const active = years.find((y) => y.status === 'active') || years[0]
    state.yearId = active ? active.id : null
    if (state.yearId != null) await loadYearData()
    state.loaded = true
  },

  /** Switch the working academic year and re-scope the whole app to it. */
  async setWorkingYear(id) {
    if (id == null || state.yearId === id) return
    state.yearId = id
    state.period = 'fall'
    await loadYearData()
  },

  setPeriod(p) {
    if (state.period === p) return
    state.period = p
    // per-season undo — schedule snapshots do not carry across seasons
    state.schedUndo = []
    state.schedRedo = []
    state.newIds = []
  },

  /* ===== Настройки: учебные годы ===== */

  async activateYear(id) {
    const y = state.years.find((x) => x.id === id)
    if (!y || y.status === 'active') return
    state.years = await api.activateYear(id)
    // activating a year makes it the working scope
    await store.setWorkingYear(id)
  },
  async createYear(body) {
    const y = await api.createYear(body)
    state.years.push(y)
    return y
  },
  async deleteYear(id) {
    state.years = await api.deleteYear(id)
    // if the working year was removed, fall back to the active one
    if (!state.years.some((y) => y.id === state.yearId)) {
      const active = state.years.find((y) => y.status === 'active') || state.years[0]
      state.yearId = active ? active.id : null
      if (state.yearId != null) await loadYearData()
    }
  },
  /** Copy the chosen source-year disciplines into the given (draft) year. */
  async rolloverYear(targetYearId, sourceYearId, disciplineIds) {
    await api.rolloverYear(targetYearId, { sourceYearId, disciplineIds })
    // only the in-scope year is held in memory — refresh it if it was the target
    if (targetYearId === state.yearId) await loadYearData()
  },

  /* ===== Настройки: типы занятий ===== */

  async reloadTopicTypes() {
    state.topicTypes = await api.getTopicTypes()
    applyTopicTypes(state.topicTypes)
  },
  async createTopicType(body) {
    const t = await api.createTopicType(body)
    await store.reloadTopicTypes()
    return t
  },
  async patchTopicType(k, body) {
    await api.patchTopicType(k, body)
    await store.reloadTopicTypes()
  },
  async deleteTopicType(k) {
    await api.deleteTopicType(k)
    await store.reloadTopicTypes()
  },

  /* ===== Распределение: назначения с undo/redo ===== */

  async commitAssign(entries) {
    const eff = entries
      .map((e) => {
        const g = state.assignments[e.groupId]
        return {
          groupId: e.groupId,
          topicId: e.topicId,
          prev: g && g[e.topicId] ? g[e.topicId].teacherId : null,
          to: e.to,
        }
      })
      .filter((e) => e.prev !== e.to)
    if (!eff.length) return
    await api.batchAssign(state.yearId, eff.map((e) => ({ groupId: e.groupId, topicId: e.topicId, teacherId: e.to })))
    state.planUndo = [...state.planUndo, eff]
    state.planRedo = []
    await refreshPlan()
  },

  async planUndoAct() {
    const e = state.planUndo[state.planUndo.length - 1]
    if (!e) return
    await api.batchAssign(state.yearId, e.map((x) => ({ groupId: x.groupId, topicId: x.topicId, teacherId: x.prev })))
    state.planUndo = state.planUndo.slice(0, -1)
    state.planRedo = [...state.planRedo, e]
    await refreshPlan()
  },

  async planRedoAct() {
    const e = state.planRedo[state.planRedo.length - 1]
    if (!e) return
    await api.batchAssign(state.yearId, e.map((x) => ({ groupId: x.groupId, topicId: x.topicId, teacherId: x.to })))
    state.planRedo = state.planRedo.slice(0, -1)
    state.planUndo = [...state.planUndo, e]
    await refreshPlan()
  },

  /* ===== Распределение: дисциплины и темы ===== */

  async createDiscipline(payload) {
    const d = await api.createDiscipline({ ...payload, yearId: state.yearId })
    await refreshPlan()
    return d
  },

  async addTopic(disciplineId, topic) {
    await api.createTopic(disciplineId, topic)
    await refreshPlan()
  },

  async removeTopic(topicId) {
    await api.deleteTopic(topicId)
    await refreshPlan()
  },

  async removeDiscipline(disciplineId) {
    await api.deleteDiscipline(disciplineId)
    await refreshPlan()
  },

  /* ===== Расписание: занятия ===== */

  async placeLesson(id, week, day, slot, roomId) {
    schedSnapshot()
    const body = { week, day, slot }
    if (roomId) body.roomId = roomId
    const l = await api.patchLesson(id, body)
    upsertLesson(l)
    state.newIds = []
  },

  async unplaceLessons(ids) {
    if (!ids.length) return
    schedSnapshot()
    const res = await Promise.all(ids.map((id) => api.patchLesson(id, { week: null, day: null, slot: null, subBy: null })))
    res.forEach(upsertLesson)
  },

  /** Set (or clear with null) the substitute teacher of a placed occurrence. */
  async setSubstitute(id, subBy) {
    schedSnapshot()
    const l = await api.patchLesson(id, { subBy: subBy || null })
    upsertLesson(l)
  },

  async updateLesson(id, fields) {
    schedSnapshot()
    const l = await api.patchLesson(id, fields)
    upsertLesson(l)
  },

  async createManualLesson(payload) {
    // Guard the plan cap even if a caller skips the UI pre-check.
    if (planRemaining(payload.groupId, payload.topicId) <= 0) {
      throw new Error('План по этой теме исчерпан')
    }
    schedSnapshot()
    const l = await api.createLesson({ ...payload, yearId: state.yearId, manual: true })
    state.lessons.push(l)
    return l
  },

  async deleteLesson(id) {
    schedSnapshot()
    await api.deleteLesson(id)
    state.lessons = state.lessons.filter((l) => l.id !== id)
  },

  async schedUndoAct() {
    if (!state.schedUndo.length) return
    const prev = state.schedUndo[state.schedUndo.length - 1]
    const cur = JSON.stringify(state.lessons)
    state.schedUndo = state.schedUndo.slice(0, -1)
    state.schedRedo = [...state.schedRedo, cur]
    state.newIds = []
    await applyLessonsTarget(JSON.parse(prev))
  },

  async schedRedoAct() {
    if (!state.schedRedo.length) return
    const next = state.schedRedo[state.schedRedo.length - 1]
    const cur = JSON.stringify(state.lessons)
    state.schedRedo = state.schedRedo.slice(0, -1)
    state.schedUndo = [...state.schedUndo, cur]
    state.newIds = []
    await applyLessonsTarget(JSON.parse(next))
  },

  /** Accept a finished generation job: one undo step for the whole result. */
  async acceptGeneration(jobId) {
    schedSnapshot()
    const { newIds } = await api.acceptGeneration(jobId)
    state.lessons = await api.getLessons(state.yearId)
    state.newIds = newIds
  },

  /* ===== Справочники ===== */

  async createTeacher(body) {
    const t = await api.createTeacher(body)
    state.teachers.push(t)
    return t
  },
  async deleteTeacher(id) {
    await api.deleteTeacher(id)
    state.teachers = state.teachers.filter((x) => x.id !== id)
  },
  async setTeacherPhoto(id, dataUrl) {
    const t = dataUrl ? await api.putTeacherPhoto(id, dataUrl) : await api.deleteTeacherPhoto(id)
    const i = state.teachers.findIndex((x) => x.id === id)
    if (i >= 0) state.teachers[i] = t
  },
  async setTeacherConstraints(id, c) {
    const t = await api.putTeacherConstraints(id, c)
    const i = state.teachers.findIndex((x) => x.id === id)
    if (i >= 0) state.teachers[i] = t
  },
  async addAbsence(teacherId, body) {
    const a = await api.createAbsence(teacherId, body)
    const t = teacherById(teacherId)
    if (t) t.absences.push(a)
  },
  async patchAbsence(teacherId, id, body) {
    await api.patchAbsence(id, body)
    const t = teacherById(teacherId)
    if (t) {
      const a = t.absences.find((x) => x.id === id)
      if (a) Object.assign(a, body)
    }
  },
  async removeAbsence(teacherId, id) {
    await api.deleteAbsence(id)
    const t = teacherById(teacherId)
    if (t) t.absences = t.absences.filter((x) => x.id !== id)
  },

  async createMajor(body) {
    const m = await api.createMajor(body)
    state.majors.push(m)
    return m
  },
  async patchMajor(id, body) {
    await api.patchMajor(id, body)
    const m = state.majors.find((x) => x.id === id)
    if (m) Object.assign(m, body)
  },
  async deleteMajor(id) {
    await api.deleteMajor(id)
    state.majors = state.majors.filter((x) => x.id !== id)
  },
  async createGroup(majorId, body) {
    const g = await api.createGroup(majorId, { ...body, yearId: state.yearId })
    state.groups.push(g)
    return g
  },
  async patchGroup(id, body) {
    await api.patchGroup(id, body)
    const g = groupById(id)
    if (g) Object.assign(g, body)
  },
  async deleteGroup(id) {
    await api.deleteGroup(id)
    state.groups = state.groups.filter((x) => x.id !== id)
  },

  async createRoom(body) {
    const r = await api.createRoom(body)
    state.rooms.push(r)
    return r
  },
  async deleteRoom(id) {
    await api.deleteRoom(id)
    state.rooms = state.rooms.filter((x) => x.id !== id)
  },

  /* ===== Настройки ===== */

  async savePeriods(fall, spring) {
    const [f, s] = await Promise.all([
      api.patchSettings(state.yearId, 'fall', fall),
      api.patchSettings(state.yearId, 'spring', spring),
    ])
    state.periods.fall = f
    state.periods.spring = s
  },

  /** Save the grid of one season of the working year (Настройки). */
  async savePeriod(id, body) {
    const p = await api.patchSettings(state.yearId, id, body)
    state.periods[id] = p
    return p
  },
}
