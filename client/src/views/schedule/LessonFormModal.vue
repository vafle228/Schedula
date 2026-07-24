<script setup>
import { computed } from 'vue'
import { store } from '../../store/index.js'
import { confirmDelete } from '../../composables/useConfirm.js'
import { KINDS, ALL_DAYS, kindOf } from '../../utils/kinds.js'
import ModalWindow from '../../components/ModalWindow.vue'
import InfoDot from '../../components/InfoDot.vue'
import { ui, dayIdxs, slotsN, bells, statusFor, asgOptions, flash, ST_COLORS, weeksCount, dateFor } from './useSchedule.js'

const lf = computed(() => ui.lf)
const isEdit = computed(() => !!(lf.value && lf.value.id))
const editL = computed(() => (isEdit.value ? store.enriched.value.find((l) => l.id === lf.value.id) : null))

const curAsg = computed(() => {
  if (isEdit.value) {
    if (!editL.value) return null
    const t = store.teacherById(editL.value.t)
    return { label: editL.value.disc + ', ' + editL.value.g, sub: t ? t.name : '' }
  }
  const a = asgOptions.value[parseInt(lf.value.asg)]
  if (!a) return null
  return { label: a.discipline.name + ', ' + a.groupName, sub: a.teacherName, a }
})

const weekOpts = computed(() => Array.from({ length: weeksCount.value }, (_, i) => ({ v: String(i + 1), label: 'Неделя ' + (i + 1) })))
const dayOpts = computed(() => dayIdxs.value.map((i) => ({ v: String(i), label: ALL_DAYS[i] })))
const slotOpts = computed(() => Array.from({ length: slotsN.value }, (_, i) => {
  const b = bells.value[i] || { from: '', to: '', hours: 2 }
  return { v: String(i), label: (i + 1) + ' пара · ' + b.from + '–' + b.to + ' · ' + b.hours + ' ак.ч' }
}))
const roomOpts = computed(() => store.state.rooms.map((r) => ({ v: r.id, label: r.id + ', ' + r.type + ', ' + r.capacity })))

/* Substitution (замена): staff teacher first, then the rest. Picking another
   than штатный marks the occurrence as a замена for this week only. */
const teacherOpts = computed(() => {
  if (!isEdit.value || !lf.value) return []
  const staff = lf.value.staffTeacher
  const st = store.teacherById(staff)
  const opts = [{ v: staff, label: (st ? st.name : '') + ' · штатный' }]
  store.state.teachers.filter((t) => t.id !== staff).forEach((t) => opts.push({ v: t.id, label: t.name }))
  return opts
})
const isSub = computed(() => !!(lf.value && isEdit.value && lf.value.teacher !== lf.value.staffTeacher))

/* Header dot + meta line for the detail card (Итерация 8). */
const editKind = computed(() => (editL.value ? kindOf(editL.value.kind) : null))
const editMeta = computed(() => {
  const l = editL.value
  if (!l) return ''
  if (l.d == null) return l.g + ' · в пуле'
  const bell = bells.value[l.s] || { from: '', to: '' }
  return l.g + ' · ' + ALL_DAYS[l.d] + ' ' + dateFor(l.w, l.d) + ' · ' + bell.from + '–' + bell.to
})

/* Reuse already-authored topics / questions as autocomplete suggestions. */
const topicBank = computed(() => [...new Set(store.enriched.value.map((l) => l.topic).filter(Boolean))])
const qBank = computed(() => [...new Set(store.enriched.value.map((l) => l.question).filter((q) => q && q !== '—'))])

const status = computed(() => {
  const f = lf.value
  if (!f || !f.placed) return { kind: 'free', text: '' }
  let probe
  if (isEdit.value) {
    if (!editL.value) return { kind: 'free', text: '' }
    probe = { id: f.id, t: editL.value.t, subBy: isSub.value ? f.teacher : null, g: editL.value.g, room: f.r, kind: f.kind }
  } else {
    const a = curAsg.value && curAsg.value.a
    if (!a) return { kind: 'free', text: '' }
    probe = { id: '__new', t: a.teacherId, subBy: null, g: a.groupName, room: f.r, kind: f.kind }
  }
  return statusFor(probe, parseInt(f.w), parseInt(f.d), parseInt(f.s), f.r)
})
const sc = computed(() => ST_COLORS[status.value.kind])

function pickAsg(e) {
  const a = asgOptions.value[parseInt(e.target.value)]
  ui.lf = { ...lf.value, asg: e.target.value, r: a ? a.defaultRoom : lf.value.r, err: '' }
}

async function save() {
  const f = lf.value
  const topic = f.topic.trim()
  if (!topic) { f.err = 'Укажите тему занятия'; return }
  if (f.placed && status.value.kind === 'unfit') { f.err = 'Слот на 1 ак.ч — выберите слот на 2 ак.ч'; return }
  const question = f.question.trim()

  if (isEdit.value) {
    const fields = { kind: f.kind, topicLabel: topic, question, number: f.number ? parseInt(f.number) : null }
    if (f.placed) {
      fields.week = parseInt(f.w)
      fields.day = parseInt(f.d)
      fields.slot = parseInt(f.s)
      fields.roomId = f.r
      fields.subBy = isSub.value ? f.teacher : null
    } else {
      fields.week = null
      fields.day = null
      fields.slot = null
      fields.subBy = null
    }
    const id = f.id
    ui.lf = null
    await store.updateLesson(id, fields)
    flash(id)
    return
  }

  const a = curAsg.value && curAsg.value.a
  if (!a) return
  const unitTopic = a.topics.find((tp) => tp.kind === f.kind) || a.topics[0]
  if (store.planRemaining(a.groupId, unitTopic.id) <= 0) {
    const planH = store.topicPlanCount(unitTopic.id) * kindOf(f.kind).acHours
    f.err = `План по этому типу занятий исчерпан — отведено ${planH} ч`
    return
  }
  const payload = {
    topicId: unitTopic.id,
    disciplineId: a.discipline.id,
    groupId: a.groupId,
    teacherId: a.teacherId,
    roomId: f.r || a.defaultRoom,
    kind: f.kind,
    period: store.state.period,
    week: f.placed ? parseInt(f.w) : null,
    day: f.placed ? parseInt(f.d) : null,
    slot: f.placed ? parseInt(f.s) : null,
    subBy: null,
    ni: 1,
    nt: 1,
    topicLabel: topic,
    question,
    number: f.number ? parseInt(f.number) : null,
  }
  ui.lf = null
  if (payload.day != null && ui.view === 'group' && a.groupName !== ui.ent.group) {
    ui.ent.group = a.groupName
  }
  const created = await store.createManualLesson(payload)
  flash(created.id)
}

async function del() {
  const l = editL.value
  const id = lf.value.id
  const ok = await confirmDelete({
    title: 'Удалить занятие?',
    message: 'Занятие будет удалено из расписания. Действие необратимо.',
    entityName: l ? [l.disc, l.g].filter(Boolean).join(' · ') : '',
  })
  if (!ok) return
  ui.lf = null
  ui.sel = []
  await store.deleteLesson(id)
}
</script>

<template>
  <ModalWindow
    v-if="lf"
    :title="isEdit ? 'Карточка занятия' : 'Новое занятие'"
    :width="isEdit ? 560 : 490"
    @close="ui.lf = null"
  >
    <template v-if="isEdit && editL" #title>
      <span class="hdr-dot" :style="{ background: editKind ? editKind.color : '#8A857C' }"></span>
      <div class="hdr-txt">
        <div class="hdr-head">{{ editL.disc }} · {{ editKind ? editKind.label : '' }}</div>
        <div class="hdr-meta mono">{{ editMeta }}</div>
      </div>
    </template>

    <!-- ===== detail card (editing an existing lesson) ===== -->
    <div v-if="isEdit" class="body">
      <div class="three">
        <div class="fld fld--num-sm">
          <span class="field-label">№</span>
          <input
            v-model="lf.number"
            class="input input--white"
            type="number"
            min="1"
            placeholder="—"
          >
        </div>
        <div class="fld f2">
          <span class="field-label">ТЕМА *</span>
          <input
            v-model="lf.topic"
            class="input input--white"
            list="lf-topic-bank"
            placeholder="начните вводить…"
            @input="lf.err = ''"
          >
        </div>
        <div class="fld f15">
          <span class="field-label">УЧЕБНЫЙ ВОПРОС</span>
          <input
            v-model="lf.question"
            class="input input--white"
            list="lf-q-bank"
            placeholder="один вопрос…"
          >
        </div>
      </div>
      <datalist id="lf-topic-bank"><option v-for="t in topicBank" :key="t" :value="t"></option></datalist>
      <datalist id="lf-q-bank"><option v-for="q in qBank" :key="q" :value="q"></option></datalist>
      <div class="hint">Тема и вопрос переиспользуются из уже заведённых — выберите существующую из списка; новое создаётся при сохранении.</div>

      <template v-if="lf.placed">
        <div class="row-end">
          <div class="fld f1">
            <span class="field-label">Аудитория</span>
            <div class="select-wrap">
              <select v-model="lf.r"><option v-for="o in roomOpts" :key="o.v" :value="o.v">{{ o.label }}</option></select>
              <span class="chev">▾</span>
            </div>
          </div>
          <div class="fld f12" title="Выбор другого преподавателя = замена на этот урок">
            <span class="field-label">Преподаватель</span>
            <div class="select-wrap">
              <select v-model="lf.teacher" :class="{ 'sub-on': isSub }"><option v-for="o in teacherOpts" :key="o.v" :value="o.v">{{ o.label }}</option></select>
              <span class="chev">▾</span>
            </div>
          </div>
        </div>
        <div v-if="isSub" class="sub-note">Замена: занятие на этой неделе проведёт выбранный преподаватель.</div>
        <div class="hint">Перенести урок в другой слот — перетащите его карточку в другую ячейку сетки.</div>
      </template>
      <div v-else class="hint">Занятие в пуле — перетащите его на свободный слот сетки, чтобы разложить.</div>

      <div v-if="lf.err" class="form-err"><span>⚠</span><span>{{ lf.err }}</span></div>
    </div>

    <!-- ===== create form (new lesson) ===== -->
    <div v-else class="body">
      <div class="fld">
        <span class="field-label lbl-row">
          НАЗНАЧЕНИЕ
          <InfoDot :size="15" tip="Связка «дисциплина — группа — преподаватель» приходит из модуля «Распределение»." />
        </span>
        <div v-if="!isEdit" class="select-wrap">
          <select :value="lf.asg" @change="pickAsg">
            <option v-for="o in asgOptions" :key="o.v" :value="o.v">{{ o.label }}</option>
          </select>
          <span class="chev">▾</span>
        </div>
        <div v-else-if="curAsg" class="asg-chip">
          <span class="asg-name">{{ curAsg.label }}</span>
          <span class="asg-sub">{{ curAsg.sub }}</span>
        </div>
      </div>

      <div class="fld">
        <span class="field-label">ТИП ЗАНЯТИЯ</span>
        <div class="select-wrap">
          <select v-model="lf.kind" class="input input--white" @change="lf.err = ''">
            <option v-for="(K, k) in KINDS" :key="k" :value="k">{{ K.label }}</option>
          </select>
          <span class="chev">▾</span>
        </div>
      </div>

      <div class="three">
        <div class="fld fld--num-sm">
          <span class="field-label">№</span>
          <input
            v-model="lf.number"
            class="input input--white"
            type="number"
            min="1"
            placeholder="—"
          >
        </div>
        <div class="fld f2">
          <span class="field-label">ТЕМА ЗАНЯТИЯ *</span>
          <input
            v-model="lf.topic"
            class="input input--white"
            placeholder="Напр.: Тема 4. Пределы и непрерывность функции"
            @input="lf.err = ''"
          >
        </div>
        <div class="fld f15">
          <span class="field-label">УЧЕБНЫЙ ВОПРОС</span>
          <input
            v-model="lf.question"
            class="input input--white"
            placeholder="Вопросы, выносимые на занятие"
          >
        </div>
      </div>

      <div class="fld">
        <span class="field-label">РАЗМЕЩЕНИЕ</span>
        <div class="place-btns">
          <button class="pick-soft place-btn" :class="{ on: lf.placed }" @click="lf.placed = true">
            В сетку (день, пара)
          </button>
          <button class="pick-soft place-btn" :class="{ on: !lf.placed }" @click="lf.placed = false">
            В пул, без слота
          </button>
        </div>
        <template v-if="lf.placed">
          <div class="selects sel4">
            <div class="fld">
              <span class="field-label">Неделя</span>
              <div class="select-wrap">
                <select v-model="lf.w">
                  <option v-for="o in weekOpts" :key="o.v" :value="o.v">{{ o.label }}</option>
                </select>
                <span class="chev">▾</span>
              </div>
            </div>
            <div class="fld">
              <span class="field-label">День</span>
              <div class="select-wrap">
                <select v-model="lf.d">
                  <option v-for="o in dayOpts" :key="o.v" :value="o.v">{{ o.label }}</option>
                </select>
                <span class="chev">▾</span>
              </div>
            </div>
            <div class="fld">
              <span class="field-label">Пара</span>
              <div class="select-wrap">
                <select v-model="lf.s">
                  <option v-for="o in slotOpts" :key="o.v" :value="o.v">{{ o.label }}</option>
                </select>
                <span class="chev">▾</span>
              </div>
            </div>
            <div class="fld">
              <span class="field-label">Аудитория</span>
              <div class="select-wrap">
                <select v-model="lf.r">
                  <option v-for="o in roomOpts" :key="o.v" :value="o.v">{{ o.label }}</option>
                </select>
                <span class="chev">▾</span>
              </div>
            </div>
          </div>

          <div v-if="isEdit" class="sub-row">
            <div class="fld sub-teacher">
              <span class="field-label lbl-row">
                ПРЕПОДАВАТЕЛЬ
                <InfoDot :size="15" tip="Выбор другого преподавателя = замена на этот урок (только для этой недели). Штатный назначается в «Распределении»." />
              </span>
              <div class="select-wrap">
                <select v-model="lf.teacher" :class="{ 'sub-on': isSub }">
                  <option v-for="o in teacherOpts" :key="o.v" :value="o.v">{{ o.label }}</option>
                </select>
                <span class="chev">▾</span>
              </div>
            </div>
          </div>
          <div v-if="isSub" class="sub-note">Замена: занятие на этой неделе проведёт выбранный преподаватель.</div>

          <div class="status" :style="{ border: '1px solid ' + sc.border, background: sc.bg }">
            <span class="st-ico" :style="{ color: sc.color }">{{ sc.icon }}</span>
            <span class="st-text">{{ status.text || 'Слот свободен, конфликтов нет' }}</span>
          </div>
        </template>
      </div>

      <div v-if="lf.err" class="form-err"><span>⚠</span><span>{{ lf.err }}</span></div>
    </div>
    <template #footer>
      <button v-if="isEdit" class="btn-danger" @click="del">Удалить занятие</button>
      <button class="btn btn-lg" @click="ui.lf = null">Отмена</button>
      <span style="flex: 1"></span>
      <button class="btn-primary btn-lg" @click="save">{{ isEdit ? 'Сохранить' : 'Создать занятие' }}</button>
    </template>
  </ModalWindow>
</template>

<style scoped>
.body { flex: 1; overflow-y: auto; padding: 16px 18px; display: flex; flex-direction: column; gap: 13px; }
.fld { display: flex; flex-direction: column; gap: 5px; min-width: 0; }

/* detail-card header (title slot) */
.hdr-dot { width: 12px; height: 12px; border-radius: 50%; flex: none; margin-top: 4px; }
.hdr-txt { flex: 1; min-width: 0; }
.hdr-head { font-size: 14.5px; font-weight: 700; color: var(--fg); }
.hdr-meta { font: 400 11px var(--mono); color: var(--muted); margin-top: 3px; }

/* detail-card rows */
.three { display: flex; gap: 8px; align-items: flex-start; }
.three .fld { flex: 1; }
.three .f2 { flex: 2; }
.three .f15 { flex: 1.5; }
.row-end { display: flex; gap: 10px; align-items: flex-end; }
.row-end .f1 { flex: 1; }
.row-end .f12 { flex: 1.2; }
.hint { font-size: 10.5px; color: var(--faint); line-height: 1.45; margin-top: -6px; }
.lbl-row { display: inline-flex; align-items: center; gap: 6px; }
.asg-chip {
  border: 1px solid rgba(0, 0, 0, 0.1);
  background: var(--hover);
  border-radius: var(--r-lg);
  padding: 9px 11px;
  display: flex;
  align-items: center;
  gap: 7px;
}
.asg-name { font-size: 13px; font-weight: 600; flex: 1; }
.asg-sub { font-size: 11.5px; color: var(--muted); }
.fld--num-sm { flex: none !important; width: 62px; }
.place-btns { display: flex; gap: 5px; }
.place-btn { flex: 1; padding: 7px 0; }
.selects { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; margin-top: 2px; }
.selects.sel4 { grid-template-columns: 0.9fr 0.8fr 1.2fr 1.1fr; }
.sub-row { display: flex; gap: 8px; align-items: flex-end; }
.sub-teacher { flex: 1; }
.sub-on { border-color: rgba(176, 124, 31, 0.6); background: rgba(176, 124, 31, 0.07); color: #8A6A28; }
.sub-note { font-size: 11px; color: var(--amber); margin-top: -4px; }
.status { display: flex; gap: 8px; align-items: baseline; border-radius: var(--r-lg); padding: 9px 11px; }
.st-ico { flex: none; font-size: 12px; }
.st-text { font-size: 12.5px; line-height: 1.5; color: #3A382F; }
</style>
