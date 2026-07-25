<script setup>
import { computed } from 'vue'
import { store } from '../../store/index.js'
import ModalWindow from '../../components/ModalWindow.vue'
import { dui, KINDS, kindLabel } from './useDistribution.js'

const at = computed(() => dui.addTopic)
const disc = computed(() => (at.value ? store.disciplineById(at.value.discId) : null))
const valid = computed(() => !!(at.value && Number(at.value.hours) > 0))

function decH() { at.value.hours = Math.max(2, at.value.hours - 2) }
function incH() { at.value.hours = at.value.hours + 2 }

async function save() {
  if (!valid.value) return
  const a = at.value
  dui.addTopic = null
  await store.addTopic(a.discId, { kind: a.kind, name: kindLabel(a.kind), hours: Number(a.hours) })
}
</script>

<template>
  <ModalWindow v-if="at" :width="400" @close="dui.addTopic = null">
    <template #title>
      <div class="ttl">
        <span class="ttl-main">Добавить блок</span>
        <span class="ttl-sub">{{ disc ? disc.name + ' · ' + disc.course + ' курс' : '' }}</span>
      </div>
    </template>
    <div class="body">
      <div class="row">
        <div class="fld">
          <span class="lbl">Вид занятия</span>
          <div class="select-wrap">
            <select v-model="at.kind">
              <option v-for="k in KINDS" :key="k.k" :value="k.k">{{ k.label }}</option>
            </select>
            <span class="chev">▾</span>
          </div>
        </div>
        <div class="fld fld-hours">
          <span class="lbl">Ак. часов</span>
          <div class="hours-step">
            <button class="step-btn" :disabled="at.hours <= 2" @click="decH">−</button>
            <input v-model.number="at.hours" class="input mono step-input" type="number" min="2">
            <button class="step-btn" @click="incH">＋</button>
          </div>
        </div>
      </div>
    </div>
    <template #footer>
      <span style="flex: 1"></span>
      <button class="btn btn-lg" @click="dui.addTopic = null">Отмена</button>
      <button class="btn-primary btn-lg" :disabled="!valid" @click="save">Добавить блок</button>
    </template>
  </ModalWindow>
</template>

<style scoped>
.ttl { flex: 1; display: flex; flex-direction: column; gap: 1px; }
.ttl-main { font-size: 15px; font-weight: 600; }
.ttl-sub { font-size: 12px; color: var(--muted); }
.body { padding: 14px 18px; }
.row { display: flex; align-items: flex-end; gap: 10px; }
.fld { display: flex; flex-direction: column; gap: 5px; min-width: 0; flex: 1; }
.fld-hours { flex: none; }
.lbl { font-size: 12px; font-weight: 600; color: var(--sub); }
.hours-step { display: inline-flex; align-items: center; gap: 4px; }
.step-btn {
  border: 1px solid var(--line-strong);
  background: var(--panel);
  width: 28px;
  height: 28px;
  border-radius: var(--r-md);
  cursor: pointer;
  font-size: 15px;
  line-height: 1;
  flex: none;
}
.step-btn:hover { background: var(--hover); }
.step-btn:disabled { opacity: 0.35; cursor: default; }
.step-input {
  width: 52px;
  text-align: center;
  font: 500 14px var(--mono);
  padding: 5px 4px;
  -moz-appearance: textfield;
}
.step-input::-webkit-inner-spin-button,
.step-input::-webkit-outer-spin-button { -webkit-appearance: none; }
</style>
