/** Visual treatment per lesson kind — one accent per kind, shared by grid, pool and legend. */
export const KINDS = {
  lec: { label: 'Лекция', mark: '●', bd: 'rgba(59,98,196,0.35)', bg: 'rgba(59,98,196,0.10)', dark: '#2A4B9E', dot: '#3B62C4' },
  prac: { label: 'Практика', mark: '▪', bd: 'rgba(31,138,91,0.35)', bg: 'rgba(31,138,91,0.10)', dark: '#166A45', dot: '#1F8A5B' },
  sem: { label: 'Семинар', mark: '◆', bd: 'rgba(138,87,180,0.35)', bg: 'rgba(138,87,180,0.10)', dark: '#6E4197', dot: '#8A57B4' },
  lab: { label: 'Лаб. работа', mark: '▣', bd: 'rgba(46,138,138,0.35)', bg: 'rgba(46,138,138,0.10)', dark: '#20706F', dot: '#2E8A8A' },
}

export const kindOf = (k) => KINDS[k] || KINDS.lec

export const ROOM_TYPES = ['Лекционная', 'Семинарская', 'Комп. класс', 'Лаборатория', 'Спортивный зал', 'Актовый зал']

export const ABSENCE_TYPES = [
  { v: 'vacation', label: 'Отпуск' },
  { v: 'sick', label: 'Больничный' },
  { v: 'trip', label: 'Командировка' },
  { v: 'other', label: 'Другое' },
]

export const ABSENCE_COLORS = { vacation: '#D97706', sick: '#C24536', trip: '#3B62C4', other: '#8A857C' }

export const ALL_DAYS = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
