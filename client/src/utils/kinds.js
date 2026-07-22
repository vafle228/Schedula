/**
 * Canonical catalogue of lesson types — the single source of truth shared by
 * the «Распределение» and «Расписание» modules. Add a row here to offer a new
 * kind everywhere. Each kind carries one base `color`; the border / fill / text
 * tints used on schedule cards are derived from it so the palette stays in sync.
 */
const rgb = (hex) => {
  const n = parseInt(hex.slice(1), 16)
  return [(n >> 16) & 255, (n >> 8) & 255, n & 255]
}
const tint = (hex, a) => { const [r, g, b] = rgb(hex); return `rgba(${r}, ${g}, ${b}, ${a})` }
const darken = (hex, f = 0.72) => {
  const [r, g, b] = rgb(hex).map((c) => Math.round(c * f))
  return '#' + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1).toUpperCase()
}
const MARK = { '50%': '●', '2px': '▪', '3px': '◆' }

const KIND_DEFS = [
  { k: 'lec', label: 'Лекция', short: 'Лек.', color: '#3B62C4', radius: '50%' },
  { k: 'prac', label: 'Практика', short: 'Практ.', color: '#1F8A5B', radius: '2px' },
  { k: 'lab', label: 'Лабораторная', short: 'Лаб.', color: '#B45309', radius: '2px' },
  { k: 'sem', label: 'Семинар', short: 'Сем.', color: '#8A3FFC', radius: '50%' },
  { k: 'consult', label: 'Консультация', short: 'Конс.', color: '#0E7490', radius: '3px' },
  { k: 'exam', label: 'Экзамен', short: 'Экз.', color: '#C0392B', radius: '3px' },
  { k: 'course', label: 'Курсовая', short: 'Курс.', color: '#7A756C', radius: '3px' },
]

/** Ordered list form — for `v-for` iteration (used by «Распределение»). */
export const KIND_LIST = KIND_DEFS.map((d) => ({
  ...d,
  dot: d.color,
  bd: tint(d.color, 0.35),
  bg: tint(d.color, 0.1),
  dark: darken(d.color),
  mark: MARK[d.radius] || '▪',
}))

/** Keyed form — for lookup and `(K, k) in KINDS` iteration (used by «Расписание»). */
export const KINDS = Object.fromEntries(KIND_LIST.map((x) => [x.k, x]))

export const kindOf = (k) => KINDS[k] || KIND_LIST[0]
export const kindLabel = (k) => kindOf(k).label
export const kindColor = (k) => kindOf(k).color
export const kindShort = (k) => kindOf(k).short
export const dotRadius = (k) => kindOf(k).radius

export const ROOM_TYPES = ['Лекционная', 'Семинарская', 'Комп. класс', 'Лаборатория', 'Спортивный зал', 'Актовый зал']

export const ABSENCE_TYPES = [
  { v: 'vacation', label: 'Отпуск' },
  { v: 'sick', label: 'Больничный' },
  { v: 'trip', label: 'Командировка' },
  { v: 'other', label: 'Другое' },
]

export const ABSENCE_COLORS = { vacation: '#D97706', sick: '#C24536', trip: '#3B62C4', other: '#8A857C' }

export const ALL_DAYS = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
