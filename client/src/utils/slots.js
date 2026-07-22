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
