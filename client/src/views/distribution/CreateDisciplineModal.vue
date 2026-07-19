<script setup>
import { computed, ref, watch, nextTick } from 'vue'
import { store } from '../../store/index.js'
import ModalWindow from '../../components/ModalWindow.vue'
import InfoDot from '../../components/InfoDot.vue'
import { dui } from './useDistribution.js'

const nameEl = ref(null)

watch(() => dui.cd, async (cd) => {
  if (cd) {
    await nextTick()
    if (nameEl.value) nameEl.value.focus()
  }
})

const cd = computed(() => dui.cd)

const groupOpts = computed(() => store.state.groups.map((g) => g.id))

const selectedGroup = computed(() => store.groupById((cd.value.group || '').trim()))

const totalHours = computed(() => cd.value.topics.reduce((h, t) => h + (Number(t.hours) || 0), 0))

const valid = computed(() => !!(
  cd.value
  && cd.value.name.trim()
  && selectedGroup.value
  && cd.value.topics.some((t) => t.name.trim() && Number(t.hours) > 0)
))

function addTopicRow() {
  cd.value.topics.push({ kind: 'lec', name: '', hours: 24 })
}

function removeTopicRow(i) {
  cd.value.topics.splice(i, 1)
}

async function save() {
  const c = cd.value
  if (!c.name.trim()) { c.error = 'Укажите название дисциплины'; return }
  if (!selectedGroup.value) { c.error = 'Выберите группу из справочника'; return }
  const topics = c.topics
    .filter((t) => t.name.trim() && Number(t.hours) > 0)
    .map((t) => ({ kind: t.kind, name: t.name.trim(), hours: Number(t.hours) }))
  if (!topics.length) { c.error = 'Добавьте хотя бы одну тему с названием и часами'; return }
  const payload = { name: c.name.trim(), groupId: selectedGroup.value.id, period: c.period, topics }
  const d = await store.createDiscipline(payload)
  store.setPeriod(c.period)
  dui.expDisc = { ...dui.expDisc, [d.id]: true }
  dui.cd = null
}
</script>

<template>
  <ModalWindow v-if="cd" title="Новая дисциплина" :width="620" @close="dui.cd = null">
    <div class="body">
      <div class="row">
        <div class="fld" style="flex: 2">
          <span class="lbl">Название дисциплины</span>
          <input
            ref="nameEl"
            v-model="cd.name"
            class="input"
            placeholder="Например: Базы данных"
            @input="cd.error = ''"
          >
        </div>
        <div class="fld" style="flex: 1">
          <span class="lbl">Группа</span>
          <input
            v-model="cd.group"
            class="input"
            list="cd-groups"
            placeholder="ИС-21"
            @input="cd.error = ''"
          >
          <datalist id="cd-groups">
            <option v-for="g in groupOpts" :key="g" :value="g"></option>
          </datalist>
        </div>
      </div>
      <div class="row row-meta">
        <div class="fld">
          <span class="lbl">Семестр</span>
          <div class="row-btns">
            <button class="pick pb" :class="{ on: cd.period === 'fall' }" @click="cd.period = 'fall'">Осень</button>
            <button class="pick pb" :class="{ on: cd.period === 'spring' }" @click="cd.period = 'spring'">Весна</button>
          </div>
        </div>
        <div class="fld">
          <span class="lbl">Курс</span>
          <span class="course-chip mono">{{ selectedGroup ? selectedGroup.course + ' курс (из группы)' : '— выберите группу' }}</span>
        </div>
        <div class="total mono">Итого: {{ totalHours }} ч</div>
      </div>

      <div class="fld">
        <div class="topics-head">
          <span class="lbl">Темы</span>
          <InfoDot :size="15" tip="Каждая тема — лекция или практика; назначается своему преподавателю." />
        </div>
        <div class="topics-box">
          <div v-for="(tp, i) in cd.topics" :key="i" class="topic-row">
            <div class="seg seg-sm">
              <button :class="{ on: tp.kind === 'lec' }" :style="tp.kind === 'lec' ? { color: '#3B62C4' } : {}" @click="tp.kind = 'lec'">Лекция</button>
              <button :class="{ on: tp.kind === 'prac' }" :style="tp.kind === 'prac' ? { color: '#1F8A5B' } : {}" @click="tp.kind = 'prac'">Практика</button>
            </div>
            <input v-model="tp.name" class="input topic-name" placeholder="Название темы" @input="cd.error = ''">
            <input v-model="tp.hours" class="input topic-hours mono" type="number" min="0">
            <span class="hours-unit">ч</span>
            <span class="rm" title="Удалить тему" @click="removeTopicRow(i)">×</span>
          </div>
          <div class="add-topic" @click="addTopicRow"><span class="plus">＋</span>Добавить тему</div>
        </div>
      </div>
    </div>
    <template #footer>
      <span class="err">{{ cd.error }}</span>
      <button class="btn btn-lg" @click="dui.cd = null">Отмена</button>
      <button class="btn-primary btn-lg" :disabled="!valid" @click="save">Создать дисциплину</button>
    </template>
  </ModalWindow>
</template>

<style scoped>
.body { flex: 1; overflow-y: auto; padding: 16px 18px; display: flex; flex-direction: column; gap: 14px; }
.row { display: flex; gap: 12px; }
.row-meta { align-items: flex-end; flex-wrap: wrap; gap: 16px; }
.fld { display: flex; flex-direction: column; gap: 6px; min-width: 0; }
.lbl { font-size: 12px; font-weight: 600; color: var(--sub); }
.row-btns { display: flex; gap: 4px; }
.pb { padding: 0 16px; height: 32px; }
.course-chip { font: 500 12px var(--mono); color: var(--sub); background: var(--chip); border-radius: 6px; padding: 8px 10px; }
.total { flex: 1; text-align: right; font: 500 12px var(--mono); color: var(--sub); align-self: flex-end; padding-bottom: 8px; }

.topics-head { display: flex; align-items: center; gap: 7px; }
.topics-box { border: 1px solid rgba(0, 0, 0, 0.1); border-radius: var(--r-lg); overflow: hidden; }
.topic-row {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 10px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}
.seg-sm button { font-size: 11px; padding: 3px 9px; border-radius: 5px; }
.topic-name { flex: 1; min-width: 0; font-size: 12.5px; padding: 6px 9px; border-radius: var(--r-sm); }
.topic-hours { width: 64px; flex: none; font: 500 12.5px var(--mono); text-align: right; padding: 6px 8px; border-radius: var(--r-sm); }
.hours-unit { font-size: 11px; color: var(--faint); flex: none; }
.rm { flex: none; color: var(--dim); cursor: pointer; font-size: 16px; line-height: 1; padding: 0 2px; }
.rm:hover { color: var(--orange-dark); }
.add-topic {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 10px;
  cursor: pointer;
  color: var(--blue);
  font-size: 12.5px;
  font-weight: 500;
}
.add-topic:hover { background: var(--hover); }
.plus { font-size: 14px; line-height: 1; }
.err { font-size: 12px; color: var(--orange-dark); flex: 1; }
</style>
