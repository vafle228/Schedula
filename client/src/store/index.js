/**
 * Shared application store (Pinia-style module built on Vue reactivity).
 * Cross-module state lives here: current period, master data, the plan
 * (disciplines / topics / assignments) and lesson slots, plus per-module
 * undo/redo stacks. Every mutation goes through the API service layer.
 */
import { reactive, computed } from 'vue'
import { api } from '../api/index.js'
import { analyze } from '../utils/conflicts.js'

/** Weekly-hour cap per teacher and period used by the load indicators. */
export const NORM_HOURS = 240

const state = reactive({
  loaded: false,
  period: 'fall',
  periods: { fall: null, spring: null },
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
  state.disciplines.forEach((d) => { discName[d.id] = d.name })
  return state.lessons
    .filter((l) => l.period === state.period)
    .map((l) => ({
      id: l.id,
      g: l.groupId,
      disc: discName[l.disciplineId] || '',
      t: l.teacherId,
      room: l.roomId,
      kind: l.kind,
      d: l.day,
      s: l.slot,
      pin: l.pin,
      manual: l.manual,
      ni: l.ni,
      nt: l.nt,
      topic: l.topicLabel,
      question: l.question,
      orphan: !state.assignments[l.topicId],
    }))
})

const scheduleAnalysis = computed(() => {
  const cfg = state.periods[state.period]
  return analyze(enriched.value, state.teachers, cfg)
})

/** Assigned topics of the given period — schedule works only with these. */
function assignedTopics(period) {
  const out = []
  state.disciplines.forEach((d) => {
    if (d.period !== period) return
    d.topics.forEach((tp) => {
      const a = state.assignments[tp.id]
      if (a) out.push({ topic: tp, discipline: d, teacherId: a.teacherId })
    })
  })
  return out
}

/* ---------- data refresh helpers ---------- */

async function refreshPlan() {
  const [disciplines, assignments, lessons] = await Promise.all([
    api.getDisciplines(), api.getAssignments(), api.getLessons(),
  ])
  state.disciplines = disciplines
  state.assignments = assignments
  state.lessons = lessons
  // lesson set changed structurally — schedule snapshots are no longer valid
  state.schedUndo = []
  state.schedRedo = []
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
      calls.push(api.patchLesson(l.id, { day: l.day, slot: l.slot, roomId: l.roomId, kind: l.kind, pin: l.pin, topicLabel: l.topicLabel, question: l.question }))
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
  teacherById,
  roomById,
  groupById,
  disciplineById,
  lessonById,
  topicById,
  assignedTopics,

  async init() {
    if (state.loaded) return
    const [periods, majors, groups, teachers, rooms, disciplines, assignments, lessons] = await Promise.all([
      api.getPeriods(), api.getMajors(), api.getGroups(), api.getTeachers(),
      api.getRooms(), api.getDisciplines(), api.getAssignments(), api.getLessons(),
    ])
    periods.forEach((p) => { state.periods[p.id] = p })
    state.majors = majors
    state.groups = groups
    state.teachers = teachers
    state.rooms = rooms
    state.disciplines = disciplines
    state.assignments = assignments
    state.lessons = lessons
    state.loaded = true
  },

  setPeriod(p) { state.period = p },

  /* ===== Распределение: назначения с undo/redo ===== */

  async commitAssign(entries) {
    const eff = entries
      .map((e) => ({
        topicId: e.topicId,
        prev: state.assignments[e.topicId] ? state.assignments[e.topicId].teacherId : null,
        to: e.to,
      }))
      .filter((e) => e.prev !== e.to)
    if (!eff.length) return
    await api.batchAssign(eff.map((e) => ({ topicId: e.topicId, teacherId: e.to })))
    state.planUndo = [...state.planUndo, eff]
    state.planRedo = []
    await refreshPlan()
  },

  async planUndoAct() {
    const e = state.planUndo[state.planUndo.length - 1]
    if (!e) return
    await api.batchAssign(e.map((x) => ({ topicId: x.topicId, teacherId: x.prev })))
    state.planUndo = state.planUndo.slice(0, -1)
    state.planRedo = [...state.planRedo, e]
    await refreshPlan()
  },

  async planRedoAct() {
    const e = state.planRedo[state.planRedo.length - 1]
    if (!e) return
    await api.batchAssign(e.map((x) => ({ topicId: x.topicId, teacherId: x.to })))
    state.planRedo = state.planRedo.slice(0, -1)
    state.planUndo = [...state.planUndo, e]
    await refreshPlan()
  },

  /* ===== Распределение: дисциплины и темы ===== */

  async createDiscipline(payload) {
    const d = await api.createDiscipline(payload)
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

  /* ===== Расписание: занятия ===== */

  async placeLesson(id, day, slot, roomId) {
    schedSnapshot()
    const body = { day, slot }
    if (roomId) body.roomId = roomId
    const l = await api.patchLesson(id, body)
    upsertLesson(l)
    state.newIds = []
  },

  async unplaceLessons(ids) {
    if (!ids.length) return
    schedSnapshot()
    const res = await Promise.all(ids.map((id) => api.patchLesson(id, { day: null, slot: null, pin: false })))
    res.forEach(upsertLesson)
  },

  async togglePin(ids) {
    const targets = ids.map(lessonById).filter((l) => l && l.day != null)
    if (!targets.length) return
    schedSnapshot()
    const res = await Promise.all(targets.map((l) => (l.pin ? api.unpinLesson(l.id) : api.pinLesson(l.id))))
    res.forEach(upsertLesson)
  },

  async updateLesson(id, fields) {
    schedSnapshot()
    const l = await api.patchLesson(id, fields)
    upsertLesson(l)
  },

  async createManualLesson(payload) {
    schedSnapshot()
    const l = await api.createLesson({ ...payload, manual: true })
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
    state.lessons = await api.getLessons()
    state.newIds = newIds
  },

  /* ===== Справочники ===== */

  async createTeacher(body) {
    const t = await api.createTeacher(body)
    state.teachers.push(t)
    return t
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
    const g = await api.createGroup(majorId, body)
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
      api.patchPeriod('fall', fall),
      api.patchPeriod('spring', spring),
    ])
    state.periods.fall = f
    state.periods.spring = s
  },
}
