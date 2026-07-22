<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { store } from '../../store/index.js'
import { ALL_DAYS } from '../../utils/kinds.js'
import InfoDot from '../../components/InfoDot.vue'
import ScheduleGrid from './ScheduleGrid.vue'
import PoolPanel from './PoolPanel.vue'
import GenerationPanel from './GenerationPanel.vue'
import LessonFormModal from './LessonFormModal.vue'
import ConstraintsModal from './ConstraintsModal.vue'
import RoomsModal from './RoomsModal.vue'
import ScheduleExportModal from './ScheduleExportModal.vue'
import {
  ui, enriched, visible, analysis, dayIdxs, slotsN, flash,
  entVal, entOptions, entStep, removeLessons, pinLessons,
  openLf, closeAllModals,
  weekBtns, weekRangeLabel, weekPagesN, selectWeek, weekPagePrev, weekPageNext,
} from './useSchedule.js'

const gridRef = ref(null)
const poolRef = ref(null)

const periodBtns = [
  { k: 'fall', label: 'Осень' },
  { k: 'spring', label: 'Весна' },
]
const viewBtns = [
  { k: 'group', label: 'Группы' },
  { k: 'teacher', label: 'Преподаватели' },
  { k: 'room', label: 'Аудитории' },
]

/* Problems shown in the header popup (Итерация 8): conflicts, orphans,
   broken wishes — click jumps to the lesson in the grid. */
const problems = computed(() => {
  const out = []
  enriched.value.forEach((l) => {
    const issues = analysis.value.byId[l.id]
    if (!issues) return
    const isHard = issues.some((x) => x.sev === 'hard')
    out.push({
      l,
      hard: isHard,
      title: l.disc + ', ' + l.g,
      accent: isHard ? '#C24536' : '#B07C1F',
      border: isHard ? 'rgba(194,69,54,0.3)' : 'rgba(176,124,31,0.35)',
      desc: issues.map((x) => x.text).join('; ') + ' · '
        + (l.d != null ? 'Н' + l.w + ' ' + ALL_DAYS[l.d] + ' ' + (l.s + 1) + ' пара' : 'в пуле'),
    })
  })
  out.sort((a, b) => (a.hard ? 0 : 1) - (b.hard ? 0 : 1))
  return out
})
const probN = computed(() => problems.value.length)

function goProblem(item) {
  const l = item.l
  ui.view = 'group'
  ui.ent.group = l.g
  if (l.w != null) selectWeek(l.w)
  ui.cursor = l.d != null ? { d: l.d, s: l.s } : null
  ui.sel = [l.id]
  ui.prob = false
  flash(l.id)
}

const isEmpty = computed(() => enriched.value.length === 0)
const emptyTitle = computed(() => (store.state.period === 'spring'
  ? 'На весенний период нет назначений'
  : 'На осенний период нет назначений'))

const entPlaced = computed(() => visible.value.filter((l) => l.d != null).length)
const entMeta = computed(() => (ui.view === 'group'
  ? entPlaced.value + ' / ' + visible.value.length + ' пар'
  : entPlaced.value + ' пар в неделю'))

const curTeacher = computed(() => (ui.view === 'teacher' ? store.teacherById(ui.ent.teacher) : null))
const entWarn = computed(() => !!(curTeacher.value && !curTeacher.value.c))

const canUndo = computed(() => store.state.schedUndo.length > 0)
const canRedo = computed(() => store.state.schedRedo.length > 0)

function pickView(k) {
  ui.view = k
  ui.cursor = null
  ui.sel = []
}

/* Switching season: reset week/selection, close the lesson card, cancel any
   placement mode and active drag; pool/problems/hours recompute by period. */
function pickSeason(k) {
  if (store.state.period === k) return
  store.setPeriod(k)
  ui.sel = []
  ui.cursor = null
  ui.dragId = null
  ui.week = 1
  ui.weekPage = 0
  ui.lf = null
  ui.prob = false
  if (ui.gen && ui.gen.phase !== 'run') ui.gen = null
  if (ui.ex) ui.ex = null
}

function openGen() {
  ui.gen = { phase: 'prep', mode: 'rebuild' }
  ui.sel = []
}

function openExport() {
  ui.ex = { step: 'config', view: 'group', scope: 'all' }
}

function ovUndo() { ui.ov = false; store.schedUndoAct() }
function ovRedo() { ui.ov = false; store.schedRedoAct() }
function ovPrint() { ui.ov = false; window.print() }

/* ---------- keyboard ---------- */

function onKey(e) {
  const tag = (e.target.tagName || '').toLowerCase()
  const inInput = tag === 'input' || tag === 'select' || tag === 'textarea'
  if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'z') {
    e.preventDefault()
    if (e.shiftKey) store.schedRedoAct()
    else store.schedUndoAct()
    return
  }
  if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'y') {
    e.preventDefault()
    store.schedRedoAct()
    return
  }
  if (e.key === 'Escape') { closeAllModals(); return }
  if (inInput) return
  if (e.key === '/') {
    e.preventDefault()
    setTimeout(() => poolRef.value && poolRef.value.focusSearch(), 30)
    return
  }
  if (e.key === 'PageUp') { e.preventDefault(); entStep(-1); return }
  if (e.key === 'PageDown') { e.preventDefault(); entStep(1); return }
  const arrows = { ArrowLeft: -1, ArrowRight: 1, ArrowUp: 0, ArrowDown: 0 }
  if (e.key in arrows) {
    e.preventDefault()
    const days = dayIdxs.value
    const c = ui.cursor || { d: days[0] || 0, s: 0 }
    let di = Math.max(0, days.indexOf(c.d))
    let s = c.s
    if (e.key === 'ArrowLeft') di = Math.max(0, di - 1)
    if (e.key === 'ArrowRight') di = Math.min(days.length - 1, di + 1)
    if (e.key === 'ArrowUp') s = Math.max(0, s - 1)
    if (e.key === 'ArrowDown') s = Math.min(slotsN.value - 1, s + 1)
    ui.cursor = { d: days[di], s }
    if (gridRef.value) gridRef.value.focus()
    return
  }
  const cur = ui.cursor
  const cellLessons = cur ? visible.value.filter((l) => l.w === ui.week && l.d === cur.d && l.s === cur.s) : []
  if (e.key === 'Enter') {
    e.preventDefault()
    if (cellLessons.length) openLf(null, cellLessons[0].id)
    return
  }
  if (e.key.toLowerCase() === 'p' || e.key.toLowerCase() === 'з') {
    pinLessons(cellLessons.map((l) => l.id))
    return
  }
  if (e.key === 'Delete' || e.key === 'Backspace') {
    removeLessons(cellLessons.map((l) => l.id))
  }
}

onMounted(() => document.addEventListener('keydown', onKey))
onUnmounted(() => document.removeEventListener('keydown', onKey))
</script>

<template>
  <div class="view">
    <!-- ======= header ======= -->
    <div class="head">
      <span class="head-title" title="Расписание, учебный год 2026/27">Расписание</span>
      <span class="sem-plaque" title="Семестр активного учебного года — переключается прямо здесь">
        <span class="plaque-lead mono">СЕМЕСТР</span>
        <button
          v-for="p in periodBtns"
          :key="p.k"
          class="plaque-btn"
          :class="{ on: store.state.period === p.k }"
          @click="pickSeason(p.k)"
        >{{ p.label }}</button>
      </span>
      <router-link class="year-chip" to="/settings" title="Даты семестров, сетка звонков — в настройках учебного года">
        <span class="plaque-lead mono">УЧ. ГОД</span>
        <span class="yc-year">2026/27</span>
        <span class="yc-act mono">настроить ↗</span>
      </router-link>
      <div class="seg">
        <button
          v-for="v in viewBtns"
          :key="v.k"
          :class="{ on: ui.view === v.k }"
          @click="pickView(v.k)"
        >{{ v.label }}</button>
      </div>
      <div class="sp"></div>
      <div class="prob-wrap">
        <button
          class="prob-chip"
          :class="probN ? 'has' : 'ok'"
          title="Проблемы и конфликты — клик открывает список"
          @click="ui.prob = !ui.prob"
        >{{ probN ? '⚠ Проблемы · ' + probN : '✓ Проблем нет' }}</button>
        <template v-if="ui.prob">
          <div class="prob-backdrop" @click="ui.prob = false"></div>
          <div class="prob-pop">
            <div class="pop-head">
              <span class="pop-title">Проблемы</span>
              <span class="pop-badge" :class="{ ok: probN === 0 }">{{ probN }}</span>
            </div>
            <div
              v-for="(pr, i) in problems"
              :key="i"
              class="pop-item"
              :style="{ borderColor: pr.border, borderLeftColor: pr.accent }"
              title="Клик — показать место проблемы в сетке"
              @click="goProblem(pr)"
            >
              <div class="pop-item-title" :style="{ color: pr.accent }">{{ pr.title }}</div>
              <div class="pop-item-desc">{{ pr.desc }}</div>
            </div>
            <div v-if="probN === 0" class="pop-empty">✓ Проблем нет</div>
          </div>
        </template>
      </div>
      <button class="btn" title="Выгрузить расписание в Excel" @click="openExport">Экспорт…</button>
      <button class="btn-primary" title="Разложить черновик расписания по неделям" @click="openGen">⟳ Разложить</button>
      <div class="ov-wrap">
        <button
          class="btn ov-btn"
          :style="{ background: ui.ov ? '#F2F0EB' : '' }"
          title="Ещё: отмена, печать, настройки периода"
          @click="ui.ov = !ui.ov"
        >⋯</button>
        <template v-if="ui.ov">
          <div class="ov-backdrop" @click="ui.ov = false"></div>
          <div class="ov-menu">
            <button
              class="ov-item"
              :style="{ color: canUndo ? '#1F1E1B' : '#C9C5BB', cursor: canUndo ? 'pointer' : 'not-allowed' }"
              title="Отменить (Ctrl+Z)"
              @click="ovUndo"
            >↶ Отменить действие<span class="ov-kbd mono">Ctrl+Z</span></button>
            <button
              class="ov-item"
              :style="{ color: canRedo ? '#1F1E1B' : '#C9C5BB', cursor: canRedo ? 'pointer' : 'not-allowed' }"
              title="Повторить (Ctrl+Shift+Z)"
              @click="ovRedo"
            >↷ Повторить действие<span class="ov-kbd mono">Ctrl+⇧+Z</span></button>
            <div class="ov-div"></div>
            <button class="ov-item" title="Печать листа сетки" @click="ovPrint">Печать сетки</button>
            <router-link class="ov-item ov-link" to="/settings" @click="ui.ov = false">
              Настройки периода<span class="ov-kbd mono">раздел →</span>
            </router-link>
          </div>
        </template>
      </div>
    </div>

    <!-- ======= empty period ======= -->
    <div v-if="isEmpty" class="empty">
      <span class="empty-circle">∅</span>
      <span class="empty-title">{{ emptyTitle }}</span>
      <span class="empty-sub">
        В сетку попадают только дисциплины, назначенные преподавателям.
        Сделайте назначения на этот период в модуле «Распределение».
      </span>
      <router-link class="empty-link" to="/distribution">Перейти к распределению →</router-link>
    </div>

    <!-- ======= workspace ======= -->
    <div v-else class="work">
      <PoolPanel ref="poolRef" />
      <div class="panel grid-panel">
        <div class="grid-head">
          <button class="nav-btn" title="Предыдущая (PgUp)" @click="entStep(-1)">‹</button>
          <select v-model="entVal" class="ent-select">
            <option v-for="o in entOptions" :key="o.v" :value="o.v">{{ o.label }}</option>
          </select>
          <button class="nav-btn" title="Следующая (PgDn)" @click="entStep(1)">›</button>
          <span class="ent-meta mono">{{ entMeta }}</span>
          <InfoDot tip="Занятие заводится слева в «Содержании курсов» (+ занятие) и перетаскивается на слот. Клик по карточке — карточка занятия. P — закрепить, Del — снять в пул, / — поиск, Ctrl+Z — отмена." />
          <span v-if="entWarn" class="ent-warn">доступность не задана — считается полностью доступным</span>
          <span class="sp"></span>
          <span class="week-lead mono">НЕДЕЛЯ</span>
          <div class="week-pager">
            <button class="wk-arrow" :disabled="ui.weekPage === 0" title="Предыдущие недели" @click="weekPagePrev">‹</button>
            <button
              v-for="w in weekBtns"
              :key="w.n"
              class="wk-btn mono"
              :class="{ on: w.on, hol: w.hol }"
              :title="'Неделя ' + w.n"
              @click="selectWeek(w.n)"
            >{{ w.n }}{{ w.hol ? '⚑' : '' }}</button>
            <button class="wk-arrow" :disabled="ui.weekPage >= weekPagesN - 1" title="Следующие недели" @click="weekPageNext">›</button>
            <span class="wk-range mono">{{ weekRangeLabel }}</span>
          </div>
        </div>
        <ScheduleGrid ref="gridRef" />
      </div>
    </div>

    <!-- ======= modals ======= -->
    <GenerationPanel />
    <LessonFormModal />
    <ConstraintsModal />
    <RoomsModal />
    <ScheduleExportModal />
  </div>
</template>

<style scoped>
.view { flex: 1; display: flex; flex-direction: column; min-height: 0; }

.head {
  flex: none;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  padding: 9px 12px;
  background: var(--panel);
  border-bottom: 1px solid rgba(0, 0, 0, 0.08);
}
.head-title {
  font-size: 14px;
  font-weight: 600;
  letter-spacing: -0.01em;
  flex: 0 1 auto;
  min-width: 60px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.sp { flex: 1; }

.sem-plaque {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: #F2F0EB;
  border-radius: 7px;
  padding: 2px 2px 2px 9px;
  flex: none;
}
.plaque-lead { font: 500 9px var(--mono); letter-spacing: 0.07em; color: var(--muted); }
.plaque-btn {
  border: none;
  border-radius: 5px;
  padding: 4px 11px;
  font: 500 12px var(--sans);
  color: var(--muted);
  background: transparent;
  cursor: pointer;
}
.plaque-btn.on { font-weight: 600; color: var(--fg); background: #FFF; box-shadow: 0 1px 2px rgba(0, 0, 0, 0.14); }

.year-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: #F2F0EB;
  border-radius: 7px;
  padding: 5px 10px;
  flex: none;
}
.year-chip:hover { background: #ECEAE4; text-decoration: none; }
.yc-year { font-size: 12px; font-weight: 600; color: var(--fg); }
.yc-act { font: 400 9.5px var(--mono); color: var(--faint); }

.prob-wrap { position: relative; flex: none; }
.prob-chip {
  flex: none;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  border-radius: 8px;
  cursor: pointer;
}
.prob-chip.has {
  border: 1px solid rgba(194, 69, 54, 0.4);
  background: rgba(194, 69, 54, 0.07);
  color: var(--red);
  font: 600 13px var(--sans);
  padding: 9px 15px;
}
.prob-chip.has:hover { background: rgba(194, 69, 54, 0.12); }
.prob-chip.ok {
  border: 1px solid rgba(31, 138, 91, 0.35);
  background: rgba(31, 138, 91, 0.06);
  color: var(--green);
  font: 500 12.5px var(--sans);
  padding: 8px 13px;
}
.prob-chip.ok:hover { background: rgba(31, 138, 91, 0.1); }

.prob-backdrop { position: fixed; inset: 0; z-index: 45; }
.prob-pop {
  position: absolute;
  right: 0;
  top: 40px;
  z-index: 46;
  width: 320px;
  max-height: 60vh;
  overflow: auto;
  background: var(--panel);
  border: 1px solid rgba(0, 0, 0, 0.12);
  border-radius: 10px;
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.16);
  padding: 10px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.pop-head { display: flex; align-items: center; gap: 8px; }
.pop-title { font-size: 13px; font-weight: 600; }
.pop-badge {
  font: 600 10px var(--mono);
  background: rgba(194, 69, 54, 0.12);
  color: #C24536;
  padding: 2px 7px;
  border-radius: 10px;
}
.pop-badge.ok { background: rgba(31, 138, 91, 0.12); color: #166A45; }
.pop-item {
  background: var(--panel);
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-left: 3px solid #C24536;
  border-radius: 8px;
  padding: 9px 11px;
  cursor: pointer;
}
.pop-item:hover { background: #FBFAF8; }
.pop-item-title { font-size: 12px; font-weight: 600; margin-bottom: 2px; }
.pop-item-desc { font-size: 11px; line-height: 1.4; color: var(--sub); }
.pop-empty {
  text-align: center;
  color: #166A45;
  font-size: 12px;
  padding: 14px 8px;
  background: rgba(31, 138, 91, 0.06);
  border-radius: 8px;
}

.ov-wrap { position: relative; flex: none; }
.ov-btn { font: 600 15px var(--sans); width: 31px; height: 31px; padding: 0; }
.ov-backdrop { position: fixed; inset: 0; z-index: 45; }
.ov-menu {
  position: absolute;
  right: 0;
  top: 40px;
  z-index: 46;
  width: 252px;
  background: var(--panel);
  border: 1px solid rgba(0, 0, 0, 0.12);
  border-radius: 9px;
  box-shadow: 0 10px 28px rgba(0, 0, 0, 0.14);
  padding: 4px;
  display: flex;
  flex-direction: column;
}
.ov-item {
  display: flex;
  align-items: center;
  gap: 8px;
  border: none;
  background: transparent;
  padding: 8px 10px;
  border-radius: var(--r-sm);
  cursor: pointer;
  font: 400 12.5px var(--sans);
  color: var(--fg);
  text-align: left;
  width: 100%;
}
.ov-item:hover { background: var(--chip); }
.ov-link { text-decoration: none; }
.ov-link:hover { color: var(--fg); text-decoration: none; }
.ov-kbd { margin-left: auto; font: 400 10.5px var(--mono); color: var(--faint); }
.ov-div { height: 1px; background: rgba(0, 0, 0, 0.08); margin: 4px 6px; }

.empty {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  color: var(--muted);
}
.empty-circle {
  width: 44px;
  height: 44px;
  border: 1.5px dashed rgba(0, 0, 0, 0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
}
.empty-title { font-size: 14px; font-weight: 600; color: #3A382F; }
.empty-sub { font-size: 12.5px; max-width: 360px; text-align: center; line-height: 1.55; }
.empty-link {
  display: inline-flex;
  background: var(--fg);
  color: #FFFFFF;
  padding: 8px 16px;
  border-radius: var(--r-md);
  font-size: 13px;
  font-weight: 500;
}
.empty-link:hover { background: var(--fg-hover); color: #FFFFFF; text-decoration: none; }

.work { flex: 1; display: flex; min-height: 0; padding: 12px; gap: 12px; }
.grid-panel { order: 2; flex: 1; min-width: 0; }
.grid-head {
  flex: none;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 9px 12px;
  border-bottom: 1px solid var(--line-soft);
}
.nav-btn {
  border: 1px solid rgba(0, 0, 0, 0.12);
  background: var(--panel);
  width: 32px;
  height: 32px;
  border-radius: var(--r-md);
  cursor: pointer;
  color: #3A382F;
  font-size: 16px;
  line-height: 1;
}
.ent-select {
  border: 1px solid var(--line-strong);
  background: var(--hover);
  border-radius: var(--r-md);
  padding: 5px 8px;
  font-size: 13px;
  font-weight: 600;
  outline: none;
  max-width: 230px;
}
.ent-meta { font: 400 11.5px var(--mono); color: var(--faint); }
.ent-warn {
  font-size: 11.5px;
  color: var(--amber);
  background: rgba(176, 124, 31, 0.08);
  border: 1px solid rgba(176, 124, 31, 0.3);
  border-radius: 11px;
  padding: 2px 9px;
}

.week-lead { font: 500 9px var(--mono); letter-spacing: 0.06em; color: var(--muted); }
.week-pager { display: inline-flex; align-items: center; gap: 3px; }
.wk-arrow {
  width: 24px;
  height: 26px;
  border: 1px solid rgba(0, 0, 0, 0.12);
  background: var(--panel);
  border-radius: var(--r-sm);
  cursor: pointer;
  color: #3A382F;
  font: 600 13px var(--sans);
}
.wk-arrow:disabled { color: #D5D1C8; cursor: default; }
.wk-btn {
  min-width: 28px;
  height: 26px;
  padding: 0 4px;
  text-align: center;
  font: 500 11px var(--mono);
  color: #3A382F;
  background: transparent;
  border: 1.5px solid rgba(0, 0, 0, 0.12);
  border-radius: var(--r-sm);
  cursor: pointer;
}
.wk-btn.on { border-color: var(--fg); font-weight: 700; }
.wk-btn.hol { color: var(--amber); background: rgba(176, 124, 31, 0.14); }
.wk-range { font: 400 9.5px var(--mono); color: var(--faint); margin-left: 3px; }
</style>
