<script setup>
import { computed } from 'vue'
import { store } from '../../store/index.js'
import { KINDS, kindOf, ALL_DAYS } from '../../utils/kinds.js'
import ModalWindow from '../../components/ModalWindow.vue'
import InfoDot from '../../components/InfoDot.vue'
import { ui, dayIdxs, slotsN, bells, statusFor, asgOptions, flash, ST_COLORS } from './useSchedule.js'

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
  return { label: a.discipline.name + ', ' + a.discipline.groupId, sub: a.teacherName, a }
})

const dayOpts = computed(() => dayIdxs.value.map((i) => ({ v: String(i), label: ALL_DAYS[i] })))
const slotOpts = computed(() => Array.from({ length: slotsN.value }, (_, i) => {
  const b = bells.value[i] || { from: '', to: '' }
  return { v: String(i), label: (i + 1) + ' пара · ' + b.from + '–' + b.to }
}))
const roomOpts = computed(() => store.state.rooms.map((r) => ({ v: r.id, label: r.id + ', ' + r.type + ', ' + r.capacity })))

const status = computed(() => {
  const f = lf.value
  if (!f || !f.placed) return { kind: 'free', text: '' }
  let probe
  if (isEdit.value) {
    if (!editL.value) return { kind: 'free', text: '' }
    probe = { id: f.id, t: editL.value.t, g: editL.value.g, room: f.r }
  } else {
    const a = curAsg.value && curAsg.value.a
    if (!a) return { kind: 'free', text: '' }
    probe = { id: '__new', t: a.teacherId, g: a.discipline.groupId, room: f.r }
  }
  return statusFor(probe, parseInt(f.d), parseInt(f.s), f.r)
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
  const question = f.question.trim()

  if (isEdit.value) {
    const fields = { kind: f.kind, topicLabel: topic, question }
    if (f.placed) {
      fields.day = parseInt(f.d)
      fields.slot = parseInt(f.s)
      fields.roomId = f.r
    } else {
      fields.day = null
      fields.slot = null
      fields.pin = false
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
  const payload = {
    topicId: unitTopic.id,
    disciplineId: a.discipline.id,
    groupId: a.discipline.groupId,
    teacherId: a.teacherId,
    roomId: f.r || a.defaultRoom,
    kind: f.kind,
    period: store.state.period,
    day: f.placed ? parseInt(f.d) : null,
    slot: f.placed ? parseInt(f.s) : null,
    pin: false,
    ni: 1,
    nt: 1,
    topicLabel: topic,
    question,
  }
  ui.lf = null
  if (payload.day != null && ui.view === 'group' && a.discipline.groupId !== ui.ent.group) {
    ui.ent.group = a.discipline.groupId
  }
  const created = await store.createManualLesson(payload)
  flash(created.id)
}

async function del() {
  const id = lf.value.id
  ui.lf = null
  ui.sel = []
  await store.deleteLesson(id)
}
</script>

<template>
  <ModalWindow
    v-if="lf"
    :title="isEdit ? 'Занятие — тема и учебный вопрос' : 'Новое занятие'"
    :width="490"
    @close="ui.lf = null"
  >
    <div class="body">
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
        <div class="kind-btns">
          <button
            v-for="(K, k) in KINDS"
            :key="k"
            class="pick-soft kind-btn"
            :class="{ on: lf.kind === k }"
            :style="{ fontWeight: lf.kind === k ? 600 : 400 }"
            @click="lf.kind = k; lf.err = ''"
          >{{ K.mark }} {{ K.label }}</button>
        </div>
      </div>

      <div class="fld">
        <span class="field-label">ТЕМА ЗАНЯТИЯ *</span>
        <input
          v-model="lf.topic"
          class="input input--white"
          placeholder="Напр.: Тема 4. Пределы и непрерывность функции"
          @input="lf.err = ''"
        >
      </div>

      <div class="fld">
        <span class="field-label">УЧЕБНЫЙ ВОПРОС</span>
        <textarea
          v-model="lf.question"
          class="input input--white qarea"
          rows="2"
          placeholder="Вопросы, выносимые на занятие"
        ></textarea>
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
          <div class="selects">
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
          <div class="status" :style="{ border: '1px solid ' + sc.border, background: sc.bg }">
            <span class="st-ico" :style="{ color: sc.color }">{{ sc.icon }}</span>
            <span class="st-text">{{ status.text || 'Слот свободен, конфликтов нет' }}</span>
          </div>
        </template>
      </div>

      <div v-if="lf.err" class="form-err"><span>⚠</span><span>{{ lf.err }}</span></div>
    </div>
    <template #footer>
      <button v-if="isEdit" class="btn-danger" @click="del">Удалить</button>
      <button class="btn btn-lg" @click="ui.lf = null">Отмена</button>
      <span style="flex: 1"></span>
      <button class="btn-primary btn-lg" @click="save">{{ isEdit ? 'Сохранить' : 'Создать занятие' }}</button>
    </template>
  </ModalWindow>
</template>

<style scoped>
.body { flex: 1; overflow-y: auto; padding: 16px 18px; display: flex; flex-direction: column; gap: 13px; }
.fld { display: flex; flex-direction: column; gap: 5px; min-width: 0; }
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
.kind-btns { display: flex; gap: 5px; flex-wrap: wrap; }
.kind-btn { font-size: 12px; padding: 6px 11px; }
.qarea { resize: vertical; min-height: 44px; }
.place-btns { display: flex; gap: 5px; }
.place-btn { flex: 1; padding: 7px 0; }
.selects { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; margin-top: 2px; }
.status { display: flex; gap: 8px; align-items: baseline; border-radius: var(--r-lg); padding: 9px 11px; }
.st-ico { flex: none; font-size: 12px; }
.st-text { font-size: 12.5px; line-height: 1.5; color: #3A382F; }
</style>
