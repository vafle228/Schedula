<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { store } from '../../store/index.js'
import InfoDot from '../../components/InfoDot.vue'
import ScheduleGrid from './ScheduleGrid.vue'
import PoolPanel from './PoolPanel.vue'
import ProblemsModal from './ProblemsModal.vue'
import GenerationPanel from './GenerationPanel.vue'
import LessonFormModal from './LessonFormModal.vue'
import PlaceDialog from './PlaceDialog.vue'
import ConstraintsModal from './ConstraintsModal.vue'
import RoomsModal from './RoomsModal.vue'
import ScheduleExportModal from './ScheduleExportModal.vue'
import {
  ui, enriched, visible, placedN, totalN, problemsN, dayIdxs, slotsN,
  entVal, entOptions, entStep, place, removeLessons, pinLessons,
  openDlg, openLf, closeAllModals,
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

const progressPct = computed(() => (totalN.value ? Math.round((placedN.value / totalN.value) * 100) : 0))
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
  if (e.key.toLowerCase() === 'n' || e.key.toLowerCase() === 'т') {
    e.preventDefault()
    openLf(ui.cursor)
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
  const cellLessons = cur ? visible.value.filter((l) => l.d === cur.d && l.s === cur.s) : []
  if (e.key === 'Enter') {
    e.preventDefault()
    if (ui.sel.length === 1 && cur && cellLessons.length === 0) { place(ui.sel[0], cur.d, cur.s); return }
    if (cellLessons.length) openDlg(cellLessons[0].id)
    return
  }
  if (e.key.toLowerCase() === 'p' || e.key.toLowerCase() === 'з') {
    pinLessons(ui.sel.length ? ui.sel : cellLessons.map((l) => l.id))
    return
  }
  if (e.key === 'Delete' || e.key === 'Backspace') {
    removeLessons(ui.sel.length ? ui.sel : cellLessons.map((l) => l.id))
  }
}

onMounted(() => document.addEventListener('keydown', onKey))
onUnmounted(() => document.removeEventListener('keydown', onKey))
</script>

<template>
  <div class="view">
    <!-- ======= header ======= -->
    <div class="head">
      <span class="head-title" title="Расписание, учебный год 2026/27">Расписание 2026/27</span>
      <div class="seg">
        <button
          v-for="p in periodBtns"
          :key="p.k"
          :class="{ on: store.state.period === p.k }"
          @click="store.setPeriod(p.k)"
        >{{ p.label }}</button>
      </div>
      <div class="seg">
        <button
          v-for="v in viewBtns"
          :key="v.k"
          :class="{ on: ui.view === v.k }"
          @click="pickView(v.k)"
        >{{ v.label }}</button>
      </div>
      <div class="stat-chip" title="Размещено пар из назначенных на период">
        <span class="mono stat-n">{{ placedN }}/{{ totalN }}</span>
        <span class="stat-bar"><span class="stat-fill" :style="{ width: progressPct + '%' }"></span></span>
      </div>
      <button
        v-if="problemsN > 0"
        class="prob-btn"
        title="Есть проблемы — клик открывает список"
        @click="ui.prob = true"
      >⚠ {{ problemsN }}</button>
      <span
        v-else
        class="prob-ok"
        title="Проблем нет — клик открывает список"
        @click="ui.prob = true"
      >✓</span>
      <div class="sp"></div>
      <button class="btn" title="Выгрузить расписание в Excel" @click="openExport">Экспорт…</button>
      <button class="btn-primary" title="Сгенерировать черновик расписания" @click="openGen">Сгенерировать</button>
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
          <InfoDot tip="Клик по пустой клетке — новое занятие (N). Двойной клик по карточке — тема и учебный вопрос. P — закрепить, Del — снять в пул, / — поиск, Ctrl+Z — отмена." />
          <span v-if="entWarn" class="ent-warn">доступность не задана — считается полностью доступным</span>
          <span class="sp"></span>
          <div v-if="ui.sel.length" class="sel-bar">
            <span class="sel-label">Выбрано: {{ ui.sel.length }}</span>
            <button class="sel-btn" title="Закрепить / открепить (P) — генератор не тронет" @click="pinLessons(ui.sel)">⌖ Закрепить</button>
            <button class="sel-btn" title="Разместить через диалог (Enter)" @click="ui.sel.length && openDlg(ui.sel[0])">Разместить…</button>
            <button class="sel-btn" title="Снять в пул (Del)" @click="removeLessons(ui.sel)">✕ Снять</button>
            <button class="sel-x" title="Esc" @click="ui.sel = []">×</button>
          </div>
        </div>
        <ScheduleGrid ref="gridRef" />
      </div>
    </div>

    <!-- ======= modals ======= -->
    <ProblemsModal />
    <GenerationPanel />
    <LessonFormModal />
    <PlaceDialog />
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

.stat-chip {
  flex: none;
  display: flex;
  align-items: center;
  gap: 7px;
  border: 1px solid rgba(0, 0, 0, 0.10);
  background: var(--hover);
  border-radius: 15px;
  padding: 5px 10px;
}
.stat-n { font: 500 11.5px var(--mono); color: #3A382F; }
.stat-bar { width: 36px; height: 3px; background: var(--active); border-radius: 2px; overflow: hidden; display: block; }
.stat-fill { display: block; height: 100%; background: var(--fg); }

.prob-btn {
  flex: none;
  display: inline-flex;
  align-items: center;
  gap: 5px;
  border: 1px solid rgba(194, 69, 54, 0.4);
  background: rgba(194, 69, 54, 0.07);
  color: var(--red);
  font: 600 12px var(--sans);
  padding: 5px 10px;
  border-radius: 15px;
  cursor: pointer;
}
.prob-btn:hover { background: rgba(194, 69, 54, 0.12); }
.prob-ok { flex: none; font: 600 12px var(--sans); color: var(--green); cursor: pointer; padding: 6px 4px; }

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

.sel-bar {
  display: flex;
  align-items: center;
  gap: 6px;
  background: var(--fg);
  border-radius: var(--r-lg);
  padding: 4px 6px 4px 12px;
}
.sel-label { font-size: 12px; color: #FFFFFF; font-weight: 500; }
.sel-btn {
  border: none;
  background: rgba(255, 255, 255, 0.14);
  color: #FFFFFF;
  font-size: 12px;
  padding: 4px 9px;
  border-radius: var(--r-sm);
  cursor: pointer;
}
.sel-x { border: none; background: transparent; color: var(--dim); font-size: 13px; padding: 4px 6px; cursor: pointer; }
</style>
