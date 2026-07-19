import { slotStatus } from './conflicts.js'

/**
 * Draft schedule generator (greedy). Operates on enriched lessons
 * ({ id, g, disc, t, room, kind, d, s, pin, orphan }) and returns new
 * placements without touching the input.
 *
 * mode 'rebuild' — unplace everything except pinned/orphaned, then fill;
 * mode 'fill'    — keep placed lessons, only place the pool.
 */
export function computeGeneration(enriched, teachers, cfg, mode) {
  const lessons = JSON.parse(JSON.stringify(enriched))
  const dayIdxs = []
  cfg.activeDays.forEach((on, i) => { if (on) dayIdxs.push(i) })
  let moved = 0
  if (mode === 'rebuild') {
    lessons.forEach((l) => {
      if (l.d != null && !l.pin && !l.orphan) { l.d = null; l.s = null; moved++ }
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
    for (const d of dayIdxs) {
      for (let s = 0; s < cfg.slotsPerDay; s++) {
        const st = slotStatus(L, d, s, null, lessons, teachers)
        if (st.kind === 'hard') continue
        if (st.kind === 'soft') { if (!softBest) softBest = [d, s]; continue }
        L.d = d
        L.s = s
        newIds.push(L.id)
        break outer
      }
    }
    if (L.d == null && softBest) {
      L.d = softBest[0]
      L.s = softBest[1]
      newIds.push(L.id)
      softUsed++
    }
  })
  const unplaced = lessons.filter((l) => l.d == null)
  return {
    placements: lessons.map((l) => ({ id: l.id, d: l.d, s: l.s })),
    newIds,
    placedN: newIds.length,
    unplacedN: unplaced.length,
    softN: softUsed,
    moved,
    unplaced: unplaced.map((l) => ({ id: l.id, disc: l.disc, g: l.g, kind: l.kind })),
  }
}
