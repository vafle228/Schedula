<script setup>
import { computed } from 'vue'
import { store } from '../../store/index.js'
import ModalWindow from '../../components/ModalWindow.vue'
import { dui, KINDS } from './useDistribution.js'

const at = computed(() => dui.addTopic)
const disc = computed(() => (at.value ? store.disciplineById(at.value.discId) : null))
const valid = computed(() => !!(at.value && at.value.name.trim() && Number(at.value.hours) > 0))

async function save() {
  if (!valid.value) return
  const a = at.value
  dui.addTopic = null
  await store.addTopic(a.discId, { kind: a.kind, name: a.name.trim(), hours: Number(a.hours) })
}
</script>

<template>
  <ModalWindow v-if="at" :width="480" @close="dui.addTopic = null">
    <template #title>
      <div class="ttl">
        <span class="ttl-main">Добавить тему</span>
        <span class="ttl-sub">{{ disc ? disc.name + ', ' + disc.groupId : '' }}</span>
      </div>
    </template>
    <div class="body">
      <div class="fld" style="align-self: flex-start; width: 200px">
        <span class="lbl">Вид занятия</span>
        <div class="select-wrap">
          <select v-model="at.kind">
            <option v-for="k in KINDS" :key="k.k" :value="k.k">{{ k.label }}</option>
          </select>
          <span class="chev">▾</span>
        </div>
      </div>
      <div class="row">
        <div class="fld" style="flex: 1">
          <span class="lbl">Название темы</span>
          <input v-model="at.name" class="input" placeholder="Например: Раздел 3. Индексы">
        </div>
        <div class="fld" style="flex: none; width: 96px">
          <span class="lbl">Часы</span>
          <input v-model="at.hours" class="input mono" type="number" min="0" style="text-align: right">
        </div>
      </div>
    </div>
    <template #footer>
      <span style="flex: 1"></span>
      <button class="btn btn-lg" @click="dui.addTopic = null">Отмена</button>
      <button class="btn-primary btn-lg" :disabled="!valid" @click="save">Добавить тему</button>
    </template>
  </ModalWindow>
</template>

<style scoped>
.ttl { flex: 1; display: flex; flex-direction: column; gap: 1px; }
.ttl-main { font-size: 15px; font-weight: 600; }
.ttl-sub { font-size: 12px; color: var(--muted); }
.body { padding: 18px; display: flex; flex-direction: column; gap: 14px; }
.row { display: flex; gap: 12px; }
.fld { display: flex; flex-direction: column; gap: 6px; min-width: 0; }
.lbl { font-size: 12px; font-weight: 600; color: var(--sub); }
</style>
