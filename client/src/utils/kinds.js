/**
 * Catalogue of lesson types — the single source of truth (стор `topicTypes`)
 * shared by the «Распределение» and «Расписание» modules and the «Типы занятий»
 * справочник. The list is reactive and mutable at runtime: the store fills it
 * from the API on init (see applyTopicTypes). Each type carries a base `color`
 * (the round marker everywhere) plus `short` label and `acHours` duration; the
 * border / fill / text tints on schedule cards are derived so the palette stays
 * in sync. Shapes were dropped in Итерация 6.5 — the marker is always round.
 */
import { reactive } from 'vue'

const rgb = (hex) => {
  const n = parseInt(hex.slice(1), 16)
  return [(n >> 16) & 255, (n >> 8) & 255, n & 255]
}
const tint = (hex, a) => { const [r, g, b] = rgb(hex); return `rgba(${r}, ${g}, ${b}, ${a})` }
const darken = (hex, f = 0.72) => {
  const [r, g, b] = rgb(hex).map((c) => Math.round(c * f))
  return '#' + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1).toUpperCase()
}

/** Factory defaults — also seed the mock backend (imported by api/mock/seed.js). */
export const DEFAULT_TOPIC_TYPES = [
  { k: 'lec', label: 'Лекция', short: 'Лек.', color: '#3B62C4', acHours: 2 },
  { k: 'prac', label: 'Практика', short: 'Практ.', color: '#1F8A5B', acHours: 2 },
  { k: 'lab', label: 'Лабораторная', short: 'Лаб.', color: '#B45309', acHours: 2 },
  { k: 'sem', label: 'Семинар', short: 'Сем.', color: '#8A3FFC', acHours: 2 },
  { k: 'consult', label: 'Консультация', short: 'Конс.', color: '#0E7490', acHours: 1 },
  { k: 'exam', label: 'Экзамен', short: 'Экз.', color: '#C0392B', acHours: 2 },
  { k: 'course', label: 'Курсовая', short: 'Курс.', color: '#7A756C', acHours: 2 },
]

function decorate(d) {
  return {
    k: d.k,
    label: d.label,
    short: d.short,
    color: d.color,
    acHours: d.acHours || 2,
    dot: d.color,
    bd: tint(d.color, 0.35),
    bg: tint(d.color, 0.1),
    dark: darken(d.color),
    mark: '●',
    radius: '50%',
  }
}

/** Ordered list form — for `v-for` iteration (used by «Распределение»). */
export const KIND_LIST = reactive([])
/** Keyed form — for lookup and `(K, k) in KINDS` iteration (used by «Расписание»). */
export const KINDS = reactive({})

/** Rebuild both catalogue forms in place so existing reactive refs stay valid. */
export function applyTopicTypes(defs) {
  const list = (defs && defs.length ? defs : DEFAULT_TOPIC_TYPES).map(decorate)
  KIND_LIST.splice(0, KIND_LIST.length, ...list)
  Object.keys(KINDS).forEach((k) => { delete KINDS[k] })
  list.forEach((x) => { KINDS[x.k] = x })
}

applyTopicTypes(DEFAULT_TOPIC_TYPES) // pre-API defaults so the first render has types

export const kindOf = (k) => KINDS[k] || KIND_LIST[0]
export const kindLabel = (k) => kindOf(k).label
export const kindColor = (k) => kindOf(k).color
export const kindShort = (k) => kindOf(k).short
export const dotRadius = () => '50%'
/** Academic hours a lesson of this type occupies — drives the slot-fit rule. */
export const kindHours = (k) => (kindOf(k) ? kindOf(k).acHours : 2)

export const ROOM_TYPES = ['Лекционная', 'Семинарская', 'Комп. класс', 'Лаборатория', 'Спортивный зал', 'Актовый зал']

export const ABSENCE_TYPES = [
  { v: 'vacation', label: 'Отпуск' },
  { v: 'sick', label: 'Больничный' },
  { v: 'trip', label: 'Командировка' },
  { v: 'other', label: 'Другое' },
]

export const ABSENCE_COLORS = { vacation: '#D97706', sick: '#C24536', trip: '#3B62C4', other: '#8A857C' }

export const ALL_DAYS = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
