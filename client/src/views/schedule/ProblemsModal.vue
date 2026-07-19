<script setup>
import { computed } from 'vue'
import { store } from '../../store/index.js'
import { ALL_DAYS } from '../../utils/kinds.js'
import ModalWindow from '../../components/ModalWindow.vue'
import { ui, analysis, flash } from './useSchedule.js'

const items = computed(() => {
  const out = []
  store.enriched.value.forEach((l) => {
    const issues = analysis.value.byId[l.id]
    if (!issues) return
    const isHard = issues.some((x) => x.sev === 'hard')
    const isOrphan = issues.some((x) => x.sev === 'orphan')
    const t = store.teacherById(l.t)
    out.push({
      l,
      title: l.disc + ', ' + l.g,
      icon: isHard ? '⚠' : isOrphan ? '◌' : '◐',
      hard: isHard,
      color: isHard ? '#C24536' : '#B07C1F',
      border: isHard ? 'rgba(194,69,54,0.35)' : 'rgba(176,124,31,0.35)',
      bg: isHard ? 'rgba(194,69,54,0.04)' : 'rgba(176,124,31,0.04)',
      text: issues.map((x) => x.text).join('; '),
      loc: l.d != null ? ALL_DAYS[l.d] + ', ' + (l.s + 1) + ' пара, ' + (t ? t.name : '') : 'в пуле',
    })
  })
  out.sort((a, b) => (a.hard ? 0 : 1) - (b.hard ? 0 : 1))
  return out
})

function go(item) {
  const l = item.l
  ui.view = 'group'
  ui.ent.group = l.g
  ui.cursor = l.d != null ? { d: l.d, s: l.s } : null
  ui.sel = [l.id]
  ui.prob = false
  flash(l.id)
}
</script>

<template>
  <ModalWindow v-if="ui.prob" title="Проблемы расписания" :width="540" @close="ui.prob = false">
    <div class="list">
      <div
        v-for="(it, i) in items"
        :key="i"
        class="item"
        :style="{ border: '1px solid ' + it.border, background: it.bg }"
        title="Клик — показать место проблемы в сетке"
        @click="go(it)"
      >
        <div class="item-top">
          <span class="ico" :style="{ color: it.color }">{{ it.icon }}</span>
          <span class="title" :style="{ color: it.color }">{{ it.title }}</span>
          <span class="loc mono">{{ it.loc }}</span>
        </div>
        <div class="text">{{ it.text }}</div>
      </div>
      <div v-if="items.length === 0" class="empty">
        <span class="ok-badge">✓</span>
        <span class="e-title">Проблем нет</span>
        <span class="e-sub">Конфликтов, осиротевших пар и нарушенных пожеланий не найдено.</span>
      </div>
    </div>
  </ModalWindow>
</template>

<style scoped>
.list {
  flex: 1;
  overflow-y: auto;
  padding: 12px 16px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  max-height: 70vh;
  min-height: 120px;
}
.item { border-radius: var(--r-lg); padding: 9px 12px; cursor: pointer; display: flex; flex-direction: column; gap: 2px; }
.item:hover { box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08); }
.item-top { display: flex; align-items: center; gap: 6px; }
.ico { flex: none; font-size: 11px; }
.title {
  font-size: 12.5px;
  font-weight: 600;
  flex: 1;
  min-width: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.loc { flex: none; font: 400 10.5px var(--mono); color: var(--faint); }
.text { font-size: 11.5px; color: var(--sub); line-height: 1.45; }
.empty { display: flex; flex-direction: column; align-items: center; gap: 9px; padding: 40px 16px; color: var(--green); }
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
.e-title { font-size: 13px; font-weight: 600; }
.e-sub { font-size: 11.5px; color: var(--muted); text-align: center; line-height: 1.5; }
</style>
