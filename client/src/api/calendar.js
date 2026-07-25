/**
 * Client for the Russian production-calendar API (calendar.kuzyak.in) — the
 * primary source of the "day off" calendar. Talks straight to the external
 * service (its responses carry `Access-Control-Allow-Origin: *`), so no backend
 * proxy is needed.
 */

export const CALENDAR_BASE = 'https://calendar.kuzyak.in'

/** Error raised when the calendar service is unreachable or answers badly. */
export class CalendarError extends Error {}

/**
 * Fetch non-working days for a calendar year.
 * Returns `{ year, holidays: [{ date, name }], shortDays: [{ date, name }] }`
 * with `date` normalised to `yyyy-mm-dd`. Raises {@link CalendarError}.
 */
export async function fetchYearCalendar(year) {
  const url = `${CALENDAR_BASE}/api/calendar/${year}/holidays`
  let res
  try {
    res = await fetch(url, { headers: { Accept: 'application/json' } })
  } catch (e) {
    throw new CalendarError('Не удалось связаться с календарём: ' + (e && e.message ? e.message : 'нет сети'))
  }
  if (!res.ok) throw new CalendarError('Календарь ответил ошибкой (' + res.status + ')')
  let data
  try {
    data = await res.json()
  } catch {
    throw new CalendarError('Календарь вернул некорректный ответ')
  }
  const norm = (list) => (Array.isArray(list) ? list : []).map((x) => ({
    date: String(x.date || '').slice(0, 10),
    name: x.name || '',
  })).filter((x) => x.date)
  return { year, holidays: norm(data.holidays), shortDays: norm(data.shortDays) }
}
