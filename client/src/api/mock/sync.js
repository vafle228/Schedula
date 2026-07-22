/**
 * Reconciles lesson slots with the plan (Распределение).
 *
 * Rule set (matches the data schema notes):
 *  - an assigned topic owns pairsPerWeek lesson slots (авто = часы ÷ 2 ÷ недель);
 *  - unassigning keeps already placed pairs (they become «осиротевшие») but
 *    drops the pool ones;
 *  - reassigning moves every pair of the topic to the new teacher.
 */

export function pairsPerWeek(topic, period) {
  return Math.max(1, Math.round(topic.hours / 2 / (period.weeksCount || 16)))
}

function defaultRoom(db, topic, discipline) {
  const sibling = db.lessons.find((l) => l.disciplineId === discipline.id)
  if (sibling) return sibling.roomId
  const wanted = topic.kind === 'prac' ? 'Комп. класс' : 'Лекционная'
  const room = db.rooms.find((r) => r.type === wanted) || db.rooms[0]
  return room ? room.id : ''
}

export function syncLessonsForTopic(db, topicId) {
  let topic = null
  let discipline = null
  for (const d of db.disciplines) {
    const tp = d.topics.find((x) => x.id === topicId)
    if (tp) { topic = tp; discipline = d; break }
  }
  const asg = db.assignments[topicId]

  if (!topic || !discipline || !asg) {
    // topic gone or unassigned: pool pairs disappear, placed ones stay orphaned
    db.lessons = db.lessons.filter((l) => l.topicId !== topicId || (topic && l.day != null))
    return
  }

  const period = db.periods[discipline.period]
  const nt = pairsPerWeek(topic, period)
  asg.pairsPerWeek = nt

  const own = db.lessons.filter((l) => l.topicId === topicId)
  own.forEach((l) => { l.teacherId = asg.teacherId; l.period = discipline.period })

  const auto = own.filter((l) => !l.manual)
  const placedN = auto.filter((l) => l.day != null).length
  const target = Math.max(nt, placedN)

  // trim surplus pool pairs
  let surplus = auto.length - target
  if (surplus > 0) {
    const removable = auto.filter((l) => l.day == null).slice(-surplus).map((l) => l.id)
    db.lessons = db.lessons.filter((l) => removable.indexOf(l.id) < 0)
  }

  // add missing pool pairs
  const have = db.lessons.filter((l) => l.topicId === topicId && !l.manual).length
  for (let i = have; i < target; i++) {
    db.counters.l++
    db.lessons.push({
      id: 'l' + db.counters.l, topicId, disciplineId: discipline.id, groupId: discipline.groupId,
      teacherId: asg.teacherId, roomId: defaultRoom(db, topic, discipline), kind: topic.kind,
      period: discipline.period, week: null, day: null, slot: null, subBy: null, pin: false, manual: false,
      ni: 0, nt: target, topicLabel: '', question: '',
    })
  }

  // renumber
  let ni = 0
  db.lessons.forEach((l) => {
    if (l.topicId === topicId && !l.manual) { l.ni = ++ni; l.nt = target }
  })
}

/** Enriched view used by the generator and the conflicts endpoint. */
export function enrichDbLessons(db, period) {
  const discById = {}
  db.disciplines.forEach((d) => { discById[d.id] = d })
  return db.lessons
    .filter((l) => l.period === period)
    .map((l) => ({
      id: l.id,
      g: l.groupId,
      disc: discById[l.disciplineId] ? discById[l.disciplineId].name : '',
      t: l.teacherId,
      room: l.roomId,
      kind: l.kind,
      w: l.week,
      d: l.day,
      s: l.slot,
      subBy: l.subBy || null,
      pin: l.pin,
      orphan: !db.assignments[l.topicId],
    }))
}
