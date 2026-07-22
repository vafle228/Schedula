import { slotStatus } from './conflicts.js'

/**
 * Draft schedule generator (greedy). Operates on enriched lessons
 * ({ id, g, disc, t, room, kind, w, d, s, subBy, pin, orphan }) and returns new
 * placements ({ id, w, d, s }) without touching the input. Занятия
 * распределяются по неделям семестра: для каждой пары ищется самый ранний
 * свободный слот (неделя → день → слот), праздники и узкие слоты пропускаются.
 *
 * mode 'rebuild' — unplace everything except pinned/orphaned, then fill;
 * mode 'fill'    — keep placed lessons, only place the pool.
 */
export function computeGeneration(enriched, teachers, cfg, mode) {
  const lessons = JSON.parse(JSON.stringify(enriched))
  const dayIdxs = []
  cfg.activeDays.forEach((on, i) => { if (on) dayIdxs.push(i) })
  const weeksN = cfg.weeksCount || 16
  const slotsN = cfg.slots ? cfg.slots.length : cfg.slotsPerDay
  let moved = 0
  if (mode === 'rebuild') {
    lessons.forEach((l) => {
      if (l.d != null && !l.pin && !l.orphan) { l.w = null; l.d = null; l.s = null; moved++ }
    })
  }
  const todo = lessons
    .filter((l) => l.d == null)
    .sort((a, b) => (a.kind === b.kind ? 0 : a.kind === 'lec' ? -1 : 1))
  const newIds = []
  let softUsed = 0
  todo.forEach((L) => {
    let softBest = null
    outer:
    for (let w = 1; w <= weeksN; w++) {
      for (const d of dayIdxs) {
        for (let s = 0; s < slotsN; s++) {
          const st = slotStatus(L, w, d, s, null, lessons, teachers, cfg)
          if (st.kind === 'hard' || st.kind === 'unfit') continue
          if (st.kind === 'soft') { if (!softBest) softBest = [w, d, s]; continue }
          L.w = w
          L.d = d
          L.s = s
          newIds.push(L.id)
          break outer
        }
      }
    }
    if (L.d == null && softBest) {
      L.w = softBest[0]
      L.d = softBest[1]
      L.s = softBest[2]
      newIds.push(L.id)
      softUsed++
    }
  })
  const unplaced = lessons.filter((l) => l.d == null)
  return {
    placements: lessons.map((l) => ({ id: l.id, w: l.w, d: l.d, s: l.s })),
    newIds,
    placedN: newIds.length,
    unplacedN: unplaced.length,
    softN: softUsed,
    moved,
    unplaced: unplaced.map((l) => ({ id: l.id, disc: l.disc, g: l.g, kind: l.kind })),
  }
}
