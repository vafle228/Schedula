/**
 * Seed data for the mock backend. One coherent dataset feeds all four
 * modules: Справочники own the master data, Распределение owns the plan
 * (disciplines → topics → assignments), Расписание owns lesson slots.
 */

import { DEFAULT_TOPIC_TYPES } from '../../utils/kinds.js'

/** 5 равномерных слотов: 4×2 ак.ч + 1×1 ак.ч (Итерация 6.4, Настройки v2). */
const DEFAULT_SLOTS = [
  { start: '08:30', hours: 2 }, { start: '10:20', hours: 2 }, { start: '12:25', hours: 2 },
  { start: '14:10', hours: 2 }, { start: '16:00', hours: 1 },
]

export function buildSeed() {
  const periods = {
    fall: {
      id: 'fall',
      dateFrom: '01.09.2026',
      dateTo: '27.12.2026',
      activeDays: [true, true, true, true, true, false, false],
      acadMin: 45,
      slots: DEFAULT_SLOTS.map((s) => ({ ...s })),
      slotsPerDay: DEFAULT_SLOTS.length,
      ag: { start: '08:30', brk: 15, long: 30, longAfter: 2 },
      weeksCount: 16,
    },
    spring: {
      id: 'spring',
      dateFrom: '09.02.2027',
      dateTo: '31.05.2027',
      activeDays: [true, true, true, true, true, false, false],
      acadMin: 45,
      slots: DEFAULT_SLOTS.map((s) => ({ ...s })),
      slotsPerDay: DEFAULT_SLOTS.length,
      ag: { start: '08:30', brk: 15, long: 30, longAfter: 2 },
      weeksCount: 16,
    },
  }

  // Явная сущность «семестр» (Итерация 6.1). Строки текущего года ('fall'/'spring')
  // переключают активный сезон; прошлые — только для чтения. Активность выводится
  // из state.period в сторе, поле status здесь — начальное значение.
  const semesters = [
    { id: 'aut2526', name: 'Осень 2025/26', from: '01.09.2025', to: '28.12.2025', status: 'done', current: false },
    { id: 'spr2526', name: 'Весна 2025/26', from: '09.02.2026', to: '31.05.2026', status: 'done', current: false },
    { id: 'fall', name: 'Осень 2026/27', from: '01.09.2026', to: '27.12.2026', status: 'active', current: true },
    { id: 'spring', name: 'Весна 2026/27', from: '08.02.2027', to: '30.05.2027', status: 'draft', current: true },
  ]

  const topicTypes = DEFAULT_TOPIC_TYPES.map((t) => ({ ...t }))

  const teachers = [
    { id: 't1', name: 'Орлова И.К.', photo: null, c: { hard: ['0-6', '1-6'], soft: [], method: 2, max: 4 }, absences: [{ id: 'a1', type: 'vacation', label: '01–14 сентября' }, { id: 'a2', type: 'trip', label: '20–22 октября' }] },
    { id: 't2', name: 'Ким Д.С.', photo: null, c: { hard: ['0-0', '0-1'], soft: ['4-5', '4-6'], method: null, max: 3 }, absences: [] },
    { id: 't3', name: 'Стеклов П.А.', photo: null, c: { hard: [], soft: ['0-0'], method: 4, max: 4 }, absences: [{ id: 'a3', type: 'vacation', label: '10–24 марта' }] },
    { id: 't4', name: 'Белов А.Н.', photo: null, c: null, absences: [] },
    { id: 't5', name: 'Юсупова Р.М.', photo: null, c: { hard: ['3-5', '3-6', '4-5', '4-6'], soft: [], method: null, max: null }, absences: [{ id: 'a4', type: 'vacation', label: '07–20 октября' }, { id: 'a5', type: 'sick', label: '03–05 ноября' }] },
    { id: 't6', name: 'Дроздова Е.В.', photo: null, c: { hard: [], soft: ['0-5', '0-6'], method: null, max: 4 }, absences: [] },
    { id: 't7', name: 'Гарин О.Л.', photo: null, c: null, absences: [] },
    { id: 't8', name: 'Мельник С.С.', photo: null, c: { hard: ['2-0', '2-1', '2-2'], soft: [], method: null, max: 4 }, absences: [{ id: 'a6', type: 'vacation', label: '01–14 апреля' }] },
    { id: 't9', name: 'Ахматова Л.Р.', photo: null, c: null, absences: [] },
    { id: 't10', name: 'Козлов В.П.', photo: null, c: null, absences: [] },
  ]

  const rooms = [
    { id: '214', type: 'Лекционная', capacity: 80 }, { id: '118', type: 'Лекционная', capacity: 120 },
    { id: '301', type: 'Лекционная', capacity: 60 }, { id: '305', type: 'Лекционная', capacity: 40 },
    { id: '220', type: 'Лекционная', capacity: 50 }, { id: 'к.412', type: 'Комп. класс', capacity: 25 },
    { id: 'к.413', type: 'Комп. класс', capacity: 25 }, { id: 'лаб.2', type: 'Лаборатория', capacity: 20 },
  ]

  const majors = [
    { id: 'm1', code: '09.02.07', name: 'Информационные системы и программирование' },
    { id: 'm2', code: '09.02.03', name: 'Программирование в компьютерных системах' },
    { id: 'm3', code: '38.02.01', name: 'Экономика и бухгалтерский учёт' },
    { id: 'm4', code: '40.02.04', name: 'Юриспруденция' },
  ]

  // group id doubles as display name (see data schema: «id / name: string»)
  const groups = [
    { id: 'ИС-31', majorId: 'm1', course: 3 },
    { id: 'ИС-32', majorId: 'm1', course: 3 },
    { id: 'ИС-21', majorId: 'm1', course: 2 },
    { id: 'ИС-11', majorId: 'm1', course: 1 },
    { id: 'ПКС-21', majorId: 'm2', course: 2 },
    { id: 'ПКС-22', majorId: 'm2', course: 2 },
    { id: 'ЭК-11', majorId: 'm3', course: 1 },
  ]

  // [group, discipline, kind, teacherId|null, roomId, placed[[day,slot]...], extraPoolPairs, opts]
  const SPEC = [
    ['ИС-31', 'Матанализ', 'lec', 't1', '214', [[0, 0]], 0],
    ['ИС-31', 'Матанализ', 'prac', 't1', '214', [[0, 1]], 1],
    ['ИС-31', 'Программирование', 'prac', 't2', 'к.412', [[1, 0]], 1],
    ['ИС-31', 'Программирование', 'lec', 't2', '214', [[4, 3]], 0],
    ['ИС-31', 'Физика', 'lec', 't3', '118', [[3, 0]], 0],
    ['ИС-31', 'История', 'lec', 't4', '301', [[1, 1]], 0],
    ['ИС-31', 'БЖД', 'lec', 't5', '220', [[2, 1]], 0, { pin: true }],
    ['ИС-31', 'Англ. язык', 'prac', 't6', '305', [[4, 1]], 1],
    ['ИС-31', 'Базы данных', 'prac', 't2', 'к.413', [], 2],
    ['ИС-32', 'История', 'lec', 't4', '301', [[1, 1]], 0],
    ['ИС-32', 'Матанализ', 'lec', 't1', '214', [[1, 0]], 1],
    ['ИС-32', 'Философия', 'lec', null, '305', [[3, 2]], 0, { orphanTeacher: 't9' }],
    ['ИС-32', 'Программирование', 'prac', 't2', 'к.412', [[2, 3]], 1],
    ['ИС-32', 'Физика', 'lec', 't3', '118', [[3, 1]], 0],
    ['ИС-32', 'Англ. язык', 'prac', 't6', '305', [[0, 2]], 1],
    ['ПКС-21', 'Веб-разработка', 'prac', 't7', 'к.413', [[0, 0], [2, 0]], 1],
    ['ПКС-21', 'ОС и сети', 'lec', 't8', '220', [[1, 2]], 1],
    ['ПКС-21', 'Матанализ', 'lec', 't1', '118', [[3, 2]], 0],
    ['ПКС-21', 'История', 'lec', 't4', '301', [[4, 0]], 0],
    ['ПКС-21', 'Базы данных', 'prac', 't10', 'к.412', [], 2],
    ['ПКС-22', 'Веб-разработка', 'prac', 't7', 'к.413', [[0, 1], [2, 1]], 0],
    ['ПКС-22', 'ОС и сети', 'lec', 't8', '220', [[4, 2]], 1],
    ['ПКС-22', 'Англ. язык', 'prac', 't6', '305', [[1, 3]], 1],
    ['ПКС-22', 'Физика', 'lec', 't3', '118', [[2, 3]], 0],
    ['ПКС-22', 'История', 'lec', 't4', '301', [], 1],
    ['ЭК-11', 'Статистика', 'lec', 't8', '214', [[0, 0]], 0],
    ['ЭК-11', 'Экономика', 'lec', 't9', '301', [[0, 3], [2, 2]], 1],
    ['ЭК-11', 'Матанализ', 'prac', 't1', '305', [[1, 2]], 1],
    ['ЭК-11', 'Англ. язык', 'prac', 't6', '305', [[3, 3]], 0],
    ['ЭК-11', 'Информатика', 'prac', 't10', 'к.412', [], 2],
  ]

  // demo lesson themes and study questions per group|discipline|kind
  const THEMES = {
    'ИС-31|Матанализ|lec': ['Тема 4. Пределы и непрерывность', 'Предел функции в точке. Односторонние пределы'],
    'ИС-31|Матанализ|prac': ['Тема 4. Пределы и непрерывность', 'Вычисление пределов: раскрытие неопределённостей'],
    'ИС-31|Программирование|prac': ['Тема 2. Структуры данных', 'Списки, словари, множества: типовые операции'],
    'ИС-31|Программирование|lec': ['Тема 2. Структуры данных', 'Абстрактные типы данных. Сложность операций'],
    'ИС-31|Физика|lec': ['Тема 3. Динамика материальной точки', 'Законы Ньютона. Силы в механике'],
    'ИС-31|БЖД|lec': ['Тема 1. Основы безопасности', 'Классификация опасных и вредных факторов'],
    'ИС-32|Матанализ|lec': ['Тема 4. Пределы и непрерывность', 'Предел функции в точке. Односторонние пределы'],
    'ПКС-21|Веб-разработка|prac': ['Тема 5. Клиент-серверное взаимодействие', 'REST API: методы, коды ответов, форматы'],
    'ПКС-21|ОС и сети|lec': ['Тема 3. Процессы и потоки', 'Планирование процессов. Состояния потока'],
    'ЭК-11|Экономика|lec': ['Тема 1. Спрос и предложение', 'Рыночное равновесие. Эластичность спроса'],
    'ЭК-11|Статистика|lec': ['Тема 2. Ряды распределения', 'Средние величины и показатели вариации'],
  }

  const topicName = (kind) => (kind === 'lec' ? 'Теоретический курс' : 'Практические занятия')

  const disciplines = []
  const assignments = {} // topicId -> { teacherId, pairsPerWeek }
  const lessons = []
  let dN = 0
  let tpN = 0
  let lN = 0
  const discByKey = {}

  SPEC.forEach((row) => {
    const [g, disc, kind, teacherId, roomId, placed, extra] = row
    const opts = row[7] || {}
    const key = g + '|' + disc
    let d = discByKey[key]
    if (!d) {
      d = { id: 'd' + (++dN), name: disc, groupId: g, period: 'fall', isNew: false, topics: [] }
      discByKey[key] = d
      disciplines.push(d)
    }
    const nt = placed.length + extra
    const topic = { id: 'tp' + (++tpN), kind, name: topicName(kind), hours: nt * 32 }
    d.topics.push(topic)
    if (teacherId) assignments[topic.id] = { teacherId, pairsPerWeek: nt }
    const theme = THEMES[g + '|' + disc + '|' + kind]
    const tOwner = teacherId || opts.orphanTeacher
    placed.forEach((pos, i) => {
      lessons.push({
        id: 'l' + (++lN), topicId: topic.id, disciplineId: d.id, groupId: g, teacherId: tOwner,
        roomId, kind, period: 'fall', day: pos[0], slot: pos[1],
        pin: !!opts.pin, manual: false, ni: i + 1, nt,
        topicLabel: theme ? theme[0] : '', question: theme ? theme[1] : '',
      })
    })
    if (teacherId) {
      for (let i = 0; i < extra; i++) {
        lessons.push({
          id: 'l' + (++lN), topicId: topic.id, disciplineId: d.id, groupId: g, teacherId,
          roomId, kind, period: 'fall', day: null, slot: null,
          pin: false, manual: false, ni: placed.length + i + 1, nt,
          topicLabel: theme ? theme[0] : '', question: theme ? theme[1] : '',
        })
      }
    }
  })

  // extra plan-only disciplines: unassigned fall topics + the spring plan
  const extraPlan = [
    ['ИС-21', 'Психология общения', 'fall', [['lec', 'Теоретический курс', 32]]],
    ['ИС-11', 'Русский язык', 'fall', [['prac', 'Практические занятия', 64]]],
    ['ИС-31', 'Теория вероятностей', 'spring', [['lec', 'Теоретический курс', 32], ['prac', 'Практикум', 32]]],
    ['ИС-32', 'ООП', 'spring', [['lec', 'Лекционный раздел', 32], ['prac', 'Лабораторный практикум', 64]]],
    ['ИС-21', 'Дискретная математика', 'spring', [['lec', 'Раздел 1. Основы', 32], ['prac', 'Семинары', 32]]],
    ['ПКС-21', 'Мобильная разработка', 'spring', [['prac', 'Практикум', 64], ['lec', 'Вводный раздел', 32]]],
    ['ПКС-22', 'Тестирование ПО', 'spring', [['lec', 'Теория', 32], ['prac', 'Практикум', 32]]],
    ['ЭК-11', 'Маркетинг', 'spring', [['lec', 'Теоретический курс', 32]]],
  ]
  extraPlan.forEach(([g, name, period, topics]) => {
    disciplines.push({
      id: 'd' + (++dN), name, groupId: g, period, isNew: false,
      topics: topics.map(([kind, tn, hours]) => ({ id: 'tp' + (++tpN), kind, name: tn, hours })),
    })
  })

  return {
    periods, semesters, topicTypes, teachers, rooms, majors, groups, disciplines, assignments, lessons,
    counters: { d: dN, tp: tpN, l: lN },
  }
}
