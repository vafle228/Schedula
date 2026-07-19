<script setup>
import { computed } from 'vue'
import { store } from '../../store/index.js'
import { api } from '../../api/index.js'
import ModalWindow from '../../components/ModalWindow.vue'
import { ui, enriched, problemsN } from './useSchedule.js'

const ex = computed(() => ui.ex)
const unplacedN = computed(() => enriched.value.filter((l) => l.d == null).length)
const hasWarn = computed(() => unplacedN.value > 0 || problemsN.value > 0)

const scopeAllN = computed(() => (ex.value.view === 'teacher' ? store.state.teachers.length : store.state.groups.length))

async function run() {
  const { exportId } = await api.exportSchedule({
    period: store.state.period,
    view: ex.value.view,
    scope: ex.value.scope,
    format: 'xlsx',
  })
  const info = await api.getExport(exportId)
  ui.ex = { ...ex.value, step: 'done', fileName: info.fileName }
}
</script>

<template>
  <ModalWindow v-if="ex" title="Экспорт расписания" :width="520" @close="ui.ex = null">
      <div v-if="ex.step === 'config'" class="body">
        <div class="fld">
          <span class="field-label">ПРЕДСТАВЛЕНИЕ</span>
          <div class="row-btns">
            <button class="pick-soft rb" :class="{ on: ex.view === 'group' }" @click="ex.view = 'group'">По группам</button>
            <button class="pick-soft rb" :class="{ on: ex.view === 'teacher' }" @click="ex.view = 'teacher'">По преподавателям</button>
          </div>
        </div>
        <div class="fld">
          <span class="field-label">ОХВАТ</span>
          <div class="row-btns">
            <button class="pick-soft rb" :class="{ on: ex.scope === 'all' }" @click="ex.scope = 'all'">Все ({{ scopeAllN }})</button>
            <button class="pick-soft rb" :class="{ on: ex.scope === 'cur' }" @click="ex.scope = 'cur'">Только текущая</button>
          </div>
        </div>
        <div v-if="hasWarn" class="note-warn">
          <span style="flex: none; color: #B07C1F">⚠</span>
          <span>Расписание неполное: не размещено пар — {{ unplacedN }}, проблем — {{ problemsN }}. Выгрузка не блокируется.</span>
        </div>
        <div class="preview mono">
          предпросмотр листа: сетка дни × пары, {{ ex.view === 'teacher' ? 'один преподаватель = один лист' : 'одна группа = один лист' }}
        </div>
      </div>
      <div v-else class="done">
        <span class="ok-circle">✓</span>
        <span class="done-title">Файл сформирован (мок)</span>
        <span class="done-file">{{ ex.fileName }}</span>
        <button class="btn" @click="ui.ex = null">Закрыть</button>
      </div>
      <template v-if="ex.step === 'config'" #footer>
        <button class="btn btn-lg" @click="ui.ex = null">Отмена</button>
        <span style="flex: 1"></span>
        <button class="btn-primary btn-lg" @click="run">Выгрузить в Excel</button>
      </template>
  </ModalWindow>
</template>

<style scoped>
.body { padding: 16px 18px; display: flex; flex-direction: column; gap: 14px; }
.fld { display: flex; flex-direction: column; gap: 6px; }
.row-btns { display: flex; gap: 6px; }
.rb { flex: 1; padding: 8px 0; font-size: 12.5px; }
.preview {
  border: 1px dashed rgba(0, 0, 0, 0.18);
  border-radius: var(--r-lg);
  padding: 14px;
  background: repeating-linear-gradient(45deg, #FBFAF8, #FBFAF8 6px, #F6F5F2 6px, #F6F5F2 12px);
  text-align: center;
  font: 400 11px var(--mono);
  color: var(--muted);
}
.done { padding: 36px 18px; display: flex; flex-direction: column; align-items: center; gap: 12px; }
.done-title { font-size: 13.5px; font-weight: 600; }
.done-file { font-size: 12px; color: var(--muted); }
</style>
