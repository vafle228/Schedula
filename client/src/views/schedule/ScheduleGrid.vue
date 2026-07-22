<script setup>
import { computed, ref } from 'vue'
import { store } from '../../store/index.js'
import { kindOf } from '../../utils/kinds.js'
import {
  ui, dayIdxs, dayHeads, slotsN, bells, weekVisible, analysis, statusFor,
  place, openLf, dateFor, isHol,
} from './useSchedule.js'

const gridEl = ref(null)
defineExpose({ focus: () => gridEl.value && gridEl.value.focus() })

const dragL = computed(() => (ui.dragId ? store.enriched.value.find((l) => l.id === ui.dragId) : null))
const curT = computed(() => (ui.view === 'teacher' ? store.teacherById(ui.ent.teacher) : null))

const dayCols = computed(() => dayIdxs.value.map((d, i) => ({
  d,
  name: dayHeads.value[i],
  date: dateFor(ui.week, d),
  hol: isHol(ui.week, d),
})))

const rows = computed(() => {
  const out = []
  for (let s = 0; s < slotsN.value; s++) {
    const cells = dayIdxs.value.map((d) => buildCell(d, s))
    const bell = bells.value[s] || { from: '', to: '', hours: 2 }
    out.push({ s, label: String(s + 1), from: bell.from, to: bell.to, hours: bell.hours, cells })
  }
  return out
})

function buildCell(d, s) {
  const holiday = isHol(ui.week, d)
  const here = weekVisible.value.filter((l) => l.d === d && l.s === s)
  const cell = {
    d, s, holiday, cards: here.map((l) => buildCard(l, d, s)),
    cls: { empty: !here.length && !holiday, holiday },
    style: {},
    tag: '', tagColor: '#C24536',
    tip: holiday ? 'Праздничный день' : here.length ? '' : 'Клик — новое занятие (N)',
  }
  if (holiday) return cell
  if (curT.value && curT.value.c) {
    const k = d + '-' + s
    const c = curT.value.c
    if (c.method === d || c.hard.indexOf(k) >= 0) {
      cell.style.background = 'repeating-linear-gradient(45deg,#F2F0EB,#F2F0EB 5px,#FBFAF8 5px,#FBFAF8 10px)'
    } else if (c.soft.indexOf(k) >= 0) {
      cell.style.background = 'rgba(176,124,31,0.05)'
    }
  }
  if (dragL.value) {
    const st = statusFor(dragL.value, ui.week, d, s)
    if (st.kind === 'unfit') {
      cell.style.border = '1px dashed rgba(0,0,0,0.14)'
      cell.style.background = 'repeating-linear-gradient(45deg,#F2F0EB,#F2F0EB 5px,#FBFAF8 5px,#FBFAF8 10px)'
      cell.style.opacity = '0.5'
      cell.unfit = true
      if (!here.length) { cell.tag = '✕ не тот слот'; cell.tagColor = '#8A857C' }
    } else if (st.kind === 'free') {
      cell.style.border = '2px solid rgba(31,138,91,0.7)'
      cell.style.background = 'rgba(31,138,91,0.05)'
    } else if (st.kind === 'soft') {
      cell.style.border = '2px solid rgba(176,124,31,0.7)'
      cell.style.background = 'rgba(176,124,31,0.06)'
      if (!here.length) { cell.tag = '◐ пожелание'; cell.tagColor = '#B07C1F' }
    } else {
      cell.style.border = '2px solid rgba(194,69,54,0.65)'
      cell.style.background = 'rgba(194,69,54,0.05)'
      if (!here.length) { cell.tag = '⚠ конфликт'; cell.tagColor = '#C24536' }
    }
    cell.cls.empty = false
  }
  if (ui.cursor && ui.cursor.d === d && ui.cursor.s === s) cell.cls.cursor = true
  return cell
}

function buildCard(l, d, s) {
  const issues = analysis.value.byId[l.id] || []
  const isHard = issues.some((x) => x.sev === 'hard')
  const isSub = !!l.subBy
  const K = kindOf(l.kind)
  const eff = store.teacherById(l.subBy || l.t)
  const effName = eff ? eff.name : ''
  const who = ui.view === 'group' ? effName : l.g
  const style = {}
  let titleColor
  let subColor = '#5C574E'
  let badge = ''
  /* Cell fill encodes STATE (Итерация 8); the type is shown by the dot.
     placed = green, manual = blue, замена = amber, конфликт = red. */
  if (l.orphan) {
    style.border = '1.5px dashed #B07C1F'
    style.background = 'rgba(176,124,31,0.06)'
    titleColor = '#B07C1F'
    subColor = '#8A6A28'
    badge = 'вне плана'
  } else if (isHard) {
    style.border = '1.5px solid #C24536'
    style.background = 'rgba(194,69,54,0.08)'
    titleColor = '#C24536'
    subColor = '#8A4038'
    badge = '⚠ конфликт'
  } else if (isSub) {
    style.border = '1px solid rgba(176,124,31,0.55)'
    style.background = 'rgba(176,124,31,0.10)'
    titleColor = '#8A6A28'
    subColor = '#8A6A28'
    badge = 'замена · ' + effName.split(' ')[0]
  } else if (l.manual) {
    style.border = '1px solid rgba(59,98,196,0.5)'
    style.background = 'rgba(59,98,196,0.14)'
    titleColor = '#2A4B9E'
    subColor = '#3A4A6E'
    badge = 'вручную'
  } else {
    style.border = '1px solid rgba(31,138,91,0.4)'
    style.background = 'rgba(31,138,91,0.12)'
    titleColor = '#166A45'
  }
  if (ui.sel.indexOf(l.id) >= 0) { style.outline = '2px solid #3B62C4'; style.outlineOffset = '1px' }
  if (ui.flashId === l.id || store.state.newIds.indexOf(l.id) >= 0) style.boxShadow = '0 0 0 2px rgba(59,98,196,0.45)'
  if (ui.dragId === l.id) style.opacity = '0.45'
  const tip = K.label
    + (l.topic ? ', ' + l.topic : ', тема не указана')
    + (isSub ? ' — замена: ' + effName : '')
    + (issues.length
      ? ' — ' + issues.map((x) => x.text).join('; ')
      : (l.pin ? ' — закреплена, перегенерация не тронет' : ' — клик: карточка занятия'))
  return {
    l, d, s, style, titleColor, subColor, badge,
    dotColor: K.color,
    pinMark: l.pin ? ' ⌖' : '',
    sub: who + ', ' + l.room + (ui.view === 'room' ? ', ' + effName : ''),
    tip,
  }
}

function onCellDrop(cell) {
  if (cell.holiday || cell.unfit) return
  if (ui.dragId) place(ui.dragId, ui.week, cell.d, cell.s)
}

function onCellClick(cell) {
  if (cell.holiday) return
  /* Cells are drag-only (Итерация 8): a click just moves the keyboard cursor.
     New lessons are created in «Содержание курсов» → «+ занятие». */
  ui.cursor = { d: cell.d, s: cell.s }
  ui.sel = []
}

function onCardClick(card) {
  openLf(null, card.l.id)
}

function onCardDragStart(card, e) {
  e.dataTransfer.effectAllowed = 'move'
  ui.dragId = card.l.id
}

</script>

<template>
  <div ref="gridEl" class="grid-scroll" tabindex="0">
    <div class="grid" :style="{ gridTemplateColumns: '66px repeat(' + dayCols.length + ', minmax(126px, 1fr))' }">
      <span></span>
      <span v-for="c in dayCols" :key="c.d" class="day-head" :class="{ hol: c.hol }">
        <span class="dh-name">{{ c.name }}</span>
        <span class="dh-date mono">{{ c.date }}{{ c.hol ? ' ⚑' : '' }}</span>
      </span>
      <template v-for="row in rows" :key="row.s">
        <span class="slot-label">
          <span class="slot-n mono">{{ row.label }}</span>
          <span class="slot-time mono">{{ row.from }}–{{ row.to }}</span>
          <span class="slot-h mono" :class="{ one: row.hours === 1 }">{{ row.hours }} ак.ч</span>
        </span>
        <div
          v-for="cell in row.cells"
          :key="cell.d + '-' + cell.s"
          class="cell"
          :class="cell.cls"
          :style="cell.style"
          :title="cell.tip"
          @dragover.prevent
          @drop.prevent="onCellDrop(cell)"
          @click="onCellClick(cell)"
        >
          <div
            v-for="card in cell.cards"
            :key="card.l.id"
            class="card"
            :style="card.style"
            :title="card.tip"
            draggable="true"
            @dragstart="onCardDragStart(card, $event)"
            @dragend="ui.dragId = null"
            @click.stop="onCardClick(card)"
          >
            <div class="card-top">
              <span class="card-dot" :style="{ background: card.dotColor }"></span>
              <span class="card-title" :style="{ color: card.titleColor }">{{ card.l.disc }}{{ card.pinMark }}</span>
            </div>
            <div class="card-sub" :style="{ color: card.subColor }">{{ card.sub }}</div>
            <div v-if="card.badge" class="card-badge" :style="{ color: card.titleColor }">{{ card.badge }}</div>
          </div>
          <span v-if="cell.tag" class="cell-tag" :style="{ color: cell.tagColor }">{{ cell.tag }}</span>
        </div>
      </template>
    </div>
    <div class="legend">
      <span class="legend-item">
        <span class="legend-sw" style="border:1px solid rgba(31,138,91,0.4);background:rgba(31,138,91,0.18)"></span>разложено
      </span>
      <span class="legend-item">
        <span class="legend-sw" style="border:1px solid rgba(59,98,196,0.45);background:rgba(59,98,196,0.14)"></span>вручную
      </span>
      <span class="legend-item">
        <span class="legend-sw" style="border:1.5px solid #B07C1F;background:rgba(176,124,31,0.14)"></span>замена
      </span>
      <span class="legend-item">
        <span class="legend-sw" style="border:1.5px solid #C24536;background:rgba(194,69,54,0.08)"></span>конфликт
      </span>
      <span class="legend-item">
        <span class="legend-sw hatch"></span>праздник
      </span>
      <span class="legend-note mono">⌖ закреплено · строка = слот звонков · занятие занимает слот целиком</span>
    </div>
  </div>
</template>

<style scoped>
.grid-scroll { flex: 1; overflow: auto; padding: 10px 12px; outline: none; }
.grid { display: grid; gap: 4px; }
.day-head { display: flex; flex-direction: column; align-items: center; gap: 1px; padding: 2px 0; }
.dh-name { font-size: 11.5px; font-weight: 600; color: var(--muted); }
.dh-date { font-size: 9px; color: var(--faint); }
.day-head.hol .dh-name { color: var(--amber); }
.day-head.hol .dh-date { color: var(--amber); }
.slot-label { align-self: center; display: flex; flex-direction: column; align-items: center; gap: 1px; text-align: center; }
.slot-n { font: 500 10.5px var(--mono); color: var(--muted); }
.slot-time { font-size: 8.5px; color: #B5B0A6; line-height: 1.2; }
.slot-h {
  font: 500 8px var(--mono);
  color: #5C574E;
  background: #ECEAE4;
  border-radius: 3px;
  padding: 1px 5px;
  margin-top: 2px;
}
.slot-h.one { color: #8A6A28; background: rgba(176, 124, 31, 0.14); }

.cell {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 3px;
  padding: 3px;
  border-radius: var(--r-md);
  min-height: 52px;
  border: 1px solid transparent;
}
.cell.empty { border: 1px dashed rgba(0, 0, 0, 0.13); }
.cell.holiday { background: repeating-linear-gradient(45deg, #EDEAE3, #EDEAE3 5px, #F6F5F2 5px, #F6F5F2 10px); }
.cell.cursor { outline: 2px solid var(--blue); outline-offset: -2px; }
.cell-tag { font-size: 9.5px; font-weight: 600; text-align: center; margin: auto; }

.card { border-radius: var(--r-sm); padding: 5px 7px; cursor: grab; }
.card-top { display: flex; align-items: center; gap: 5px; }
.card-dot { width: 8px; height: 8px; border-radius: 50%; flex: none; }
.card-title {
  font-size: 11.5px;
  font-weight: 600;
  flex: 1;
  min-width: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.card-sub { font-size: 10.5px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.card-badge {
  align-self: flex-start;
  margin-top: 2px;
  font: 500 8px var(--mono);
  background: rgba(0, 0, 0, 0.05);
  border-radius: 3px;
  padding: 1px 5px;
}

.legend { margin-top: 14px; padding-top: 12px; border-top: 1px dashed rgba(0, 0, 0, 0.12); display: flex; align-items: center; gap: 13px; flex-wrap: wrap; font-size: 11px; color: var(--sub); }
.legend-note { color: var(--faint); }
.legend-item { display: inline-flex; align-items: center; gap: 5px; }
.legend-sw { width: 12px; height: 12px; border-radius: 3px; }
.legend-sw.hatch { background: repeating-linear-gradient(45deg, #EDEAE3, #EDEAE3 3px, #F6F5F2 3px, #F6F5F2 6px); }
</style>
