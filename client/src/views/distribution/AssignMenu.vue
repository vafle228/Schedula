<script setup>
import { computed, ref, watch, nextTick } from 'vue'
import { store } from '../../store/index.js'
import { initials, avatarBg } from '../../utils/format.js'
import { dui, hoursOf, norm, commitAssign } from './useDistribution.js'

const inputEl = ref(null)

watch(() => dui.menu, async (m) => {
  if (m) {
    await nextTick()
    if (inputEl.value) inputEl.value.focus()
  }
})

const list = computed(() => {
  if (!dui.menu) return []
  const q = dui.menuSearch.trim().toLowerCase()
  return store.state.teachers
    .filter((t) => !q || t.name.toLowerCase().includes(q))
    .map((t) => {
      const h = hoursOf(t.id, store.state.period)
      return {
        t, h,
        init: t.photo ? '' : initials(t.name),
        bg: avatarBg(t.photo),
        hoursLabel: h + ' / ' + norm + ' ч',
        over: h > norm,
      }
    })
})

function pick(t) {
  const ids = dui.menu.ids
  commitAssign(ids.map((id) => ({ topicId: id, to: t.id })))
  dui.menu = null
}
</script>

<template>
  <div v-if="dui.menu" class="backdrop" @click="dui.menu = null">
    <div
      class="menu"
      :style="{ left: dui.menu.x + 'px', top: dui.menu.y + 'px' }"
      @click.stop
    >
      <div class="menu-head">
        <span class="menu-title">{{ dui.menu.title }}</span>
        <input
          ref="inputEl"
          v-model="dui.menuSearch"
          class="input"
          placeholder="Найти преподавателя…"
          style="font-size: 12.5px"
        >
      </div>
      <div class="menu-list">
        <div v-for="row in list" :key="row.t.id" class="menu-row" @click="pick(row.t)">
          <span
            class="avatar"
            :style="{ background: row.bg, color: row.t.photo ? 'transparent' : '#5C574E' }"
          >{{ row.init }}</span>
          <span class="name">{{ row.t.name }}</span>
          <span class="hours mono" :style="{ color: row.over ? '#B45309' : '#8A857C' }">{{ row.hoursLabel }}</span>
        </div>
        <div v-if="list.length === 0" class="menu-empty">Не найдено</div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.backdrop { position: fixed; inset: 0; z-index: 50; }
.menu {
  position: fixed;
  width: 300px;
  background: var(--panel);
  border: 1px solid rgba(0, 0, 0, 0.12);
  border-radius: var(--r-xl);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.16);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.menu-head {
  padding: 10px 12px 8px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  border-bottom: 1px solid var(--line-soft);
}
.menu-title {
  font-size: 12px;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.menu-list { max-height: 300px; overflow-y: auto; padding: 4px 0; }
.menu-row { display: flex; align-items: center; gap: 9px; padding: 6px 12px; cursor: pointer; }
.menu-row:hover { background: var(--chip); }
.avatar {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 9px;
  font-weight: 600;
  flex: none;
  background-size: cover !important;
  background-position: center !important;
}
.name { font-size: 12.5px; flex: 1; min-width: 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.hours { flex: none; font: 400 11px var(--mono); }
.menu-empty { padding: 16px 12px; font-size: 12px; color: var(--muted); text-align: center; }
</style>
