<script setup>
import { computed, ref } from 'vue'
import { store } from '../../store/index.js'
import { kindOf, KINDS } from '../../utils/kinds.js'
import {
  ui, dayIdxs, dayHeads, slotsN, bells, visible, analysis, statusFor, place, openLf,
} from './useSchedule.js'

const gridEl = ref(null)
defineExpose({ focus: () => gridEl.value && gridEl.value.focus() })

const dragL = computed(() => (ui.dragId ? store.enriched.value.find((l) => l.id === ui.dragId) : null))
const curT = computed(() => (ui.view === 'teacher' ? store.teacherById(ui.ent.teacher) : null))

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
  const here = visible.value.filter((l) => l.d === d && l.s === s)
  const cell = {
    d, s, cards: here.map((l) => buildCard(l, d, s)),
    cls: { empty: !here.length },
    style: {},
    tag: '', tagColor: '#C24536',
    tip: here.length ? '' : 'Клик — новое занятие (N)',
  }
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
    const st = statusFor(dragL.value, d, s)
    if (st.kind === 'unfit') {
      // 2 ак.ч не влезает в слот на 1 ак.ч — слот гаснет и не принимает drop
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
  const isSoft = issues.some((x) => x.sev === 'soft')
  const K = kindOf(l.kind)
  const style = {}
  let titleColor
  let subColor = '#5C574E'
  if (l.orphan) {
    style.border = '1.5px dashed #B07C1F'
    style.background = 'rgba(176,124,31,0.06)'
    titleColor = '#B07C1F'
    subColor = '#8A6A28'
  } else if (isHard) {
    style.border = '1.5px solid #C24536'
    style.background = 'rgba(194,69,54,0.07)'
    titleColor = '#C24536'
    subColor = '#8A4038'
  } else {
    style.border = '1px solid ' + K.bd
    style.background = K.bg
    titleColor = K.dark
  }
  if (ui.sel.indexOf(l.id) >= 0) { style.outline = '2px solid #3B62C4'; style.outlineOffset = '1px' }
  if (ui.flashId === l.id || store.state.newIds.indexOf(l.id) >= 0) style.boxShadow = '0 0 0 2px rgba(59,98,196,0.45)'
  if (ui.dragId === l.id) style.opacity = '0.45'
  const icons = [l.pin ? '⌖' : '', isHard ? '⚠' : '', isSoft && !isHard ? '◐' : '', l.orphan ? '◌' : ''].filter(Boolean).join(' ')
  const t = store.teacherById(l.t)
  const who = ui.view === 'group' ? (t ? t.name : '') : l.g
  const tip = K.label
    + (l.topic ? ', ' + l.topic : ', тема не указана')
    + (issues.length
      ? ' — ' + issues.map((x) => x.text).join('; ')
      : (l.pin ? ' — закреплена, перегенерация не тронет' : ' — двойной клик: тема и вопрос'))
  return {
    l, d, s, style, titleColor, subColor, icons,
    iconColor: isHard ? '#C24536' : (l.orphan || isSoft) ? '#B07C1F' : '#5C574E',
    sub: who + ', ' + l.room + (ui.view === 'room' ? ', ' + (t ? t.name : '') : ''),
    tip,
  }
}

function onCellDrop(cell) {
  if (cell.unfit) return // 2 ак.ч нельзя в слот на 1 ак.ч
  if (ui.dragId) place(ui.dragId, cell.d, cell.s)
}

function onCellClick(cell) {
  const here = visible.value.filter((l) => l.d === cell.d && l.s === cell.s)
  if (!here.length && !ui.dragId) openLf({ d: cell.d, s: cell.s })
  else { ui.cursor = { d: cell.d, s: cell.s }; ui.sel = [] }
}

function onCardClick(card, e) {
  const id = card.l.id
  if (e.shiftKey || e.ctrlKey || e.metaKey) {
    ui.sel = ui.sel.indexOf(id) >= 0 ? ui.sel.filter((x) => x !== id) : [...ui.sel, id]
  } else {
    ui.sel = [id]
  }
  ui.cursor = { d: card.d, s: card.s }
}

function onCardDragStart(card, e) {
  e.dataTransfer.effectAllowed = 'move'
  ui.dragId = card.l.id
}

const legend = computed(() => Object.keys(KINDS).map((k) => ({
  label: KINDS[k].label.toLowerCase(), bd: KINDS[k].bd, bg: KINDS[k].bg,
})))
</script>

<template>
  <div ref="gridEl" class="grid-scroll" tabindex="0">
    <div class="grid" :style="{ gridTemplateColumns: '54px repeat(' + dayIdxs.length + ', minmax(126px, 1fr))' }">
      <span></span>
      <span v-for="dh in dayHeads" :key="dh" class="day-head">{{ dh }}</span>
      <template v-for="row in rows" :key="row.s">
        <span class="slot-label">
          <span class="slot-n mono">{{ row.label }}</span>
          <span class="slot-t mono">{{ row.from }}</span>
          <span class="slot-t mono">{{ row.to }}</span>
          <span class="slot-h mono">{{ row.hours }} ак.ч</span>
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
            @click.stop="onCardClick(card, $event)"
            @dblclick.stop="openLf(null, card.l.id)"
          >
            <div class="card-top">
              <span class="card-title" :style="{ color: card.titleColor }">{{ card.l.disc }}</span>
              <span class="card-icons" :style="{ color: card.iconColor }">{{ card.icons }}</span>
            </div>
            <div v-if="card.l.topic" class="card-topic" :style="{ color: card.titleColor }">{{ card.l.topic }}</div>
            <div class="card-sub" :style="{ color: card.subColor }">{{ card.sub }}</div>
          </div>
          <span v-if="cell.tag" class="cell-tag" :style="{ color: cell.tagColor }">{{ cell.tag }}</span>
        </div>
      </template>
    </div>
    <div class="legend">
      <span v-for="lg in legend" :key="lg.label" class="legend-item">
        <span class="legend-sw" :style="{ border: '1px solid ' + lg.bd, background: lg.bg }"></span>{{ lg.label }}
      </span>
    </div>
  </div>
</template>

<style scoped>
.grid-scroll { flex: 1; overflow: auto; padding: 10px 12px; outline: none; }
.grid { display: grid; gap: 4px; }
.day-head { text-align: center; font-size: 11.5px; font-weight: 600; color: var(--muted); padding: 2px 0; }
.slot-label { align-self: center; display: flex; flex-direction: column; align-items: center; gap: 1px; text-align: center; }
.slot-n { font-size: 11px; color: var(--faint); }
.slot-t { font-size: 8.5px; color: #C0BBB0; line-height: 1.2; }
.slot-h { font-size: 8px; color: #A8A399; line-height: 1.2; margin-top: 1px; }

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
.cell.cursor { outline: 2px solid var(--blue); outline-offset: -2px; }
.cell-tag { font-size: 9.5px; font-weight: 600; text-align: center; margin: auto; }

.card { border-radius: var(--r-sm); padding: 5px 7px; cursor: grab; }
.card-top { display: flex; align-items: center; gap: 5px; }
.card-title {
  font-size: 11.5px;
  font-weight: 600;
  flex: 1;
  min-width: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.card-icons { flex: none; font-size: 10.5px; }
.card-topic { font-size: 10px; opacity: 0.85; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.card-sub { font-size: 10.5px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

.legend { margin-top: 10px; display: flex; align-items: center; gap: 14px; flex-wrap: wrap; font-size: 11px; color: var(--sub); }
.legend-item { display: inline-flex; align-items: center; gap: 5px; }
.legend-sw { width: 12px; height: 12px; border-radius: 3px; }
</style>
