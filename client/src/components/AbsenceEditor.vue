<script setup>
import { computed } from 'vue'
import { store } from '../store/index.js'
import { ABSENCE_TYPES, ABSENCE_COLORS } from '../utils/kinds.js'

const props = defineProps({
  teacher: { type: Object, required: true },
})

const absences = computed(() => props.teacher.absences || [])

const add = () => store.addAbsence(props.teacher.id, { type: 'vacation', label: '' })
const setType = (a, e) => store.patchAbsence(props.teacher.id, a.id, { type: e.target.value })
const setLabel = (a, e) => store.patchAbsence(props.teacher.id, a.id, { label: e.target.value })
const remove = (a) => store.removeAbsence(props.teacher.id, a.id)
</script>

<template>
  <div class="abs">
    <div v-for="a in absences" :key="a.id" class="abs-row">
      <span class="dot" :style="{ background: ABSENCE_COLORS[a.type] || '#8A857C' }"></span>
      <div class="select-wrap type-sel">
        <select :value="a.type" @change="setType(a, $event)">
          <option v-for="o in ABSENCE_TYPES" :key="o.v" :value="o.v">{{ o.label }}</option>
        </select>
        <span class="chev">▾</span>
      </div>
      <input
        class="input label-input"
        :value="a.label"
        placeholder="напр. 01–14 сентября"
        @change="setLabel(a, $event)"
      >
      <span class="rm" title="Удалить период" @click="remove(a)">✕</span>
    </div>
    <div v-if="absences.length === 0" class="empty">
      Отсутствий нет — преподаватель доступен весь семестр.
    </div>
    <div class="add" title="Добавить период отсутствия" @click="add">
      <span class="add-circle">＋</span>Добавить период
    </div>
  </div>
</template>

<style scoped>
.abs { display: flex; flex-direction: column; gap: 10px; }
.abs-row { display: flex; align-items: center; gap: 8px; }
.dot { flex: none; width: 8px; height: 8px; border-radius: 2px; }
.type-sel { flex: none; width: 158px; }
.label-input { flex: 1; min-width: 0; font-size: 12.5px; }
.rm { flex: none; color: var(--dim); cursor: pointer; font-size: 15px; line-height: 1; padding: 2px 4px; }
.rm:hover { color: var(--orange-dark); }
.empty { font-size: 12px; color: var(--faint); padding: 2px 0; }
.add {
  align-self: flex-start;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: var(--blue);
  font-size: 12.5px;
  font-weight: 500;
  cursor: pointer;
  padding: 2px 0;
}
.add:hover { color: var(--blue-dark); }
.add-circle {
  width: 20px;
  height: 20px;
  border: 1.5px dashed rgba(59, 98, 196, 0.4);
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
}
</style>
