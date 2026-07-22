/**
 * Conflict analysis for the schedule module.
 *
 * Works on "enriched" lessons: { id, g, disc, t, room, kind, d, s, pin, orphan }
 * where d/s are day index (0 = Пн) and slot index, or null when the lesson
 * sits in the pool. Conflicts are computed, never stored (see data schema).
 */
import { kindHours } from './kinds.js'

/** True when a lesson of `kind` fits slot index `s` of the given config. */
function slotFits(kind, s, cfg) {
  if (!cfg || !cfg.slots || !cfg.slots[s]) return true
  return kindHours(kind) <= cfg.slots[s].hours
}

/**
 * Full pass over placed lessons.
 * Returns { byId: { lessonId: [{sev, text}] }, hardN, softN, orphanN }.
 * sev ∈ 'hard' | 'soft' | 'orphan'.
 */
export function analyze(lessons, teachers, cfg) {
  const byId = {}
  const add = (id, sev, text) => { (byId[id] = byId[id] || []).push({ sev, text }) }
  const tMap = {}
  teachers.forEach((t) => { tMap[t.id] = t })

  lessons.filter((l) => l.orphan && l.d != null).forEach((l) => {
    add(l.id, 'orphan', 'Назначение снято в «Распределении» — пара осиротела')
  })

  const placed = lessons.filter((l) => l.d != null && !l.orphan)
  const grp = (fn) => {
    const m = {}
    placed.forEach((l) => { const k = fn(l); (m[k] = m[k] || []).push(l) })
    return m
  }

  Object.values(grp((l) => l.t + '|' + l.d + '|' + l.s)).forEach((a) => {
    if (a.length > 1) a.forEach((l) => add(l.id, 'hard', 'Преподаватель в двух местах одновременно'))
  })
  Object.values(grp((l) => l.g + '|' + l.d + '|' + l.s)).forEach((a) => {
    if (a.length > 1) a.forEach((l) => add(l.id, 'hard', 'Группа в двух местах одновременно'))
  })
  Object.values(grp((l) => l.room + '|' + l.d + '|' + l.s)).forEach((a) => {
    if (a.length > 1) a.forEach((l) => add(l.id, 'hard', 'Аудитория ' + l.room + ' занята'))
  })

  // lessons that fell out of the grid after the settings were narrowed
  if (cfg) {
    const slotsN = cfg.slots ? cfg.slots.length : cfg.slotsPerDay
    placed.forEach((l) => {
      if ((cfg.activeDays && cfg.activeDays[l.d] === false) || (slotsN && l.s >= slotsN)) {
        add(l.id, 'hard', 'Пара вне учебной недели или сетки звонков (см. «Настройки»)')
      } else if (!slotFits(l.kind, l.s, cfg)) {
        add(l.id, 'hard', 'Занятие 2 ак.ч в слоте на 1 ак.ч (см. «Настройки»)')
      }
    })
  }

  placed.forEach((l) => {
    const c = tMap[l.t] && tMap[l.t].c
    if (!c) return
    const k = l.d + '-' + l.s
    if (c.method === l.d) add(l.id, 'hard', 'Методический день преподавателя')
    else if (c.hard.indexOf(k) >= 0) add(l.id, 'hard', 'Преподаватель недоступен в этот слот')
    else if (c.soft.indexOf(k) >= 0) add(l.id, 'soft', 'Нежелательный слот преподавателя')
  })

  Object.values(grp((l) => l.t + '|' + l.d)).forEach((a) => {
    const c = tMap[a[0].t] && tMap[a[0].t].c
    if (c && c.max && a.length > c.max) {
      a.forEach((l) => add(l.id, 'hard', 'Превышен максимум пар в день (' + c.max + ')'))
    }
  })

  let hardN = 0
  let softN = 0
  let orphanN = 0
  Object.keys(byId).forEach((id) => {
    const sevs = byId[id].map((x) => x.sev)
    if (sevs.indexOf('hard') >= 0) hardN++
    else if (sevs.indexOf('orphan') >= 0) orphanN++
    else softN++
  })
  return { byId, hardN, softN, orphanN }
}

/**
 * Status of dropping lesson L into (d, s) with room r.
 * Returns { kind: 'free'|'soft'|'hard', text }.
 */
export function slotStatus(L, d, s, r, lessons, teachers, cfg) {
  const tMap = {}
  teachers.forEach((t) => { tMap[t.id] = t })
  const tName = tMap[L.t] ? tMap[L.t].name : ''
  if (!slotFits(L.kind, s, cfg)) return { kind: 'unfit', text: 'Занятие 2 ак.ч не помещается в слот на 1 ак.ч' }
  const others = lessons.filter((x) => x.id !== L.id && x.d === d && x.s === s && !x.orphan)
  if (others.some((x) => x.t === L.t)) return { kind: 'hard', text: 'Преподаватель ' + tName + ' уже занят в этом слоте' }
  if (others.some((x) => x.g === L.g)) return { kind: 'hard', text: 'Группа ' + L.g + ' уже занята в этом слоте' }
  if (others.some((x) => x.room === (r || L.room))) return { kind: 'hard', text: 'Аудитория ' + (r || L.room) + ' занята' }
  const c = tMap[L.t] && tMap[L.t].c
  if (c) {
    const k = d + '-' + s
    if (c.method === d) return { kind: 'hard', text: 'Методический день преподавателя' }
    if (c.hard.indexOf(k) >= 0) return { kind: 'hard', text: 'Преподаватель недоступен в этот слот' }
    if (c.max) {
      const n = lessons.filter((x) => x.id !== L.id && x.t === L.t && x.d === d && !x.orphan).length
      if (n + 1 > c.max) return { kind: 'hard', text: 'Превышен максимум пар в день (' + c.max + ')' }
    }
    if (c.soft.indexOf(k) >= 0) return { kind: 'soft', text: 'Нежелательный слот преподавателя — можно, но генератор бы избегал' }
  }
  return { kind: 'free', text: 'Слот свободен, конфликтов нет' }
}
