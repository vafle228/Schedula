<script setup>
import { computed } from 'vue'
import { store } from '../../store/index.js'
import { kindOf, ALL_DAYS } from '../../utils/kinds.js'
import ModalWindow from '../../components/ModalWindow.vue'
import { ui, dayIdxs, slotsN, bells, statusFor, place, ST_COLORS } from './useSchedule.js'

const dlg = computed(() => ui.dlg)
const L = computed(() => store.enriched.value.find((l) => l.id === dlg.value.id))

const dayOpts = computed(() => dayIdxs.value.map((i) => ({ v: String(i), label: ALL_DAYS[i] })))
const slotOpts = computed(() => Array.from({ length: slotsN.value }, (_, i) => {
  const b = bells.value[i] || { from: '', to: '', hours: 2 }
  return { v: String(i), label: (i + 1) + ' пара · ' + b.from + '–' + b.to + ' · ' + b.hours + ' ак.ч' }
}))
const roomOpts = computed(() => store.state.rooms.map((r) => ({ v: r.id, label: r.id + ', ' + r.type + ', ' + r.capacity })))

const status = computed(() => {
  if (!L.value) return { kind: 'free', text: '' }
  return statusFor(L.value, parseInt(dlg.value.d), parseInt(dlg.value.s), dlg.value.r)
})
const sc = computed(() => ST_COLORS[status.value.kind])

const teacherName = computed(() => {
  const t = L.value ? store.teacherById(L.value.t) : null
  return t ? t.name : ''
})

function confirm() {
  place(dlg.value.id, parseInt(dlg.value.d), parseInt(dlg.value.s), dlg.value.r)
  ui.dlg = null
}
</script>

<template>
  <ModalWindow v-if="dlg && L" title="Разместить пару" :width="420" @close="ui.dlg = null">
    <div class="body">
      <div class="lesson-chip">
        <span class="mark" :style="{ color: kindOf(L.kind).dot }">{{ kindOf(L.kind).mark }}</span>
        <span class="lname">{{ L.disc }}, {{ L.g }}</span>
        <span class="lsub">{{ teacherName }}</span>
      </div>
      <div class="selects">
        <div class="fld">
          <span class="field-label">День</span>
          <div class="select-wrap">
            <select v-model="dlg.d">
              <option v-for="o in dayOpts" :key="o.v" :value="o.v">{{ o.label }}</option>
            </select>
            <span class="chev">▾</span>
          </div>
        </div>
        <div class="fld">
          <span class="field-label">Пара</span>
          <div class="select-wrap">
            <select v-model="dlg.s">
              <option v-for="o in slotOpts" :key="o.v" :value="o.v">{{ o.label }}</option>
            </select>
            <span class="chev">▾</span>
          </div>
        </div>
        <div class="fld">
          <span class="field-label">Аудитория</span>
          <div class="select-wrap">
            <select v-model="dlg.r">
              <option v-for="o in roomOpts" :key="o.v" :value="o.v">{{ o.label }}</option>
            </select>
            <span class="chev">▾</span>
          </div>
        </div>
      </div>
      <div class="status" :style="{ border: '1px solid ' + sc.border, background: sc.bg }">
        <span class="st-ico" :style="{ color: sc.color }">{{ sc.icon }}</span>
        <span class="st-text">{{ status.text }}</span>
      </div>
      <div class="hint">Конфликт не блокирует размещение — он будет подсвечен в сетке и попадёт в панель проблем. Слот на 1 ак.ч не примет занятие на 2 ак.ч.</div>
    </div>
    <template #footer>
      <button class="btn btn-lg" @click="ui.dlg = null">Отмена</button>
      <span style="flex: 1"></span>
      <button class="btn-primary btn-lg" :disabled="status.kind === 'unfit'" @click="confirm">Разместить</button>
    </template>
  </ModalWindow>
</template>

<style scoped>
.body { padding: 16px 18px; display: flex; flex-direction: column; gap: 12px; }
.lesson-chip {
  border: 1px solid rgba(0, 0, 0, 0.1);
  background: var(--hover);
  border-radius: var(--r-lg);
  padding: 9px 11px;
  display: flex;
  align-items: center;
  gap: 7px;
}
.mark { font-size: 11px; }
.lname { font-size: 13px; font-weight: 600; flex: 1; }
.lsub { font-size: 11.5px; color: var(--muted); }
.selects { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; }
.fld { display: flex; flex-direction: column; gap: 4px; min-width: 0; }
.status { display: flex; gap: 8px; align-items: baseline; border-radius: var(--r-lg); padding: 9px 11px; }
.st-ico { flex: none; font-size: 12px; }
.st-text { font-size: 12.5px; line-height: 1.5; color: #3A382F; }
.hint { font-size: 11px; color: var(--muted); line-height: 1.5; }
</style>
