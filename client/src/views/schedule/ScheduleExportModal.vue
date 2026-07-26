<script setup>
import { computed } from 'vue'
import { store } from '../../store/index.js'
import { api } from '../../api/index.js'
import { kindShort, kindColor, kindLabel } from '../../utils/kinds.js'
import ModalWindow from '../../components/ModalWindow.vue'
import { ui, enriched, problemsN, dayIdxs, weeksCount, slotsN } from './useSchedule.js'

const ex = computed(() => ui.ex)
const view = computed(() => ex.value.view)

const teacherName = (id) => {
  const t = store.teacherById(id)
  return t ? t.name : ''
}

/* The lesson field that identifies a block in the chosen view: the effective
   teacher (substitute if any) for teacher view, else the group. */
const lessonKey = (l) => (view.value === 'teacher' ? (l.subBy || l.t) : l.g)

const scopeAllN = computed(() => (view.value === 'teacher' ? store.state.teachers.length : store.state.groups.length))

/* The concrete "current" entity, resolved against real store data so a stale
   default (e.g. seed teacher "t1") can never leak into the scope button or the
   request — falls back to the first available block. */
const curEntity = computed(() => {
  if (view.value === 'teacher') {
    const list = store.state.teachers
    const t = list.find((x) => x.id === ui.ent.teacher) || list[0]
    return t ? { key: t.id, name: t.name } : { key: null, name: '—' }
  }
  const list = store.state.groups
  const g = list.find((x) => x.name === ui.ent.group) || list[0]
  return g ? { key: g.name, name: g.name } : { key: null, name: '—' }
})

/* The blocks that will be stacked inside every day sheet. */
const entities = computed(() => {
  if (ex.value.scope === 'cur') return curEntity.value.key == null ? [] : [curEntity.value]
  if (view.value === 'teacher') return store.state.teachers.map((t) => ({ key: t.id, name: t.name }))
  return [...store.state.groups]
    .sort((a, b) => a.course - b.course || a.name.localeCompare(b.name))
    .map((g) => ({ key: g.name, name: g.name }))
})

const viewNoun = computed(() => (view.value === 'teacher' ? 'преподаватель' : 'группа'))
const viewNounPl = computed(() => (view.value === 'teacher' ? 'преподаватели' : 'группы'))
const viewNounGen = computed(() => (view.value === 'teacher' ? 'преподавателей' : 'групп'))

/* ---------- statistics of what the file will contain ---------- */

/* Placed lessons that fall inside the current view + scope. */
const scopedPlaced = computed(() => {
  const keys = new Set(entities.value.map((e) => e.key))
  return enriched.value.filter((l) => l.d != null && keys.has(lessonKey(l)))
})
const total = computed(() => scopedPlaced.value.length)

/* In-scope lessons that stay in the pool — they won't appear in the file. */
const unplacedInScope = computed(() => {
  const keys = new Set(entities.value.map((e) => e.key))
  return enriched.value.filter((l) => l.d == null && keys.has(lessonKey(l))).length
})

/* Composition by lesson type, largest first — the export's "what's inside". */
const byKind = computed(() => {
  const m = new Map()
  scopedPlaced.value.forEach((l) => m.set(l.kind, (m.get(l.kind) || 0) + 1))
  return [...m.entries()]
    .map(([k, n]) => ({ k, n, label: kindShort(k), title: kindLabel(k), color: kindColor(k) }))
    .sort((a, b) => b.n - a.n)
})
const pct = (n) => (total.value ? Math.round((n / total.value) * 100) : 0)

/* How many blocks actually carry at least one placed lesson. */
const filledEntities = computed(() => {
  const keys = new Set(scopedPlaced.value.map(lessonKey))
  return entities.value.filter((e) => keys.has(e.key)).length
})

const hasWarn = computed(() => unplacedInScope.value > 0 || problemsN.value > 0)

async function run() {
  const { exportId } = await api.exportSchedule({
    yearId: store.state.yearId,
    period: store.state.period,
    view: view.value,
    scope: ex.value.scope,
    entity: ex.value.scope === 'cur' ? curEntity.value.key : undefined,
    format: 'xlsx',
  })
  const info = await api.getExport(exportId)
  ui.ex = { ...ex.value, step: 'done', exportId, fileName: info.fileName }
  await api.downloadExport(exportId, info.fileName)
}

function redownload() {
  api.downloadExport(ex.value.exportId, ex.value.fileName)
}
</script>

<template>
  <ModalWindow v-if="ex" title="Экспорт расписания" :width="540" @close="ui.ex = null">
      <div v-if="ex.step === 'config'" class="body">
        <div class="fld">
          <span class="field-label">ПРЕДСТАВЛЕНИЕ</span>
          <div class="row-btns">
            <button class="pick-soft rb" :class="{ on: ex.view === 'group' }" @click="ex.view = 'group'">Расписание групп</button>
            <button class="pick-soft rb" :class="{ on: ex.view === 'teacher' }" @click="ex.view = 'teacher'">Расписание преподавателей</button>
          </div>
          <span class="fld-hint">{{ view === 'teacher'
            ? 'Лист на каждый день, блок на каждого преподавателя. В ячейке: дисциплина, тема, кабинет, группа.'
            : 'Лист на каждый день, блок на каждую группу. В ячейке: дисциплина, тема, кабинет, преподаватель.' }}</span>
        </div>

        <div class="fld">
          <span class="field-label">ОХВАТ</span>
          <div class="row-btns">
            <button class="pick-soft rb" :class="{ on: ex.scope === 'all' }" @click="ex.scope = 'all'">Все {{ viewNounPl }} ({{ scopeAllN }})</button>
            <button class="pick-soft rb" :class="{ on: ex.scope === 'cur' }" @click="ex.scope = 'cur'">Только «{{ curEntity.name }}»</button>
          </div>
        </div>

        <div class="fld">
          <span class="field-label">В ФАЙЛЕ БУДЕТ</span>
          <div class="stats">
            <div class="stat-row">
              <div class="stat"><b>{{ total }}</b><span>{{ total === 1 ? 'занятие' : 'занятий' }}</span></div>
              <div class="stat"><b>{{ dayIdxs.length }}</b><span>{{ dayIdxs.length === 1 ? 'лист' : 'листов' }}</span></div>
              <div class="stat"><b>{{ entities.length }}</b><span>{{ entities.length === 1 ? 'блок' : 'блоков' }}</span></div>
              <div class="stat"><b>{{ weeksCount }}×{{ slotsN }}</b><span>недель×пар</span></div>
            </div>

            <template v-if="total">
              <div class="stat-bar">
                <span
                  v-for="row in byKind"
                  :key="row.k"
                  class="seg"
                  :style="{ width: pct(row.n) + '%', background: row.color }"
                  :title="row.title + ': ' + row.n"
                ></span>
              </div>
              <div class="stat-legend">
                <span v-for="row in byKind" :key="row.k" class="lg" :title="row.title">
                  <span class="lg-dot" :style="{ background: row.color }"></span>
                  <span class="lg-lbl">{{ row.label }}</span>
                  <span class="lg-n mono">{{ row.n }}</span>
                </span>
              </div>
              <div v-if="ex.scope === 'all'" class="stat-cov mono">
                занятия есть у {{ filledEntities }} из {{ entities.length }} {{ viewNounGen }}
              </div>
            </template>
            <div v-else class="stat-empty mono">нет размещённых занятий — листы будут пустой сеткой</div>
          </div>
        </div>

        <div v-if="hasWarn" class="note-warn">
          <span style="flex: none; color: #B07C1F">⚠</span>
          <span>
            <template v-if="unplacedInScope">Не попадёт в файл: {{ unplacedInScope }} неразмещённых пар{{ problemsN ? '. ' : '.' }}</template>
            <template v-if="problemsN">Проблем в расписании — {{ problemsN }}.</template>
            Выгрузка не блокируется.
          </span>
        </div>
      </div>
      <div v-else class="done">
        <span class="ok-circle">✓</span>
        <span class="done-title">Файл сформирован</span>
        <span class="done-file">{{ ex.fileName }}</span>
        <div class="row-btns">
          <button class="btn" @click="redownload">Скачать ещё раз</button>
          <button class="btn-primary" @click="ui.ex = null">Готово</button>
        </div>
      </div>
      <template v-if="ex.step === 'config'" #footer>
        <button class="btn btn-lg" @click="ui.ex = null">Отмена</button>
        <span style="flex: 1"></span>
        <button class="btn-primary btn-lg" @click="run">Выгрузить в Excel</button>
      </template>
  </ModalWindow>
</template>

<style scoped>
.body { padding: 16px 18px; display: flex; flex-direction: column; gap: 16px; }
.fld { display: flex; flex-direction: column; gap: 6px; }
.fld-hint { font-size: 11px; color: var(--faint); line-height: 1.4; }
.row-btns { display: flex; gap: 6px; }
.rb { flex: 1; padding: 8px 0; font-size: 12.5px; }

/* ---- statistics ---- */
.stats {
  border: 1px solid var(--line-soft);
  border-radius: var(--r-lg);
  background: #FBFAF8;
  padding: 12px 14px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.stat-row { display: flex; gap: 8px; }
.stat {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  padding: 8px 4px;
  background: #FFF;
  border: 1px solid var(--line-soft);
  border-radius: var(--r-md);
}
.stat b { font-size: 18px; font-weight: 700; color: var(--fg); line-height: 1; }
.stat span { font-size: 10px; color: var(--muted); }

.stat-bar {
  display: flex;
  height: 10px;
  border-radius: 5px;
  overflow: hidden;
  background: #ECEAE4;
}
.seg { min-width: 2px; }
.seg + .seg { box-shadow: -1px 0 0 rgba(255, 255, 255, 0.6); }

.stat-legend { display: flex; flex-wrap: wrap; gap: 4px 12px; }
.lg { display: inline-flex; align-items: center; gap: 5px; }
.lg-dot { width: 8px; height: 8px; border-radius: 2px; flex: none; }
.lg-lbl { font-size: 11px; color: var(--sub); }
.lg-n { font: 600 10.5px var(--mono); color: var(--fg); }

.stat-cov { font: 400 10px var(--mono); color: var(--faint); }
.stat-empty { font: 400 11px var(--mono); color: var(--faint); text-align: center; padding: 4px 0; }

.done { padding: 36px 18px; display: flex; flex-direction: column; align-items: center; gap: 12px; }
.done-title { font-size: 13.5px; font-weight: 600; }
.done-file { font-size: 12px; color: var(--muted); }
</style>
