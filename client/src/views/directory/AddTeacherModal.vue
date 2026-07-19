<script setup>
import { reactive, computed } from 'vue'
import { store } from '../../store/index.js'
import { initials, avatarBg } from '../../utils/format.js'
import ModalWindow from '../../components/ModalWindow.vue'

const emit = defineEmits(['close', 'created'])

const form = reactive({ name: '', photo: null })
const valid = computed(() => !!form.name.trim())
const init = computed(() => (form.photo ? '' : initials(form.name) || '—'))

function onPhoto(e) {
  const f = e.target.files && e.target.files[0]
  if (!f) return
  const r = new FileReader()
  r.onload = () => { form.photo = r.result }
  r.readAsDataURL(f)
}

async function save() {
  if (!valid.value) return
  const t = await store.createTeacher({ name: form.name.trim(), photo: form.photo })
  emit('created', t)
}
</script>

<template>
  <ModalWindow title="Новый преподаватель" :width="460" @close="emit('close')">
    <div class="body">
      <div class="photo-row">
        <label
          class="photo-circle"
          :style="{ background: avatarBg(form.photo) }"
          title="Загрузить фото"
        >
          {{ init }}
          <input type="file" accept="image/*" style="display: none" @change="onPhoto">
        </label>
        <div class="photo-info">
          <span class="lbl">Фото</span>
          <span class="photo-hint">
            Нажмите на кружок, чтобы загрузить. Без фото используются инициалы —
            фото можно заменить в любой момент на карточке.
          </span>
          <span v-if="form.photo" class="photo-clear" @click="form.photo = null">Убрать фото</span>
        </div>
      </div>
      <div class="fld">
        <span class="lbl">ФИО</span>
        <input v-model="form.name" class="input" placeholder="Фамилия И. О.">
      </div>
      <span class="hint">Доступность и периоды отсутствия заполняются на карточке после создания.</span>
    </div>
    <template #footer>
      <span style="flex: 1"></span>
      <button class="btn btn-lg" @click="emit('close')">Отмена</button>
      <button class="btn-primary btn-lg" :disabled="!valid" @click="save">Добавить</button>
    </template>
  </ModalWindow>
</template>

<style scoped>
.body { padding: 18px; display: flex; flex-direction: column; gap: 16px; }
.photo-row { display: flex; gap: 14px; align-items: center; }
.photo-circle {
  flex: none;
  width: 64px;
  height: 64px;
  border-radius: 50%;
  color: var(--sub);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: 600;
  cursor: pointer;
  overflow: hidden;
  border: 1px solid rgba(0, 0, 0, 0.1);
  background-size: cover !important;
  background-position: center !important;
}
.photo-info { flex: 1; display: flex; flex-direction: column; gap: 6px; }
.lbl { font-size: 12px; font-weight: 600; color: var(--sub); }
.photo-hint { font-size: 12px; color: var(--muted); line-height: 1.4; }
.photo-clear { font-size: 11.5px; color: var(--blue); cursor: pointer; }
.fld { display: flex; flex-direction: column; gap: 6px; }
.hint { font-size: 11.5px; color: var(--muted); line-height: 1.5; }
</style>
