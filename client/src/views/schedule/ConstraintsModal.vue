<script setup>
import { computed } from 'vue'
import { store } from '../../store/index.js'
import ModalWindow from '../../components/ModalWindow.vue'
import InfoDot from '../../components/InfoDot.vue'
import AvailabilityEditor from '../../components/AvailabilityEditor.vue'
import AbsenceEditor from '../../components/AbsenceEditor.vue'
import { ui } from './useSchedule.js'

const cur = computed(() => store.teacherById(ui.co.tid) || store.state.teachers[0])

const list = computed(() => store.state.teachers.map((t) => ({
  t,
  status: t.c ? 'заданы' : 'не заданы',
  on: cur.value && t.id === cur.value.id,
})))
</script>

<template>
  <ModalWindow v-if="ui.co" title="Доступность преподавателей" :width="720" @close="ui.co = null">
    <div class="split">
      <div class="side">
        <div
          v-for="row in list"
          :key="row.t.id"
          class="side-row"
          :class="{ on: row.on }"
          @click="ui.co = { tid: row.t.id }"
        >
          <span class="side-name" :style="{ fontWeight: row.on ? 600 : 400 }">{{ row.t.name }}</span>
          <span class="side-status mono" :class="row.t.c ? 'ok' : 'warn'">{{ row.status }}</span>
        </div>
      </div>
      <div v-if="cur" class="detail">
        <div class="d-name">{{ cur.name }}</div>
        <div class="sect">
          <div class="sect-head">
            <span class="micro">НЕДОСТУПНЫЕ И НЕЖЕЛАТЕЛЬНЫЕ СЛОТЫ</span>
            <InfoDot :size="15" tip="Клик по клетке циклит состояние: свободно → недоступно → нежелательно." />
          </div>
          <AvailabilityEditor :teacher="cur" />
        </div>
        <div class="sect abs-sect">
          <div class="sect-head">
            <span class="micro">ПЕРИОДЫ ОТСУТСТВИЯ</span>
            <InfoDot :size="15" tip="Отпуск, больничный, командировка — блокируют даты для генератора и проверки конфликтов." />
          </div>
          <AbsenceEditor :teacher="cur" />
        </div>
        <div class="foot-hint">
          Жёсткие ограничения генератор не нарушает; нежелательные слоты постарается избежать.
          Периоды отсутствия исключают даты из расписания. Изменения сразу учитываются в проверке конфликтов.
        </div>
      </div>
    </div>
  </ModalWindow>
</template>

<style scoped>
.split { flex: 1; display: flex; min-height: 0; max-height: 76vh; }
.side {
  flex: none;
  width: 230px;
  border-right: 1px solid rgba(0, 0, 0, 0.08);
  overflow-y: auto;
  padding: 8px;
}
.side-row {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 7px 10px;
  border-radius: var(--r-md);
  cursor: pointer;
}
.side-row:hover { background: var(--chip); }
.side-row.on { background: var(--active); }
.side-name {
  font-size: 12.5px;
  flex: 1;
  min-width: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.side-status { flex: none; font: 500 9.5px var(--mono); border-radius: 4px; padding: 1px 6px; }
.side-status.ok { color: var(--green); background: rgba(31, 138, 91, 0.08); }
.side-status.warn { color: var(--amber); background: rgba(176, 124, 31, 0.08); }

.detail { flex: 1; overflow-y: auto; padding: 16px 18px; display: flex; flex-direction: column; gap: 14px; }
.d-name { font-size: 14px; font-weight: 600; }
.sect { display: flex; flex-direction: column; gap: 6px; }
.sect-head { display: flex; align-items: center; gap: 6px; }
.abs-sect { border-top: 1px solid rgba(0, 0, 0, 0.08); padding-top: 12px; gap: 10px; }
.foot-hint {
  border-top: 1px dashed rgba(0, 0, 0, 0.12);
  padding-top: 10px;
  font-size: 11.5px;
  color: var(--muted);
  line-height: 1.55;
}
</style>
