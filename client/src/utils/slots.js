/**
 * Bell-grid arithmetic (Итерация 6.2/6.3). A slot is described only by its
 * start time and how many academic hours it spans (1 or 2); its end is derived
 * from the academic-hour length plus 5 min between hours inside one pair.
 */
export function toMin(t) {
  const [a, b] = String(t).split(':')
  return (+a) * 60 + (+b || 0)
}

export function toStr(m) {
  m = ((m % 1440) + 1440) % 1440
  return String(Math.floor(m / 60)).padStart(2, '0') + ':' + String(m % 60).padStart(2, '0')
}

/** Minutes a slot of `hours` academic hours occupies. */
export function slotLen(hours, acadMin) {
  return hours * acadMin + (hours - 1) * 5
}

export function slotEnd(start, hours, acadMin) {
  return toStr(toMin(start) + slotLen(hours, acadMin))
}

/** Slots → bell rows { from, to, hours } for the grid and export. */
export function slotBells(slots, acadMin) {
  return (slots || []).map((s) => ({
    from: s.start,
    to: slotEnd(s.start, s.hours, acadMin),
    hours: s.hours,
  }))
}

/**
 * Auto-fill slot start times from the day start, break and long break.
 * Slot composition (how many hours each) is kept as-is; only starts change.
 */
export function recalcStarts(slots, { start, brk, long, longAfter }, acadMin) {
  let t = toMin(start)
  return slots.map((s, i) => {
    const row = { start: toStr(t), hours: s.hours }
    t += slotLen(s.hours, acadMin) + (i + 1 === longAfter ? long : brk)
    return row
  })
}
