/**
 * Client for the Russian production calendar — the primary source of the "day
 * off" calendar. Two services are combined, each doing what it does best; both
 * answer with `Access-Control-Allow-Origin: *`, so no backend proxy is needed.
 *
 *  • isdayoff.ru — the source of truth for *which* days are non-working. It
 *    answers `getdata` with a compact bitmask (one char per day-of-year, index
 *    0-based): `0` = working, `1` = non-working, `2` = shortened pre-holiday.
 *    It captures government transfers / bridge days precisely, but carries no
 *    names and doesn't tell a public holiday from an ordinary weekend — both
 *    are `1`. So we count a `1` as a *holiday* only when it falls on a Mon–Fri
 *    (a normally-working weekday); Sat/Sun `1`s are the weekly weekend and are
 *    left to the grid's own `activeDays` handling (crucial for institutions
 *    that teach on Saturdays).
 *
 *  • date.nager.at — a name lookup by date. Its `localName` gives the official
 *    Russian holiday name ("Новый год", "День защитника Отечества", …). This
 *    call is best-effort: if it fails, day-offs still load, just unnamed.
 *
 * A small map of fixed-date federal holidays backs Nager up as an offline
 * fallback for the common names.
 */

export const CALENDAR_BASE = 'https://isdayoff.ru'
const NAMES_BASE = 'https://date.nager.at'

/** Error raised when the calendar service is unreachable or answers badly. */
export class CalendarError extends Error {}

/** Fixed-date federal non-working holidays, keyed by `"MM-DD"` — name fallback. */
const HOLIDAY_NAMES = {
  '01-01': 'Новый год',
  '01-02': 'Новогодние каникулы',
  '01-03': 'Новогодние каникулы',
  '01-04': 'Новогодние каникулы',
  '01-05': 'Новогодние каникулы',
  '01-06': 'Новогодние каникулы',
  '01-07': 'Рождество Христово',
  '01-08': 'Новогодние каникулы',
  '02-23': 'День защитника Отечества',
  '03-08': 'Международный женский день',
  '05-01': 'Праздник Весны и Труда',
  '05-09': 'День Победы',
  '06-12': 'День России',
  '11-04': 'День народного единства',
}

/** ISO `yyyy-mm-dd` of a Date, in local time. */
function toISO(dt) {
  return dt.getFullYear() + '-'
    + String(dt.getMonth() + 1).padStart(2, '0') + '-'
    + String(dt.getDate()).padStart(2, '0')
}

/**
 * Fetch official Russian holiday names for a year from Nager.Date, as a
 * `Map<"yyyy-mm-dd", name>`. Best-effort: any failure yields an empty map so
 * the caller can still produce (unnamed) day-offs.
 */
async function fetchHolidayNames(year) {
  const out = new Map()
  try {
    const res = await fetch(`${NAMES_BASE}/api/v3/PublicHolidays/${year}/RU`, {
      headers: { Accept: 'application/json' },
    })
    if (!res.ok) return out
    const list = await res.json()
    if (!Array.isArray(list)) return out
    for (const h of list) {
      const date = String(h && h.date ? h.date : '').slice(0, 10)
      const name = (h && (h.localName || h.name)) || ''
      if (date && name && !out.has(date)) out.set(date, name)
    }
  } catch { /* non-fatal — names are optional */ }
  return out
}

/**
 * Fetch non-working days for a calendar year.
 * Returns `{ year, holidays: [{ date, name }], shortDays: [{ date, name }] }`
 * with `date` normalised to `yyyy-mm-dd`. Raises {@link CalendarError} only when
 * the authoritative day-off source (isdayoff.ru) is unreachable or malformed.
 */
export async function fetchYearCalendar(year) {
  const url = `${CALENDAR_BASE}/api/getdata?year=${year}&pre=1&cc=ru`
  let res
  let names
  try {
    // Day-offs (required) and names (best-effort) fetched together.
    [res, names] = await Promise.all([
      fetch(url, { headers: { Accept: 'text/plain' } }),
      fetchHolidayNames(year),
    ])
  } catch (e) {
    throw new CalendarError('Не удалось связаться с календарём: ' + (e && e.message ? e.message : 'нет сети'))
  }
  if (!res.ok) throw new CalendarError('Календарь ответил ошибкой (' + res.status + ')')
  const body = (await res.text()).trim()
  // Expect one digit per day of the year; anything else is an error payload.
  if (!/^[0-9]+$/.test(body) || (body.length !== 365 && body.length !== 366)) {
    throw new CalendarError('Календарь вернул некорректный ответ')
  }

  // Per-day: ISO date, weekday and best-known name (Nager → static fallback).
  const info = []
  const day = new Date(year, 0, 1)
  for (let i = 0; i < body.length; i++) {
    const iso = toISO(day)
    info.push({ iso, wd: day.getDay(), name: names.get(iso) || HOLIDAY_NAMES[iso.slice(5)] || '' })
    day.setDate(day.getDate() + 1)
  }

  const holidays = []
  const shortDays = []
  for (let i = 0; i < body.length; i++) {
    const code = body[i]
    if (code === '1') {
      const { iso, wd } = info[i] // 0 = Sun … 6 = Sat
      if (wd !== 0 && wd !== 6) {
        // A bridge / transferred day-off (no name of its own) inherits the name
        // of the nearest named day within the same run of consecutive
        // non-working days — the holiday break it belongs to. So a Friday added
        // onto «День труда» reads «День труда» too.
        let name = info[i].name
        if (!name) {
          let lo = i; let hi = i
          while (lo - 1 >= 0 && body[lo - 1] === '1') lo--
          while (hi + 1 < body.length && body[hi + 1] === '1') hi++
          let best = 0
          for (let j = lo; j <= hi; j++) {
            if (info[j].name && (!name || Math.abs(j - i) < best)) { name = info[j].name; best = Math.abs(j - i) }
          }
        }
        holidays.push({ date: iso, name })
      }
    } else if (code === '2') {
      shortDays.push({ date: info[i].iso, name: '' })
    }
  }
  return { year, holidays, shortDays }
}
