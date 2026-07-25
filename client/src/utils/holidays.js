/**
 * Mapping between real calendar dates and the schedule's (week-day) grid cells.
 *
 * A cell is the string `"w-d"` where `w` is the 1-based teaching week and `d`
 * the 0-based day, both counted from the semester's `startDate` — the exact
 * convention `dateFor()` uses in the schedule module and `isHoliday()` in the
 * conflict engine. Holidays landing on a weekend / non-teaching day carry no
 * cell (the grid already skips those days) and are simply dropped.
 */

const DAY = 86400000
const WD = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
const MONTHS = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
  'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']

/** Parse an ISO date (`yyyy-mm-dd`, time ignored) as a local midnight Date. */
export function parseISO(s) {
  return new Date(String(s).slice(0, 10) + 'T00:00:00')
}

/** Parse an ISO (`yyyy-mm-dd`) or Russian (`dd.mm.yyyy`) date, or `null`. */
export function parseAny(s) {
  const v = String(s || '').trim()
  if (/^\d{4}-\d{2}-\d{2}/.test(v)) return parseISO(v)
  const m = v.match(/^(\d{2})\.(\d{2})\.(\d{4})$/)
  if (m) return new Date(Number(m[3]), Number(m[2]) - 1, Number(m[1]))
  return null
}

/**
 * Last teaching day of the semester as a Date. Bounded by the grid
 * (`startDate + weeksCount` weeks) and, when tighter, the year's declared
 * end date (`dateTo`) — so day-offs never fall outside the semester window.
 */
export function periodEnd(cfg) {
  if (!cfg || !cfg.startDate) return null
  const gridEnd = parseISO(cfg.startDate)
  gridEnd.setDate(gridEnd.getDate() + (cfg.weeksCount || 16) * 7 - 1)
  const declared = parseAny(cfg.dateTo)
  return declared && declared < gridEnd ? declared : gridEnd
}

/** ISO `yyyy-mm-dd` of a Date, in local time. */
function toISO(dt) {
  return dt.getFullYear() + '-'
    + String(dt.getMonth() + 1).padStart(2, '0') + '-'
    + String(dt.getDate()).padStart(2, '0')
}

/** Calendar years the semester spans (usually one, occasionally two). */
export function periodYears(cfg) {
  if (!cfg || !cfg.startDate) return []
  const start = parseISO(cfg.startDate)
  const weeks = cfg.weeksCount || 16
  const end = new Date(start)
  end.setDate(end.getDate() + weeks * 7 - 1)
  const out = []
  for (let y = start.getFullYear(); y <= end.getFullYear(); y++) out.push(y)
  return out
}

/** Grid cell `"w-d"` for an ISO date, or `null` when outside the semester. */
export function dateToCell(cfg, iso) {
  if (!cfg || !cfg.startDate) return null
  const day = parseISO(iso)
  const diff = Math.round((day - parseISO(cfg.startDate)) / DAY)
  if (diff < 0) return null // before the semester starts
  const end = periodEnd(cfg)
  if (end && day > end) return null // after the semester ends
  const w = Math.floor(diff / 7) + 1
  const d = diff % 7
  if (w > (cfg.weeksCount || 16)) return null
  if (cfg.activeDays && !cfg.activeDays[d]) return null // weekend / non-teaching day
  return w + '-' + d
}

/** ISO `yyyy-mm-dd` of a grid cell `"w-d"` given the period start. */
export function cellToISO(cfg, cell) {
  if (!cfg || !cfg.startDate) return ''
  const [w, d] = String(cell).split('-').map(Number)
  const dt = parseISO(cfg.startDate)
  dt.setDate(dt.getDate() + (w - 1) * 7 + d)
  return toISO(dt)
}

/**
 * Human-readable descriptor of a cell for the settings panel:
 * `{ cell, iso, w, d, wd, dom, ym, monthLabel, dmy }`.
 */
export function describeCell(cfg, cell) {
  const [w, d] = String(cell).split('-').map(Number)
  const iso = cellToISO(cfg, cell)
  const dt = iso ? parseISO(iso) : null
  return {
    cell,
    iso,
    w,
    d,
    wd: WD[d] || '',
    dom: dt ? dt.getDate() : 0,
    ym: dt ? iso.slice(0, 7) : '',
    monthLabel: dt ? MONTHS[dt.getMonth()] + ' ' + dt.getFullYear() : '',
    dmy: dt ? String(dt.getDate()).padStart(2, '0') + '.'
      + String(dt.getMonth() + 1).padStart(2, '0') + '.' + dt.getFullYear() : '',
  }
}

/**
 * Fold a list of `{ date, name }` holidays into a sorted, de-duplicated list of
 * cells that fall on teaching days of the period. Returns
 * `{ cells: ["w-d"], named: [{ cell, date, name }] }`.
 */
export function holidaysToCells(cfg, holidays) {
  const seen = new Set()
  const named = []
  for (const h of holidays || []) {
    const cell = dateToCell(cfg, h.date)
    if (!cell || seen.has(cell)) continue
    seen.add(cell)
    named.push({ cell, date: h.date, name: h.name || '' })
  }
  const cells = [...seen].sort(cellCmp)
  return { cells, named }
}

/** Sort comparator for `"w-d"` cells: by week then day. */
export function cellCmp(a, b) {
  const [aw, ad] = a.split('-').map(Number)
  const [bw, bd] = b.split('-').map(Number)
  return aw - bw || ad - bd
}
