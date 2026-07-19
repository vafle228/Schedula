<script setup>
import { computed } from 'vue'
import { store } from '../../store/index.js'
import { api } from '../../api/index.js'
import ModalWindow from '../../components/ModalWindow.vue'
import InfoDot from '../../components/InfoDot.vue'
import { dui, teacherOfTopic, kindShort } from './useDistribution.js'

const exp = computed(() => dui.exp)

const periodBtns = [
  { k: 'fall', label: 'Осень' },
  { k: 'spring', label: 'Весна' },
  { k: 'both', label: 'Оба периода' },
]

const allRows = computed(() => {
  if (!exp.value) return []
  const rows = []
  store.state.disciplines
    .filter((d) => exp.value.period === 'both' || d.period === exp.value.period)
    .forEach((d) => d.topics.forEach((tp) => {
      const tid = teacherOfTopic(tp.id)
      const t = tid ? store.teacherById(tid) : null
      rows.push({
        disc: d.name + ', ' + tp.name,
        group: d.groupId,
        kind: kindShort(tp.kind),
        hours: String(tp.hours),
        teacher: t ? t.name : '— не назначено',
        assigned: !!t,
      })
    }))
  return rows
})

const warnCount = computed(() => allRows.value.filter((r) => !r.assigned).length)
const shownRows = computed(() => allRows.value.slice(0, 5))
const moreLabel = computed(() => (allRows.value.length > 5
  ? '… и ещё ' + (allRows.value.length - 5) + ' строк'
  : 'Все строки показаны'))

function showWarn() {
  const p = exp.value.period
  dui.exp = null
  dui.fStatus = 'open'
  dui.fKind = 'all'
  dui.fCourse = 'all'
  dui.search = ''
  if (p !== 'both') store.setPeriod(p)
}

let genTimer = null
async function start() {
  const period = exp.value.period
  dui.exp = { ...exp.value, step: 'gen' }
  const { exportId } = await api.exportCurriculum(period)
  const info = await api.getExport(exportId)
  genTimer = setTimeout(() => {
    if (dui.exp) dui.exp = { ...dui.exp, step: 'done', fileName: info.fileName }
  }, 1400)
}

function close() {
  clearTimeout(genTimer)
  dui.exp = null
}
</script>

<template>
  <ModalWindow v-if="exp" title="Экспорт в Excel — государственный шаблон" :width="580" @close="close">
    <template v-if="exp.step === 'config'">
      <div class="body">
        <div class="fld">
          <span class="lbl">Период</span>
          <div class="row-btns">
            <button
              v-for="p in periodBtns"
              :key="p.k"
              class="pick pb"
              :class="{ on: exp.period === p.k }"
              @click="exp.period = p.k"
            >{{ p.label }}</button>
          </div>
        </div>
        <div v-if="warnCount > 0" class="warn-box">
          <span class="warn-ico">⚠</span>
          <span class="warn-text">{{ warnCount }} тем не назначено. Файл можно сформировать — строки останутся без преподавателя.</span>
          <span class="warn-show" @click="showWarn">Показать</span>
        </div>
        <div class="fld">
          <div class="prev-head">
            <span class="lbl">Предпросмотр</span>
            <InfoDot :size="15" tip="Строка = тема; структура шаблона условная." />
          </div>
          <div class="prev-box">
            <div class="prev-thead mono">
              <span style="flex: 2">ДИСЦИПЛИНА / ТЕМА</span>
              <span class="col-group">ГРУППА</span>
              <span class="col-kind">ВИД</span>
              <span class="col-hours">ЧАСЫ</span>
              <span style="flex: 1.3; text-align: right">ПРЕПОДАВАТЕЛЬ</span>
            </div>
            <div v-for="(r, i) in shownRows" :key="i" class="prev-row">
              <span class="ellip" style="flex: 2">{{ r.disc }}</span>
              <span class="col-group muted">{{ r.group }}</span>
              <span class="col-kind muted">{{ r.kind }}</span>
              <span class="col-hours mono">{{ r.hours }}</span>
              <span
                class="ellip"
                style="flex: 1.3; text-align: right"
                :style="{ color: r.assigned ? '#3A382F' : '#B45309' }"
              >{{ r.teacher }}</span>
            </div>
            <div class="prev-more">{{ moreLabel }}</div>
          </div>
        </div>
        <div class="actions">
          <button class="btn btn-lg" @click="close">Отмена</button>
          <button class="btn-primary btn-lg" @click="start">Сформировать файл</button>
        </div>
      </div>
    </template>
    <template v-else-if="exp.step === 'gen'">
      <div class="center">
        <span class="spinner"></span>
        <span class="gen-text">Формируем файл по шаблону…</span>
      </div>
    </template>
    <template v-else>
      <div class="center done">
        <span class="ok-circle">✓</span>
        <span class="done-title">Файл сохранён</span>
        <span class="done-file mono">{{ exp.fileName }}</span>
        <div class="done-btns">
          <button class="btn" @click="close">Открыть файл</button>
          <button class="btn-primary" @click="close">Готово</button>
        </div>
      </div>
    </template>
  </ModalWindow>
</template>

<style scoped>
.body { padding: 16px 18px; display: flex; flex-direction: column; gap: 14px; }
.fld { display: flex; flex-direction: column; gap: 7px; }
.lbl { font-size: 12px; font-weight: 600; color: var(--sub); }
.row-btns { display: flex; gap: 4px; }
.pb { padding: 6px 14px; font-size: 12.5px; }

.warn-box {
  display: flex;
  align-items: center;
  gap: 10px;
  border: 1px solid rgba(217, 119, 6, 0.4);
  background: rgba(217, 119, 6, 0.05);
  border-radius: var(--r-lg);
  padding: 10px 12px;
}
.warn-ico { color: var(--orange-dark); font-size: 14px; flex: none; }
.warn-text { font-size: 12.5px; color: #3A382F; flex: 1; }
.warn-show { font-size: 12px; font-weight: 500; color: var(--blue); cursor: pointer; flex: none; }

.prev-head { display: flex; align-items: center; gap: 7px; }
.prev-box { border: 1px solid rgba(0, 0, 0, 0.1); border-radius: var(--r-lg); overflow: hidden; }
.prev-thead {
  display: flex;
  background: var(--hover);
  border-bottom: 1px solid rgba(0, 0, 0, 0.08);
  font: 500 10.5px var(--mono);
  color: var(--muted);
  padding: 6px 12px;
  gap: 8px;
}
.prev-row {
  display: flex;
  padding: 5px 12px;
  gap: 8px;
  font-size: 11.5px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.04);
  color: #3A382F;
}
.col-group { flex: none; width: 52px; }
.col-kind { flex: none; width: 48px; }
.col-hours { flex: none; width: 36px; text-align: right; }
.muted { color: var(--muted); }
.ellip { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.prev-more { padding: 5px 12px; font-size: 11px; color: var(--faint); }

.actions { display: flex; justify-content: flex-end; gap: 8px; padding-top: 2px; }
.center { padding: 44px 18px; display: flex; flex-direction: column; align-items: center; gap: 14px; }
.gen-text { font-size: 13px; color: var(--sub); }
.done { padding: 36px 18px; gap: 12px; }
.done-title { font-size: 14px; font-weight: 600; }
.done-file { font: 400 12px var(--mono); color: var(--muted); }
.done-btns { display: flex; gap: 8px; margin-top: 6px; }
</style>
