<script setup>
import { computed, ref } from 'vue'
import { store } from '../../store/index.js'
import { kindOf, KINDS } from '../../utils/kinds.js'
import InfoDot from '../../components/InfoDot.vue'
import { ui, entUnplaced, poolCards, openDlg, openLf, dragPlaced, unplaceToPool } from './useSchedule.js'

const searchEl = ref(null)
defineExpose({ focusSearch: () => searchEl.value && searchEl.value.focus() })

const kindOpts = computed(() => [
  { k: 'all', label: 'Все типы' },
  ...Object.entries(KINDS).map(([k, K]) => ({ k, label: K.label })),
])

const cards = computed(() => poolCards.value.map((l) => {
  const K = kindOf(l.kind)
  const t = store.teacherById(l.t)
  const tName = t ? t.name : ''
  return {
    l, K,
    title: ui.view === 'group' ? l.disc : l.disc + ', ' + l.g,
    norm: l.manual ? 'вручную' : 'пара ' + l.ni + ' из ' + l.nt,
    sub: ui.view === 'group' ? tName + ', ' + l.room : ui.view === 'teacher' ? K.label + ', ' + l.room : tName + ', ' + l.g,
    tip: K.label + (l.topic ? ', ' + l.topic : '') + ' — перетащите в клетку сетки или кликните, чтобы выбрать день и пару',
  }
}))

function onDragStart(l, e) {
  e.dataTransfer.effectAllowed = 'move'
  ui.dragId = l.id
}

/* return-to-pool drop target (Итерация 8) — only for a placed lesson */
function onPoolDragOver(e) {
  if (!dragPlaced.value) return
  e.preventDefault()
  e.dataTransfer.dropEffect = 'move'
  if (!ui.poolOver) ui.poolOver = true
}
function onPoolDragLeave(e) {
  if (e.currentTarget.contains(e.relatedTarget)) return
  ui.poolOver = false
}
function onPoolDrop(e) {
  if (!dragPlaced.value) return
  e.preventDefault()
  unplaceToPool(ui.dragId)
}
</script>

<template>
  <div
    class="panel pool"
    @dragover="onPoolDragOver"
    @dragleave="onPoolDragLeave"
    @drop="onPoolDrop"
  >
    <div class="pool-head">
      <span class="pool-title">Занятия</span>
      <span class="pool-count mono">{{ entUnplaced.length }}</span>
      <InfoDot tip="Пары выбранной группы, преподавателя или аудитории, ещё не поставленные в сетку. Перетащите карточку в клетку — или кликните по ней, чтобы выбрать день и пару." />
      <span class="sp"></span>
      <button class="btn new-btn" title="Новое занятие (N) — сразу в сетку или в пул" @click="openLf(null)">
        <span class="plus">＋</span>Занятие
      </button>
    </div>
    <div class="pool-filters">
      <input
        ref="searchEl"
        v-model="ui.q"
        class="input"
        placeholder="Поиск: дисциплина, ФИО…  ( / )"
        style="font-size: 12px"
      >
      <div class="select-wrap">
        <select v-model="ui.kindF" class="kind-filter">
          <option v-for="o in kindOpts" :key="o.k" :value="o.k">{{ o.label }}</option>
        </select>
        <span class="chev">▾</span>
      </div>
    </div>
    <div class="pool-list">
      <div v-if="dragPlaced" class="drop-zone" :class="{ over: ui.poolOver }">
        <span class="dz-ico">↩</span> Отпустите, чтобы снять с сетки и вернуть в пул
      </div>
      <div
        v-for="c in cards"
        :key="c.l.id"
        class="pool-card"
        :style="{ border: '1px solid ' + c.K.bd, background: c.K.bg }"
        :title="c.tip"
        draggable="true"
        @dragstart="onDragStart(c.l, $event)"
        @dragend="ui.dragId = null"
        @click="openDlg(c.l.id)"
      >
        <div class="pc-top">
          <span class="pc-title" :style="{ color: c.K.dark }">{{ c.title }}</span>
          <span class="pc-norm mono">{{ c.norm }}</span>
        </div>
        <div class="pc-sub">{{ c.sub }}</div>
      </div>

      <div v-if="entUnplaced.length === 0" class="pool-empty ok">
        <span class="ok-badge">✓</span>
        <span class="pe-title">Всё расставлено</span>
        <span class="pe-sub">У выбранной группы, преподавателя или аудитории нет пар в пуле.</span>
      </div>
      <div v-else-if="cards.length === 0" class="pool-empty">
        <span class="pe-nf">Ничего не найдено</span>
        <button class="btn" style="font-size: 12px; padding: 5px 12px" @click="ui.q = ''; ui.kindF = 'all'">
          Сбросить фильтры
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.pool { order: 1; flex: none; width: 300px; }
.pool-head { flex: none; display: flex; align-items: center; gap: 7px; padding: 10px 12px 8px; }
.pool-title { font-size: 13.5px; font-weight: 600; }
.pool-count { font: 500 11px var(--mono); color: var(--muted); background: var(--chip); border-radius: 10px; padding: 1px 7px; }
.sp { flex: 1; }
.new-btn { display: inline-flex; align-items: center; gap: 4px; font-size: 12px; padding: 4px 9px; }
.plus { font-size: 13px; line-height: 1; }

.pool-filters {
  flex: none;
  padding: 0 12px 8px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  border-bottom: 1px solid var(--line-soft);
}
.kind-filter { font-size: 12px; }

.pool-list { flex: 1; overflow-y: auto; padding: 8px 10px; display: flex; flex-direction: column; gap: 6px; }

.drop-zone {
  flex: none;
  display: flex;
  align-items: center;
  gap: 7px;
  justify-content: center;
  text-align: center;
  border: 1.5px dashed rgba(31, 138, 91, 0.5);
  background: rgba(31, 138, 91, 0.05);
  color: #166A45;
  border-radius: 8px;
  padding: 11px 10px;
  font-size: 11.5px;
  font-weight: 600;
}
.drop-zone.over { border-color: #1F8A5B; background: rgba(31, 138, 91, 0.14); }
.dz-ico { font-size: 14px; line-height: 1; }
.pool-card { border-radius: var(--r-lg); padding: 8px 11px; cursor: grab; display: flex; flex-direction: column; gap: 4px; }
.pool-card:hover { box-shadow: 0 2px 8px rgba(0, 0, 0, 0.10); }
.pc-top { display: flex; align-items: center; gap: 6px; }
.pc-title {
  font-size: 12.5px;
  font-weight: 600;
  flex: 1;
  min-width: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.pc-norm {
  flex: none;
  font: 500 10px var(--mono);
  background: rgba(255, 255, 255, 0.75);
  color: var(--sub);
  border-radius: 4px;
  padding: 1px 6px;
}
.pc-sub { font-size: 11px; color: var(--sub); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

.pool-empty { display: flex; flex-direction: column; align-items: center; gap: 9px; padding: 48px 16px; color: var(--muted); }
.pool-empty.ok { padding: 56px 16px; color: var(--green); }
.ok-badge {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  background: rgba(31, 138, 91, 0.12);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
}
.pe-title { font-size: 13px; font-weight: 600; }
.pe-sub { font-size: 11.5px; color: var(--muted); text-align: center; line-height: 1.5; }
.pe-nf { font-size: 13px; }
</style>
