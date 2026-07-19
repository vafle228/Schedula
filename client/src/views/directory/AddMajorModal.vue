<script setup>
import { reactive, computed } from 'vue'
import { store } from '../../store/index.js'
import ModalWindow from '../../components/ModalWindow.vue'

const emit = defineEmits(['close', 'created'])

const form = reactive({ code: '', name: '' })
const valid = computed(() => !!(form.code.trim() && form.name.trim()))

async function save() {
  if (!valid.value) return
  const m = await store.createMajor({ code: form.code.trim(), name: form.name.trim() })
  emit('created', m)
}
</script>

<template>
  <ModalWindow title="Новая специальность" :width="460" @close="emit('close')">
    <div class="body">
      <div class="row">
        <div class="fld" style="flex: none; width: 130px">
          <span class="lbl">Код</span>
          <input v-model="form.code" class="input mono" placeholder="09.02.07" style="font-weight: 500">
        </div>
        <div class="fld" style="flex: 1">
          <span class="lbl">Название</span>
          <input v-model="form.name" class="input" placeholder="Напр. Сетевое и системное администрирование">
        </div>
      </div>
      <span class="hint">Группы добавляются на карточке специальности после создания.</span>
    </div>
    <template #footer>
      <span style="flex: 1"></span>
      <button class="btn btn-lg" @click="emit('close')">Отмена</button>
      <button class="btn-primary btn-lg" :disabled="!valid" @click="save">Добавить</button>
    </template>
  </ModalWindow>
</template>

<style scoped>
.body { padding: 18px; display: flex; flex-direction: column; gap: 14px; }
.row { display: flex; gap: 10px; }
.fld { display: flex; flex-direction: column; gap: 6px; }
.lbl { font-size: 12px; font-weight: 600; color: var(--sub); }
.hint { font-size: 11.5px; color: var(--muted); line-height: 1.5; }
</style>
