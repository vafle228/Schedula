<script setup>
/**
 * Настройки → «Праздничные и нерабочие дни».
 *
 * Primary source is the Russian production calendar (calendar.kuzyak.in): the
 * «Обновить из календаря» action fetches the year's holidays and folds them
 * onto the current semester's grid. The manual editor is the fallback — add or
 * drop individual days by date.
 *
 * Holidays are stored on the semester as `"w-d"` grid cells (the format the
 * grid, conflict engine and generator already understand); this panel only
 * decides how that list gets filled. Everything is bounded to the semester's
 * own interval (see `dateToCell` / `periodEnd`).
 */
import { computed, reactive, ref } from 'vue'
import { store } from '../../store/index.js'
import { fetchYearCalendar, CalendarError, CALENDAR_BASE } from '../../api/calendar.js'
import {
  periodYears, holidaysToCells, dateToCell, describeCell, cellCmp, cellToISO,
} from '../../utils/holidays.js'

const period = computed(() => store.state.period)
const cfg = computed(() => store.state.periods[period.value])
const seasonLabel = computed(() => (period.value === 'fall' ? 'Осенний семестр' : 'Весенний семестр'))
const source = computed(() => (cfg.value && cfg.value.holidaySource) || 'api')
const hasStart = computed(() => !!(cfg.value && cfg.value.startDate))
const host = CALENDAR_BASE.replace(/^https?:\/\//, '')

const cells = computed(() => (cfg.value && cfg.value.holidays ? [...cfg.value.holidays].sort(cellCmp) : []))

// Day-offs grouped by month — keeps a long list readable instead of a wall of chips.
const months = computed(() => {
  const groups = []
  const byKey = new Map()
  for (const c of cells.value) {
    const d = describeCell(cfg.value, c)
    let g = byKey.get(d.ym)
    if (!g) { g = { key: d.ym, label: d.monthLabel, days: [] }; byKey.set(d.ym, g); groups.push(g) }
    g.days.push({ ...d, name: names.value[c] || '' })
  }
  return groups
})

// Date-input bounds so a manual pick can only land inside the semester.
const range = computed(() => {
  const c = cfg.value
  if (!c || !c.startDate) return { min: '', max: '' }
  return { min: c.startDate, max: cellToISO(c, (c.weeksCount || 16) + '-6') }
})

const ui = reactive({ busy: false, msg: '', err: '', newDate: '' })
// Holiday names from the last sync — transient, used only for day tooltips.
const names = ref({})

function clearMsg() { ui.msg = ''; ui.err = '' }

async function setSource(s) {
  if (s === source.value) return
  clearMsg()
  await store.savePeriod(period.value, { holidaySource: s })
}

async function saveCells(next, patch = {}) {
  await store.savePeriod(period.value, { holidays: [...next].sort(cellCmp), ...patch })
}

async function sync() {
  clearMsg()
  const years = periodYears(cfg.value)
  if (!years.length) { ui.err = 'Не задана дата начала семестра — укажите её в учебном году.'; return }
  ui.busy = true
  try {
    const holidays = []
    let shortN = 0
    for (const y of years) {
      const data = await fetchYearCalendar(y)
      holidays.push(...data.holidays)
      shortN += data.shortDays.filter((s) => dateToCell(cfg.value, s.date)).length
    }
    const { cells: next, named } = holidaysToCells(cfg.value, holidays)
    const m = {}
    named.forEach((n) => { m[n.cell] = n.name })
    names.value = m
    await saveCells(next, { holidaySource: 'api' })
    ui.msg = `Отмечено ${next.length} ${plural(next.length)} за ${years.join(', ')}.`
      + (shortN > 0 ? ` Предпраздничных сокращённых дней: ${shortN} (в сетке не учитываются).` : '')
  } catch (e) {
    ui.err = (e instanceof CalendarError ? e.message : 'Не удалось обновить календарь.')
      + ' Можно задать дни вручную.'
  } finally {
    ui.busy = false
  }
}

async function addManual() {
  clearMsg()
  if (!ui.newDate) return
  const cell = dateToCell(cfg.value, ui.newDate)
  if (!cell) { ui.err = 'Дата вне учебного семестра или приходится на неучебный день недели.'; return }
  if (cells.value.includes(cell)) { ui.err = 'Этот день уже отмечен как нерабочий.'; return }
  await saveCells([...cells.value, cell], { holidaySource: 'manual' })
  ui.newDate = ''
}

async function removeCell(cell) {
  clearMsg()
  await saveCells(cells.value.filter((c) => c !== cell))
}

async function clearAll() {
  clearMsg()
  if (!cells.value.length) return
  await saveCells([])
  names.value = {}
}

function plural(n) {
  const a = Math.abs(n) % 100
  const b = a % 10
  if (a > 10 && a < 20) return 'нерабочих дней'
  if (b > 1 && b < 5) return 'нерабочих дня'
  if (b === 1) return 'нерабочий день'
  return 'нерабочих дней'
}
</script>

<template>
  <div class="panel sect">
    <div class="sect-head">
      <span class="sect-title">Праздничные и нерабочие дни</span>
      <span class="sect-sub">
        Нерабочие дни выпадают из сетки: занятия на них не ставятся, а уже размещённые помечаются
        как конфликт. Основной источник — производственный календарь РФ; вручную можно поправить
        любой день. Настройки относятся к сезону «{{ seasonLabel }}».
      </span>
    </div>

    <!-- source toggle -->
    <div class="src-row">
      <div class="seg">
        <button :class="{ on: source === 'api' }" @click="setSource('api')">Производственный календарь</button>
        <button :class="{ on: source === 'manual' }" @click="setSource('manual')">Вручную</button>
      </div>
      <span class="count mono">{{ cells.length }} {{ plural(cells.length) }}</span>
      <span class="sp"></span>
      <button v-if="cells.length" class="link-btn danger" @click="clearAll">Очистить все</button>
    </div>

    <div v-if="!hasStart" class="warn">
      Для этого семестра не задана дата начала — календарь не с чем сопоставить. Укажите даты
      учебного года выше.
    </div>

    <!-- API source -->
    <div v-if="source === 'api' && hasStart" class="api-line">
      <button class="btn-primary" :disabled="ui.busy" @click="sync">
        {{ ui.busy ? 'Загружаем…' : '↻ Обновить из календаря' }}
      </button>
      <span class="src-host mono">источник: {{ host }}</span>
    </div>

    <!-- manual add -->
    <div v-if="source === 'manual' && hasStart" class="man-add">
      <span class="lbl">Добавить нерабочий день</span>
      <div class="man-ctl">
        <input
          v-model="ui.newDate"
          type="date"
          class="input mono"
          :min="range.min"
          :max="range.max"
          @keyup.enter="addManual"
        >
        <button class="btn-primary" :disabled="!ui.newDate" @click="addManual">Добавить</button>
      </div>
    </div>

    <!-- day-offs, grouped by month -->
    <div v-if="hasStart && months.length" class="months">
      <div v-for="g in months" :key="g.key" class="mgroup">
        <span class="mlabel">{{ g.label }}</span>
        <div class="days">
          <span v-for="day in g.days" :key="day.cell" class="day" :title="day.name || 'Нерабочий день'">
            <span class="day-num mono">{{ day.dom }}</span>
            <span class="day-wd">{{ day.wd }}</span>
            <button class="day-x" title="Убрать" @click="removeCell(day.cell)">✕</button>
          </span>
        </div>
      </div>
    </div>
    <div v-else-if="hasStart" class="empty-note">
      Нерабочих дней пока нет.
      {{ source === 'api' ? 'Нажмите «Обновить из календаря».' : 'Добавьте день по дате выше.' }}
    </div>

    <div v-if="ui.msg" class="ok-msg">{{ ui.msg }}</div>
    <div v-if="ui.err" class="err-msg">{{ ui.err }}</div>
  </div>
</template>

<style scoped>
.sect { padding: 16px 18px; gap: 12px; overflow: visible; }
.sect-head { display: flex; flex-direction: column; gap: 2px; }
.sect-title { font-size: 13.5px; font-weight: 600; }
.sect-sub { font-size: 11.5px; color: var(--muted); line-height: 1.5; }
.sp { flex: 1; }

.src-row { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.count { font: 500 11px var(--mono); color: var(--sub); }
.link-btn { border: none; background: transparent; color: var(--blue); font: 500 11.5px var(--sans); cursor: pointer; padding: 2px 3px; }
.link-btn:hover { text-decoration: underline; }
.link-btn.danger { color: var(--red); }

.warn {
  font-size: 11.5px;
  color: var(--amber-dark);
  background: rgba(176, 124, 31, 0.07);
  border: 1px solid rgba(176, 124, 31, 0.22);
  border-radius: var(--r-md);
  padding: 8px 10px;
  line-height: 1.5;
}

.api-line { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.src-host { font: 400 11px var(--mono); color: var(--faint); }

.man-add { display: flex; flex-direction: column; gap: 5px; }
.man-ctl { display: flex; align-items: center; gap: 8px; }
.lbl { font-size: 11px; font-weight: 600; color: var(--muted); }

/* day-offs grouped by month */
.months {
  display: flex;
  flex-direction: column;
  gap: 4px;
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: var(--r-md);
  padding: 6px 8px;
  background: var(--hover);
}
.mgroup {
  display: grid;
  grid-template-columns: 116px 1fr;
  gap: 10px;
  align-items: baseline;
  padding: 5px 2px;
}
.mgroup + .mgroup { border-top: 1px solid rgba(0, 0, 0, 0.05); }
.mlabel { font-size: 12px; font-weight: 600; color: var(--sub); }
.days { display: flex; flex-wrap: wrap; gap: 6px; }
.day {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  background: var(--panel);
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: var(--r-md);
  padding: 3px 4px 3px 8px;
}
.day-num { font: 600 12px var(--mono); color: var(--fg); }
.day-wd { font-size: 10.5px; color: var(--faint); }
.day-x {
  border: none;
  background: transparent;
  color: var(--faint);
  cursor: pointer;
  font-size: 10px;
  line-height: 1;
  width: 16px;
  height: 16px;
  border-radius: 50%;
}
.day-x:hover { background: rgba(194, 69, 54, 0.12); color: var(--red); }

.empty-note { font-size: 11.5px; color: var(--faint); }
.ok-msg { font-size: 11.5px; color: var(--green-dark); }
.err-msg { font-size: 11.5px; color: var(--red); }
</style>
