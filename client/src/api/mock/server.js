/**
 * In-memory mock of the REST API from «API — Спецификация ендпоинтов».
 * Same routes, methods and payload shapes — swap `request` in ../client.js
 * for a real fetch once the backend exists.
 */
import { buildSeed } from './seed.js'
import { syncLessonsForTopic, pairsPerWeek, enrichDbLessons } from './sync.js'
import { computeGeneration } from '../../utils/generator.js'
import { analyze } from '../../utils/conflicts.js'

const db = buildSeed()
db.jobs = {}
db.exports = {}
let jobN = 0
let exportN = 0
let absN = 100

export class ApiError extends Error {
  constructor(status, message) {
    super(message)
    this.status = status
  }
}

const clone = (x) => JSON.parse(JSON.stringify(x))

function findTopic(topicId) {
  for (const d of db.disciplines) {
    const tp = d.topics.find((x) => x.id === topicId)
    if (tp) return { topic: tp, discipline: d }
  }
  return null
}

function setAssignment(topicId, teacherId) {
  const found = findTopic(topicId)
  if (!found) throw new ApiError(404, 'Тема не найдена')
  if (teacherId == null) {
    delete db.assignments[topicId]
  } else {
    if (!db.teachers.some((t) => t.id === teacherId)) throw new ApiError(404, 'Преподаватель не найден')
    db.assignments[topicId] = {
      teacherId,
      pairsPerWeek: pairsPerWeek(found.topic, db.periods[found.discipline.period]),
    }
  }
  syncLessonsForTopic(db, topicId)
}

/* ---------------- route table ---------------- */

const routes = []
function on(method, pattern, handler) {
  const keys = []
  const re = new RegExp('^' + pattern.replace(/:[^/]+/g, (m) => { keys.push(m.slice(1)); return '([^/]+)' }) + '$')
  routes.push({ method, re, keys, handler })
}

/* ----- periods (Настройки) ----- */
on('GET', '/periods', () => [db.periods.fall, db.periods.spring])
on('GET', '/periods/:id', (p) => {
  const per = db.periods[p.id]
  if (!per) throw new ApiError(404, 'Период не найден')
  return per
})
on('PATCH', '/periods/:id', (p, q, body) => {
  const per = db.periods[p.id]
  if (!per) throw new ApiError(404, 'Период не найден')
  Object.assign(per, body)
  if (body.slots) per.slotsPerDay = body.slots.length
  return per
})

/* ----- semesters (Настройки) ----- */
on('GET', '/semesters', () => db.semesters)
on('POST', '/semesters', (p, q, body) => {
  const s = {
    id: 'sem' + Date.now(),
    name: body.name,
    from: body.from,
    to: body.to,
    status: 'draft',
    current: false,
  }
  db.semesters.push(s)
  return s
})
on('POST', '/semesters/:id/activate', (p) => {
  const target = db.semesters.find((s) => s.id === p.id)
  if (!target) throw new ApiError(404, 'Семестр не найден')
  // only current-year seasons ('fall'/'spring') carry real data
  if (target.id === 'fall' || target.id === 'spring') {
    db.semesters.forEach((s) => {
      if (s.current) s.status = s.id === target.id ? 'active' : 'draft'
    })
  }
  return db.semesters
})

/* ----- topic types (Справочник «Типы занятий») ----- */
on('GET', '/topic-types', () => db.topicTypes.map((t) => ({
  ...t,
  used: db.disciplines.reduce((n, d) => n + d.topics.filter((tp) => tp.kind === t.k).length, 0),
})))
on('POST', '/topic-types', (p, q, body) => {
  const base = (body.label || 'тип').toLowerCase().replace(/[^a-zа-я0-9]+/gi, '').slice(0, 6) || 'type'
  let k = base
  let i = 1
  while (db.topicTypes.some((t) => t.k === k)) k = base + (++i)
  const t = {
    k,
    label: body.label,
    short: body.short || (body.label || '').slice(0, 4) + '.',
    color: body.color,
    acHours: body.acHours || 2,
  }
  db.topicTypes.push(t)
  return t
})
on('PATCH', '/topic-types/:k', (p, q, body) => {
  const t = db.topicTypes.find((x) => x.k === p.k)
  if (!t) throw new ApiError(404, 'Тип занятия не найден')
  Object.assign(t, body)
  return t
})
on('DELETE', '/topic-types/:k', (p) => {
  const used = db.disciplines.some((d) => d.topics.some((tp) => tp.kind === p.k))
  if (used) throw new ApiError(409, 'Тип используется в темах')
  db.topicTypes = db.topicTypes.filter((x) => x.k !== p.k)
  return null
})

/* ----- majors / groups (Справочники) ----- */
on('GET', '/majors', () => db.majors.map((m) => ({ ...m, groupsCount: db.groups.filter((g) => g.majorId === m.id).length })))
on('POST', '/majors', (p, q, body) => {
  const m = { id: 'nm' + Date.now(), code: body.code, name: body.name }
  db.majors.push(m)
  return m
})
on('PATCH', '/majors/:id', (p, q, body) => {
  const m = db.majors.find((x) => x.id === p.id)
  if (!m) throw new ApiError(404, 'Специальность не найдена')
  Object.assign(m, body)
  return m
})
on('DELETE', '/majors/:id', (p) => {
  if (db.groups.some((g) => g.majorId === p.id)) throw new ApiError(409, 'У специальности есть группы')
  db.majors = db.majors.filter((x) => x.id !== p.id)
  return null
})
on('GET', '/groups', () => db.groups)
on('GET', '/majors/:id/groups', (p) => db.groups.filter((g) => g.majorId === p.id))
on('POST', '/majors/:id/groups', (p, q, body) => {
  if (!db.majors.some((m) => m.id === p.id)) throw new ApiError(404, 'Специальность не найдена')
  if (db.groups.some((g) => g.id.toLowerCase() === body.name.toLowerCase())) throw new ApiError(409, 'Имя группы занято')
  const g = { id: body.name, majorId: p.id, course: body.course }
  db.groups.push(g)
  return g
})
on('PATCH', '/groups/:id', (p, q, body) => {
  const g = db.groups.find((x) => x.id === p.id)
  if (!g) throw new ApiError(404, 'Группа не найдена')
  if (body.course != null) g.course = body.course
  if (body.majorId != null) g.majorId = body.majorId
  return g
})
on('DELETE', '/groups/:id', (p) => {
  if (db.disciplines.some((d) => d.groupId === p.id) || db.lessons.some((l) => l.groupId === p.id)) {
    throw new ApiError(409, 'У группы есть дисциплины или занятия')
  }
  db.groups = db.groups.filter((x) => x.id !== p.id)
  return null
})

/* ----- disciplines / topics (Распределение) ----- */
on('GET', '/disciplines', () => db.disciplines)
on('POST', '/disciplines', (p, q, body) => {
  db.counters.d++
  const d = {
    id: 'd' + db.counters.d, name: body.name, groupId: body.groupId,
    period: body.period, isNew: true,
    topics: (body.topics || []).map((t) => {
      db.counters.tp++
      return { id: 'tp' + db.counters.tp, kind: t.kind, name: t.name, hours: t.hours }
    }),
  }
  db.disciplines.unshift(d)
  return d
})
on('PATCH', '/disciplines/:id', (p, q, body) => {
  const d = db.disciplines.find((x) => x.id === p.id)
  if (!d) throw new ApiError(404, 'Дисциплина не найдена')
  Object.assign(d, body)
  return d
})
on('DELETE', '/disciplines/:id', (p) => {
  const d = db.disciplines.find((x) => x.id === p.id)
  if (!d) throw new ApiError(404, 'Дисциплина не найдена')
  d.topics.forEach((tp) => {
    delete db.assignments[tp.id]
    db.lessons = db.lessons.filter((l) => l.topicId !== tp.id)
  })
  db.disciplines = db.disciplines.filter((x) => x.id !== p.id)
  return null
})
on('POST', '/disciplines/:id/topics', (p, q, body) => {
  const d = db.disciplines.find((x) => x.id === p.id)
  if (!d) throw new ApiError(404, 'Дисциплина не найдена')
  db.counters.tp++
  const tp = { id: 'tp' + db.counters.tp, kind: body.kind, name: body.name, hours: body.hours }
  d.topics.push(tp)
  return tp
})
on('PATCH', '/topics/:id', (p, q, body) => {
  const found = findTopic(p.id)
  if (!found) throw new ApiError(404, 'Тема не найдена')
  Object.assign(found.topic, body)
  if (db.assignments[p.id]) syncLessonsForTopic(db, p.id)
  return found.topic
})
on('DELETE', '/topics/:id', (p) => {
  const found = findTopic(p.id)
  if (!found) throw new ApiError(404, 'Тема не найдена')
  delete db.assignments[p.id]
  db.lessons = db.lessons.filter((l) => l.topicId !== p.id)
  found.discipline.topics = found.discipline.topics.filter((t) => t.id !== p.id)
  return null
})

/* ----- assignments ----- */
on('GET', '/assignments', () => db.assignments)
on('PUT', '/topics/:id/assignment', (p, q, body) => {
  setAssignment(p.id, body.teacherId)
  return db.assignments[p.id]
})
on('DELETE', '/topics/:id/assignment', (p) => {
  setAssignment(p.id, null)
  return null
})
on('POST', '/disciplines/:id/assignment', (p, q, body) => {
  const d = db.disciplines.find((x) => x.id === p.id)
  if (!d) throw new ApiError(404, 'Дисциплина не найдена')
  const touched = []
  d.topics.forEach((tp) => {
    if (!db.assignments[tp.id]) {
      setAssignment(tp.id, body.teacherId)
      touched.push(tp.id)
    }
  })
  return { topicIds: touched }
})
on('POST', '/assignments/batch', (p, q, body) => {
  (body.ops || []).forEach((op) => setAssignment(op.topicId, op.teacherId))
  return db.assignments
})

/* ----- teachers / absences (Справочники) ----- */
on('GET', '/teachers', () => db.teachers)
on('POST', '/teachers', (p, q, body) => {
  const t = { id: 'nt' + Date.now(), name: body.name, photo: body.photo || null, c: null, absences: [] }
  db.teachers.push(t)
  return t
})
on('PATCH', '/teachers/:id', (p, q, body) => {
  const t = db.teachers.find((x) => x.id === p.id)
  if (!t) throw new ApiError(404, 'Преподаватель не найден')
  if (body.name != null) t.name = body.name
  return t
})
on('DELETE', '/teachers/:id', (p) => {
  const t = db.teachers.find((x) => x.id === p.id)
  if (!t) throw new ApiError(404, 'Преподаватель не найден')
  if (Object.values(db.assignments).some((a) => a.teacherId === p.id) || db.lessons.some((l) => l.teacherId === p.id)) {
    throw new ApiError(409, 'На преподавателя есть назначения или занятия')
  }
  db.teachers = db.teachers.filter((x) => x.id !== p.id)
  return null
})
on('PUT', '/teachers/:id/photo', (p, q, body) => {
  const t = db.teachers.find((x) => x.id === p.id)
  if (!t) throw new ApiError(404, 'Преподаватель не найден')
  t.photo = body.dataUrl
  return t
})
on('DELETE', '/teachers/:id/photo', (p) => {
  const t = db.teachers.find((x) => x.id === p.id)
  if (!t) throw new ApiError(404, 'Преподаватель не найден')
  t.photo = null
  return t
})
on('PUT', '/teachers/:id/constraints', (p, q, body) => {
  const t = db.teachers.find((x) => x.id === p.id)
  if (!t) throw new ApiError(404, 'Преподаватель не найден')
  t.c = body
  return t
})
on('POST', '/teachers/:id/absences', (p, q, body) => {
  const t = db.teachers.find((x) => x.id === p.id)
  if (!t) throw new ApiError(404, 'Преподаватель не найден')
  const a = { id: 'ab' + (++absN), type: body.type, label: body.label || '' }
  t.absences.push(a)
  return a
})
on('PATCH', '/absences/:id', (p, q, body) => {
  for (const t of db.teachers) {
    const a = t.absences.find((x) => x.id === p.id)
    if (a) { Object.assign(a, body); return a }
  }
  throw new ApiError(404, 'Период отсутствия не найден')
})
on('DELETE', '/absences/:id', (p) => {
  db.teachers.forEach((t) => { t.absences = t.absences.filter((x) => x.id !== p.id) })
  return null
})

/* ----- rooms ----- */
on('GET', '/rooms', () => db.rooms.map((r) => ({ ...r, used: db.lessons.filter((l) => l.roomId === r.id).length })))
on('POST', '/rooms', (p, q, body) => {
  if (db.rooms.some((r) => r.id.toLowerCase() === body.id.toLowerCase())) throw new ApiError(409, 'Аудитория уже есть')
  const r = { id: body.id, capacity: body.capacity, type: body.type }
  db.rooms.push(r)
  return r
})
on('PATCH', '/rooms/:id', (p, q, body) => {
  const r = db.rooms.find((x) => x.id === p.id)
  if (!r) throw new ApiError(404, 'Аудитория не найдена')
  Object.assign(r, body)
  return r
})
on('DELETE', '/rooms/:id', (p) => {
  if (db.lessons.some((l) => l.roomId === p.id)) throw new ApiError(409, 'На аудиторию назначены пары')
  db.rooms = db.rooms.filter((x) => x.id !== p.id)
  return null
})

/* ----- lessons (Расписание) ----- */
on('GET', '/lessons', () => db.lessons)
on('POST', '/lessons', (p, q, body) => {
  db.counters.l++
  const found = body.topicId ? findTopic(body.topicId) : null
  const l = {
    id: body.id || 'm' + db.counters.l,
    topicId: body.topicId || null,
    disciplineId: body.disciplineId || (found ? found.discipline.id : null),
    groupId: body.groupId,
    teacherId: body.teacherId,
    roomId: body.roomId,
    kind: body.kind,
    period: body.period,
    day: body.day != null ? body.day : null,
    slot: body.slot != null ? body.slot : null,
    pin: !!body.pin,
    manual: body.manual !== false,
    ni: body.ni || 1,
    nt: body.nt || 1,
    topicLabel: body.topicLabel || '',
    question: body.question || '',
  }
  db.lessons.push(l)
  return l
})
on('PATCH', '/lessons/:id', (p, q, body) => {
  const l = db.lessons.find((x) => x.id === p.id)
  if (!l) throw new ApiError(404, 'Занятие не найдено')
  Object.assign(l, body)
  return l
})
on('DELETE', '/lessons/:id', (p) => {
  db.lessons = db.lessons.filter((x) => x.id !== p.id)
  return null
})
on('PUT', '/lessons/:id/pin', (p) => {
  const l = db.lessons.find((x) => x.id === p.id)
  if (!l) throw new ApiError(404, 'Занятие не найдено')
  l.pin = true
  return l
})
on('DELETE', '/lessons/:id/pin', (p) => {
  const l = db.lessons.find((x) => x.id === p.id)
  if (!l) throw new ApiError(404, 'Занятие не найдено')
  l.pin = false
  return l
})

/* ----- generation ----- */
const GEN_STAGES = ['Готовлю данные…', 'Размещаю лекции…', 'Размещаю практики…', 'Разрешаю конфликты аудиторий…', 'Проверяю пожелания…']

on('GET', '/schedule/readiness', (p, q) => {
  const period = q.period || 'fall'
  const lessons = db.lessons.filter((l) => l.period === period)
  return {
    totalPairs: lessons.length,
    placedPairs: lessons.filter((l) => l.day != null).length,
    noConstraintsTeachers: db.teachers.filter((t) => !t.c).length,
    roomsCount: db.rooms.length,
    pinnedCount: lessons.filter((l) => l.pin && l.day != null).length,
  }
})
on('POST', '/schedule/generate', (p, q, body) => {
  const period = body.period || 'fall'
  const enriched = enrichDbLessons(db, period)
  const result = computeGeneration(enriched, db.teachers, db.periods[period], body.mode)
  const id = 'job' + (++jobN)
  db.jobs[id] = { id, pct: 0, stage: 0, status: 'run', result, period }
  return { jobId: id }
})
on('GET', '/schedule/generate/:id', (p) => {
  const job = db.jobs[p.id]
  if (!job) throw new ApiError(404, 'Задача не найдена')
  if (job.status === 'run') {
    job.pct = Math.min(100, job.pct + 3 + Math.random() * 7)
    job.stage = Math.min(GEN_STAGES.length - 1, Math.floor(job.pct / 20))
    if (job.pct >= 100) job.status = 'done'
  }
  const r = job.result
  return {
    status: job.status,
    pct: Math.round(job.pct),
    stage: GEN_STAGES[job.stage],
    live: 'размещено ' + Math.round((job.pct / 100) * r.placedN) + ' / ' + (r.placedN + r.unplacedN),
    summary: job.status === 'done' ? { placedN: r.placedN, unplacedN: r.unplacedN, softN: r.softN, moved: r.moved, unplaced: r.unplaced } : null,
  }
})
on('POST', '/schedule/generate/:id/cancel', (p) => { delete db.jobs[p.id]; return null })
on('POST', '/schedule/generate/:id/rollback', (p) => { delete db.jobs[p.id]; return null })
on('POST', '/schedule/generate/:id/accept', (p) => {
  const job = db.jobs[p.id]
  if (!job) throw new ApiError(404, 'Задача не найдена')
  job.result.placements.forEach((pl) => {
    const l = db.lessons.find((x) => x.id === pl.id)
    if (l) { l.day = pl.d; l.slot = pl.s }
  })
  const newIds = job.result.newIds
  delete db.jobs[p.id]
  return { newIds }
})

/* ----- conflicts ----- */
on('GET', '/schedule/conflicts', (p, q) => {
  const period = q.period || 'fall'
  const an = analyze(enrichDbLessons(db, period), db.teachers, db.periods[period])
  return Object.keys(an.byId).map((id) => ({
    lessonSlotIds: [id],
    issues: an.byId[id],
  }))
})

/* ----- exports ----- */
on('POST', '/exports/curriculum', (p, q, body) => {
  const id = 'ex' + (++exportN)
  const suffix = body.period === 'both' ? '' : body.period === 'fall' ? '_осень' : '_весна'
  db.exports[id] = { id, status: 'done', fileName: 'Учебный_план_2026-27' + suffix + '.xlsx' }
  return { exportId: id }
})
on('POST', '/exports/schedule', (p, q, body) => {
  const id = 'ex' + (++exportN)
  const view = body.view === 'teacher' ? 'преподаватели' : 'группы'
  const per = body.period === 'spring' ? 'весна' : 'осень'
  db.exports[id] = { id, status: 'done', fileName: 'расписание_' + view + '_' + per + '.xlsx' }
  return { exportId: id }
})
on('GET', '/exports/:id', (p) => {
  const e = db.exports[p.id]
  if (!e) throw new ApiError(404, 'Экспорт не найден')
  return e
})

/* ---------------- dispatcher ---------------- */

export function mockRequest(method, url, body) {
  const [path, qs] = url.split('?')
  const query = {}
  if (qs) qs.split('&').forEach((kv) => { const [k, v] = kv.split('='); query[decodeURIComponent(k)] = decodeURIComponent(v || '') })
  for (const r of routes) {
    if (r.method !== method) continue
    const m = r.re.exec(path)
    if (!m) continue
    const params = {}
    r.keys.forEach((k, i) => { params[k] = decodeURIComponent(m[i + 1]) })
    const res = r.handler(params, query, body ? clone(body) : undefined)
    return res == null ? null : clone(res)
  }
  throw new ApiError(404, method + ' ' + path + ' — маршрут не найден')
}
