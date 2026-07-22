<script setup>
import { computed, ref, watch, nextTick } from 'vue'
import { store } from '../../store/index.js'
import ModalWindow from '../../components/ModalWindow.vue'
import InfoDot from '../../components/InfoDot.vue'
import { dui, KINDS } from './useDistribution.js'

const nameEl = ref(null)

watch(() => dui.cd, async (cd) => {
  if (cd) {
    await nextTick()
    if (nameEl.value) nameEl.value.focus()
  }
})

const cd = computed(() => dui.cd)

const groupOpts = computed(() => store.state.groups.map((g) => ({ v: g.id, label: g.id + ' · ' + g.course + ' курс' })))

const selectedGroup = computed(() => store.groupById((cd.value.group || '').trim()))

const totalHours = computed(() => cd.value.topics.reduce((h, t) => h + (Number(t.hours) || 0), 0))

/* Курс и семестр не редактируются в форме: курс берётся из выбранной группы,
   семестр — активный (Итерация 5.1). */
const courseLabel = computed(() => (selectedGroup.value ? selectedGroup.value.course + ' курс' : 'зависит от группы'))
const semesterLabel = computed(() => (store.state.period === 'fall' ? 'осенний семестр' : 'весенний семестр'))

// единственный блокер — непустое название; дисциплина без группы разрешена
const valid = computed(() => !!(cd.value && cd.value.name.trim()))

function addTopicRow() {
  cd.value.topics.push({ kind: 'lec', name: '', hours: 24 })
}

function removeTopicRow(i) {
  cd.value.topics.splice(i, 1)
}

async function save() {
  const c = cd.value
  if (!c.name.trim()) { c.error = 'Укажите название дисциплины'; return }
  // пустые строки тем молча отбрасываются; дисциплина без тем разрешена
  const topics = c.topics
    .filter((t) => t.name.trim() && Number(t.hours) > 0)
    .map((t) => ({ kind: t.kind, name: t.name.trim(), hours: Number(t.hours) }))
  const groupId = selectedGroup.value ? selectedGroup.value.id : 'Без группы'
  const payload = { name: c.name.trim(), groupId, period: store.state.period, topics }
  const d = await store.createDiscipline(payload)
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
          <div class="select-wrap">
            <select v-model="cd.group" @change="cd.error = ''">
              <option value="">Без группы</option>
              <option v-for="g in groupOpts" :key="g.v" :value="g.v">{{ g.label }}</option>
            </select>
            <span class="chev">▾</span>
          </div>
        </div>
      </div>

      <!-- read-only auto-context: курс из группы, семестр активный -->
      <div class="ctx">
        <span class="ctx-lead mono">определяются автоматически:</span>
        <span class="ctx-chip"><span class="ctx-k mono">Курс</span>{{ courseLabel }}</span>
        <span class="ctx-chip"><span class="ctx-k mono">Семестр</span>{{ semesterLabel }}</span>
        <span class="sp"></span>
        <span class="ctx-total mono">Итого: {{ totalHours }} ч</span>
      </div>
      <div class="fld">
        <div class="topics-head">
          <span class="lbl">Темы</span>
          <InfoDot :size="15" tip="Каждая тема — занятие своего вида; назначается своему преподавателю. Дисциплину можно создать и без тем — добавите позже." />
          <span class="sp"></span>
          <span class="count mono">{{ cd.topics.filter((t) => t.name.trim()).length }}/{{ cd.topics.length }}</span>
        </div>
        <div class="topics-box">
          <div class="topics-list">
            <div v-for="(tp, i) in cd.topics" :key="i" class="topic-row">
              <div class="select-wrap kind-sel">
                <select v-model="tp.kind">
                  <option v-for="k in KINDS" :key="k.k" :value="k.k">{{ k.label }}</option>
                </select>
                <span class="chev">▾</span>
              </div>
              <input v-model="tp.name" class="input topic-name" placeholder="Название темы" @input="cd.error = ''">
              <input v-model="tp.hours" class="input topic-hours mono" type="number" min="0">
              <span class="hours-unit">ч</span>
              <span class="rm" title="Удалить тему" @click="removeTopicRow(i)">×</span>
            </div>
            <div v-if="!cd.topics.length" class="topics-empty">Тем пока нет — добавьте ниже или позже, в списке дисциплин.</div>
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
.fld { display: flex; flex-direction: column; gap: 6px; min-width: 0; }
.lbl { font-size: 12px; font-weight: 600; color: var(--sub); }
.sp { flex: 1; }
.count { font: 500 11px var(--mono); color: var(--muted); background: var(--chip); border-radius: 10px; padding: 1px 7px; }

.ctx {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  background: #FBFAF8;
  border: 1px solid rgba(0, 0, 0, 0.07);
  border-radius: var(--r-md);
  padding: 8px 11px;
}
.ctx-lead { font: 400 10.5px var(--mono); color: var(--faint); }
.ctx-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: var(--chip);
  border-radius: 5px;
  padding: 3px 8px;
  font-size: 12px;
  color: var(--sub);
}
.ctx-k { font: 500 9.5px var(--mono); letter-spacing: 0.05em; color: var(--faint); }
.ctx-total { font: 500 12px var(--mono); color: var(--sub); }

.topics-head { display: flex; align-items: center; gap: 7px; }
.topics-box { border: 1px solid rgba(0, 0, 0, 0.1); border-radius: var(--r-lg); overflow: hidden; }
.topics-list { max-height: 240px; overflow-y: auto; }
.topics-list .topic-row:last-child { border-bottom: none; }
.add-topic { border-top: 1px solid rgba(0, 0, 0, 0.05); }
.topic-row {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 10px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}
.kind-sel { flex: none; width: 142px; }
.kind-sel select { padding: 6px 24px 6px 9px; font-size: 12px; font-weight: 500; border-radius: var(--r-sm); }
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
.topics-empty {
  padding: 12px 12px 4px;
  font-size: 12px;
  color: var(--dim);
  text-align: center;
}
.plus { font-size: 14px; line-height: 1; }
.err { font-size: 12px; color: var(--orange-dark); flex: 1; }
</style>
