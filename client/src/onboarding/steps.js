/**
 * The guided-tour script.
 *
 * Steps are data, not code: each one names the route it lives on, the CSS
 * selector to spotlight (or a list of selectors tried in priority order), and
 * optionally a `before()` hook that puts the view into the right state first —
 * switching a tab, picking a season. Adding or reordering a step means editing
 * this array and nothing else.
 *
 * The order deliberately follows the *data dependencies* rather than the
 * sidebar: a discipline needs a group, a group needs a specialty, and the
 * schedule grid only shows what «Распределение» has assigned. That is the
 * opposite of where a new user lands (`/` redirects to `/distribution`), which
 * is precisely why the tour exists.
 *
 * `available()` lets a step opt out when its UI cannot render — «Расписание»
 * replaces the whole workspace with an empty state when the period has no
 * assignments, so the pool and grid simply do not exist in the DOM.
 */
import { store } from '../store/index.js'
import { dirUi } from '../views/directory/useDirectory.js'

/** True when «Расписание» renders its grid rather than the empty state. */
const scheduleHasWork = () => store.enriched.value.length > 0

const openDirTab = (sec) => () => {
  dirUi.sec = sec
}

export const STEPS = [
  {
    id: 'nav',
    chapter: 'Обзор',
    route: '/distribution',
    target: '.rail',
    placement: 'right',
    title: 'Четыре раздела',
    text: 'Schedula собирает расписание за четыре шага. «Настройки» задают календарь и сетку звонков, «Справочники» — преподавателей, группы и аудитории, «Распределение» раздаёт нагрузку, «Расписание» раскладывает её по дням и парам. Пойдём по этому порядку — он совпадает с тем, как данные зависят друг от друга.',
  },

  /* ---------- Настройки ---------- */
  {
    id: 'year',
    chapter: 'Настройки',
    route: '/settings',
    target: '.col > .sect:nth-child(1)',
    placement: 'right',
    title: 'Учебный год',
    text: 'Год — это пара семестров, осень и весна. Активным может быть только один: к нему привязаны группы, дисциплины и занятия. Кнопка ⇄ переносит учебный план в следующий год, чтобы не заводить его заново.',
  },
  {
    id: 'bells',
    chapter: 'Настройки',
    route: '/settings',
    target: '.slot-table',
    placement: 'top',
    title: 'Академический час и сетка звонков',
    text: 'Сетка звонков задаёт, сколько пар в дне и когда они начинаются. Пока здесь нет ни одного слота, сетка расписания будет пустой — раскладывать занятия просто некуда.',
  },
  {
    id: 'holidays',
    chapter: 'Настройки',
    route: '/settings',
    target: '.src-row',
    placement: 'top',
    title: 'Нерабочие дни',
    text: 'Праздники можно подтянуть из производственного календаря или отметить вручную. Занятие, попавшее на такой день, будет помечено как конфликт.',
  },

  /* ---------- Справочники ---------- */
  {
    id: 'dir-tabs',
    chapter: 'Справочники',
    route: '/directory',
    target: '.head .seg',
    placement: 'bottom',
    title: 'Мастер-данные',
    text: 'Четыре справочника, которые меняются нечасто. Всё остальное в программе ссылается именно на них, поэтому заполнять стоит отсюда.',
  },
  {
    id: 'dir-majors',
    chapter: 'Справочники',
    route: '/directory',
    target: '.panel.side',
    placement: 'right',
    before: openDirTab('majors'),
    title: 'Специальности и группы',
    text: 'Группа принадлежит специальности и курсу. Созданные здесь группы сразу видны в «Распределении» и «Расписании» — без единой группы список дисциплин будет пустым.',
  },
  {
    id: 'dir-major-detail',
    chapter: 'Справочники',
    route: '/directory',
    target: '.panel.card',
    placement: 'left',
    before: openDirTab('majors'),
    title: 'Карточка специальности',
    text: 'Справа — карточка выбранной специальности: код и название редактируются прямо в полях. Ниже, в «Группы специальности», группы и создаются — с курсом, куратором и учебными днями. Группа привязана к специальности и текущему учебному году, поэтому при переносе плана в новый год (⇄) группы заводятся заново.',
  },
  {
    id: 'dir-teachers',
    chapter: 'Справочники',
    route: '/directory',
    // the detail card exists only once a teacher is selected — on a fresh
    // install there are none, so fall back to the list panel
    target: ['.panel.card', '.panel.side'],
    placement: 'left',
    before: openDirTab('teachers'),
    title: 'Преподаватели',
    text: 'У каждого преподавателя — норма нагрузки (верхняя граница в «Распределении»), еженедельная доступность и периоды отсутствия. Клик по ячейке доступности переключает её: свободно → недоступно → нежелательно. Расписание учитывает это при проверке конфликтов.',
  },
  {
    id: 'dir-rooms',
    chapter: 'Справочники',
    route: '/directory',
    target: '.rooms-panel',
    placement: 'auto',
    before: openDirTab('rooms'),
    title: 'Аудитории',
    text: 'Аудитории с типом. Две пары в одной аудитории в одно время — жёсткий конфликт, программа его подсветит.',
  },
  {
    id: 'dir-types',
    chapter: 'Справочники',
    route: '/directory',
    target: '.types-panel',
    placement: 'auto',
    before: openDirTab('types'),
    title: 'Типы занятий',
    text: 'Лекция, практика, лабораторная и так далее — с цветом и длительностью в академических часах. Длительность важна: двухчасовое занятие не встанет в одночасовой слот.',
  },

  /* ---------- Распределение ---------- */
  {
    id: 'dist-pool',
    chapter: 'Распределение',
    route: '/distribution',
    target: '.panel.pool',
    placement: 'right',
    title: 'Учебный план',
    text: 'Слева — дисциплины, сгруппированные по группам. Дисциплина раскрывается в блоки нагрузки: вид занятия плюс количество академических часов. Именно блок, а не дисциплина целиком, назначается преподавателю.',
  },
  {
    id: 'dist-create',
    chapter: 'Распределение',
    route: '/distribution',
    target: '.new-disc',
    placement: 'bottom',
    title: 'Новая дисциплина',
    text: 'Здесь создаётся дисциплина (или по Ctrl + N). Курс и семестр подставятся из выбранной группы — останется добавить блоки нагрузки.',
  },
  {
    id: 'dist-assign',
    chapter: 'Распределение',
    route: '/distribution',
    target: '.panel.teachers',
    placement: 'left',
    title: 'Назначение нагрузки',
    text: 'Три способа назначить преподавателя: перетащить блок (или всю дисциплину) на строку справа, нажать ＋ на блоке, либо кликнуть по блоку и выбрать из списка. Полоса показывает нагрузку относительно нормы. Клик по имени снимает назначение.',
  },
  {
    id: 'dist-progress',
    chapter: 'Распределение',
    route: '/distribution',
    target: '.progress',
    placement: 'bottom',
    title: 'Готовность плана',
    text: 'Счётчик показывает, сколько блоков уже закреплено за преподавателями. В сетку расписания попадают только назначенные блоки, так что до перехода к расписанию его стоит довести до конца.',
  },

  /* ---------- Расписание ---------- */
  {
    id: 'sched-pool',
    chapter: 'Расписание',
    route: '/schedule',
    target: '.pool',
    placement: 'right',
    available: scheduleHasWork,
    title: 'Содержание курсов',
    text: 'Слева — занятия, заведённые из назначений. Кнопка «+ занятие» добавляет тему с учебным вопросом; новое занятие попадает в пул и ждёт своего слота.',
  },
  {
    id: 'sched-grid',
    chapter: 'Расписание',
    route: '/schedule',
    target: '.grid-panel',
    placement: 'left',
    available: scheduleHasWork,
    title: 'Сетка недели',
    text: 'Перетащите карточку из пула в ячейку «день × пара». Пока вы тянете, ячейки подсвечиваются: зелёная — свободна, янтарная — нарушает пожелание преподавателя, красная — жёсткий конфликт, штриховка — занятие не помещается в слот. Клик по карточке открывает её, Del возвращает в пул.',
  },
  {
    id: 'sched-gen',
    chapter: 'Расписание',
    route: '/schedule',
    target: '.head > .btn-primary',
    placement: 'bottom',
    title: 'Автоматическая раскладка',
    text: '«⟳ Разложить» расставляет пул сама. Можно пересобрать всё расписание или только доразместить оставшееся. Результат сначала показывается как черновик — «Принять результат» закрепляет его, «Откатить всё» отменяет.',
  },
  {
    id: 'sched-problems',
    chapter: 'Расписание',
    route: '/schedule',
    target: '.prob-chip',
    placement: 'bottom',
    title: 'Проблемы',
    text: 'Здесь собраны все конфликты: преподаватель или группа в двух местах сразу, занятая аудитория, занятие в праздник, нарушение методического дня. Отдельно помечаются «осиротевшие» пары — те, чьё назначение убрали из плана. Программа никогда не удаляет их молча, только помечает.',
  },
  {
    id: 'export',
    chapter: 'Расписание',
    route: '/schedule',
    target: '.head > button.btn',
    placement: 'bottom',
    title: 'Экспорт в Excel',
    text: 'Готовое расписание выгружается по листу на учебный день. В «Распределении» такая же кнопка выгружает учебный план по государственному шаблону — с формулами, так что файл остаётся «живым».',
  },

  /* ---------- финал ---------- */
  {
    id: 'done',
    chapter: 'Готово',
    route: null,
    target: null,
    title: 'Это всё',
    text: 'Дальше — по порядку: настройте год и сетку звонков, заполните справочники, раздайте нагрузку и разложите расписание. Обучение можно пройти заново в любой момент — кнопка «Обучение» в левом меню.',
  },
]
