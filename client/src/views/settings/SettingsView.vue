<script setup>
import { reactive, ref, computed, watch } from 'vue'
import { store } from '../../store/index.js'
import { api } from '../../api/index.js'
import { ALL_DAYS } from '../../utils/kinds.js'
import { toMin, toStr, slotEnd, slotLen } from '../../utils/slots.js'
import { confirmDelete } from '../../composables/useConfirm.js'
import ModalWindow from '../../components/ModalWindow.vue'

const activeId = computed(() => store.state.period)
// the year the whole app (and these settings) is currently scoped to
const workingYear = computed(() => store.state.years.find((y) => y.id === store.state.yearId))
const workingName = computed(() => (workingYear.value ? workingYear.value.name : '—'))

/* ---------- roll-over: copy a curated set of disciplines ---------- */

const roll = reactive({ open: false, target: null, source: '', busy: false, error: '', discs: [], checked: {}, targetDiscs: [] })
const targetYear = computed(() => store.state.years.find((y) => y.id === roll.target))
const targetName = computed(() => (targetYear.value ? targetYear.value.name : '—'))
const sourceYearOpts = computed(() => store.state.years
  .filter((y) => y.id !== roll.target)
  .map((y) => ({ v: y.id, label: y.name })))

const majorCode = (id) => {
  const m = store.state.majors.find((x) => x.id === id)
  return m ? m.code : ''
}
const rollMeta = (d) =>
  `${d.course} курс · ${d.period === 'fall' ? 'осень' : 'весна'}${majorCode(d.majorId) ? ' · ' + majorCode(d.majorId) : ''}`

/* A discipline's identity within a year: same major, course, season and name. */
const discKey = (d) => `${d.majorId}|${d.course}|${d.period}|${String(d.name || '').trim().toLowerCase()}`
/* Disciplines already present in the target draft year. */
const targetDiscKeys = computed(() => new Set(roll.targetDiscs.map(discKey)))

/* Source disciplines annotated with a diff status against the target year. */
const rollRows = computed(() => roll.discs
  .map((d) => ({ ...d, exists: targetDiscKeys.value.has(discKey(d)) }))
  .sort((a, b) => Number(a.exists) - Number(b.exists)))
const rollChosen = computed(() => roll.discs.filter((d) => roll.checked[d.id]).length)
const rollNewCount = computed(() => rollRows.value.filter((d) => !d.exists).length)
const rollDupCount = computed(() => rollRows.value.filter((d) => d.exists).length)

/*
 * Load the source year's disciplines as a checklist. Diff-aware default:
 * tick only what is missing from the working year, leave duplicates unticked.
 */
watch(() => roll.source, async (src) => {
  roll.discs = []
  roll.checked = {}
  roll.error = ''
  if (!src) return
  const discs = await api.getDisciplines(Number(src))
  const curKeys = targetDiscKeys.value
  const checked = {}
  discs.forEach((d) => { checked[d.id] = !curKeys.has(discKey(d)) })
  roll.discs = discs
  roll.checked = checked
})

async function openRollover(y) {
  if (roll.open && roll.target === y.id) { closeRollover(); return }
  roll.open = true
  roll.target = y.id
  roll.source = ''
  roll.discs = []
  roll.checked = {}
  roll.error = ''
  // the in-scope year is already in the store; any other draft is fetched on demand
  roll.targetDiscs = y.id === store.state.yearId
    ? store.state.disciplines
    : await api.getDisciplines(y.id)
}
function closeRollover() {
  if (roll.busy) return
  roll.open = false
  roll.target = null
}

function toggleRoll(id) { roll.checked = { ...roll.checked, [id]: !roll.checked[id] } }
function setAllRoll(on) {
  const c = {}
  roll.discs.forEach((d) => { c[d.id] = on })
  roll.checked = c
}
/** Tick only the disciplines missing from the working year (the merge default). */
function selectNewRoll() {
  const c = {}
  rollRows.value.forEach((d) => { c[d.id] = !d.exists })
  roll.checked = c
}

async function doRollover() {
  if (!roll.source || !rollChosen.value) return
  roll.busy = true
  roll.error = ''
  try {
    const ids = roll.discs.filter((d) => roll.checked[d.id]).map((d) => d.id)
    await store.rolloverYear(roll.target, Number(roll.source), ids)
    roll.open = false
    roll.target = null
    roll.source = ''
    roll.discs = []
    roll.checked = {}
  } catch (e) {
    roll.error = (e && e.message) || 'Не удалось перенести дисциплины'
  } finally {
    roll.busy = false
  }
}

const form = reactive({ dirty: false, saved: false, acadMin: 45, days: [], slots: [] })

function loadForm() {
  const p = store.state.periods[activeId.value]
  if (!p) return
  form.dirty = false
  form.saved = false
  form.acadMin = p.acadMin || 45
  form.days = [...p.activeDays]
  form.slots = (p.slots || []).map((s) => ({ brk: 15, ...s }))
}
loadForm()
// reload when the season changes or the working year's settings are reloaded
watch([activeId, () => store.state.periods], loadForm)

function mark() { form.dirty = true; form.saved = false }

const validT = (t) => /^\d{1,2}:\d{2}$/.test(String(t))

/* ---------- academic years ---------- */

const yearRows = computed(() => store.state.years.map((y) => {
  const st = y.status
  return {
    id: y.id,
    name: y.name,
    aut: y.autFrom + ' — ' + y.autTo,
    spr: y.sprFrom + ' — ' + y.sprTo,
    weight: st === 'active' ? 600 : 500,
    bg: st === 'active' ? 'rgba(31,138,91,0.04)' : 'transparent',
    status: st === 'active' ? 'активный' : st === 'done' ? 'завершён' : 'черновик',
    statusCls: st,
    active: st === 'active',
    actTip: st === 'done'
      ? 'Снова сделать активным и открыть во всех разделах (текущий активный станет черновиком)'
      : 'Сделать активным и открыть во всех разделах (текущий активный станет черновиком)',
    delTip: st === 'active' ? 'Активный год удалить нельзя — сначала сделайте активным другой' : 'Удалить учебный год',
  }
}))

const newYear = ref(null)
function openNewYear() { newYear.value = { name: '', autFrom: '', autTo: '', sprFrom: '', sprTo: '', copy: true } }
const nyValid = computed(() => {
  const n = newYear.value
  return !!(n && n.name.trim() && n.autFrom.trim() && n.autTo.trim() && n.sprFrom.trim() && n.sprTo.trim())
})
async function createYear() {
  if (!nyValid.value) return
  const n = newYear.value
  await store.createYear({
    name: n.name.trim(),
    autFrom: n.autFrom.trim(), autTo: n.autTo.trim(),
    sprFrom: n.sprFrom.trim(), sprTo: n.sprTo.trim(),
    copyFromYearId: n.copy ? store.state.yearId : undefined,
  })
  newYear.value = null
}

async function removeYear(y) {
  if (y.active) return
  const ok = await confirmDelete({
    title: 'Удалить учебный год?',
    message: 'Будут удалены настройки года, назначения и расписание обоих семестров. Действие необратимо.',
    entityName: `${y.name} · осень ${y.aut} · весна ${y.spr}`,
    confirmLabel: 'Удалить уч. год',
  })
  if (ok) store.deleteYear(y.id)
}

/* ---------- academic hour ---------- */

function ahDec() { form.acadMin = Math.max(30, form.acadMin - 5); mark() }
function ahInc() { form.acadMin = Math.min(60, form.acadMin + 5); mark() }
const exType = computed(() => 'урок 2 ак.ч = ' + slotLen(2, form.acadMin) + ' мин, консультация 1 ак.ч = ' + form.acadMin + ' мин')

/* ---------- week ---------- */

function toggleDay(i) { form.days[i] = !form.days[i]; mark() }

/* ---------- slots (bells) ---------- */

/* Recompute the start of every slot below `from`: start[i] = end[i-1] + break[i-1]. */
function cascade(slots, from) {
  for (let i = Math.max(1, from + 1); i < slots.length; i++) {
    const p = slots[i - 1]
    if (!validT(p.start)) break
    slots[i].start = toStr(toMin(p.start) + slotLen(p.hours, form.acadMin) + p.brk)
  }
  return slots
}

function commitSlots(slots) { form.slots = slots; mark() }
const cloneSlots = () => form.slots.map((s) => ({ ...s }))

function updSlot(i, patch) {
  const slots = cloneSlots()
  Object.assign(slots[i], patch)
  commitSlots(cascade(slots, i))
}
function setSlotStart(i, v) {
  const slots = cloneSlots()
  slots[i].start = v
  if (validT(v)) {
    // editing a start retunes the break before it, then shifts the slots below
    if (i > 0 && validT(slots[i - 1].start)) {
      const p = slots[i - 1]
      slots[i - 1].brk = Math.max(0, toMin(v) - (toMin(p.start) + slotLen(p.hours, form.acadMin)))
    }
    cascade(slots, i)
  }
  commitSlots(slots)
}
function setSlotBrk(i, brk) { updSlot(i, { brk: Math.min(60, Math.max(5, brk)) }) }
function setSlotHours(i, h) { updSlot(i, { hours: h }) }
function delSlot(i) {
  const slots = cloneSlots().filter((_, j) => j !== i)
  commitSlots(cascade(slots, Math.max(0, i - 1)))
}
function addSlot() {
  const last = form.slots[form.slots.length - 1]
  const start = last && validT(last.start)
    ? toStr(toMin(last.start) + slotLen(last.hours, form.acadMin) + last.brk)
    : '08:30'
  commitSlots([...cloneSlots(), { start, hours: 2, brk: 15 }])
}

const slotRows = computed(() => form.slots.map((b, i) => {
  const ok = validT(b.start)
  const last = i === form.slots.length - 1
  const brkKind = b.brk >= 25 ? 'большая' : b.brk <= 10 ? 'укороченная' : 'обычная'
  return {
    n: i + 1,
    start: b.start,
    hours: b.hours,
    brk: b.brk,
    last,
    brkLabel: last ? '—' : b.brk + ' мин',
    brkBig: !last && b.brk >= 25,
    brkTitle: last
      ? 'После последнего урока перемены нет'
      : 'Перемена после этого урока · ' + brkKind + ' · сдвигает начало следующих уроков',
    end: ok ? slotEnd(b.start, b.hours, form.acadMin) : '—',
    mins: slotLen(b.hours, form.acadMin) + ' мин',
  }
}))

/* ---------- save ---------- */

async function save() {
  if (!form.dirty) return
  await store.savePeriod(activeId.value, {
    acadMin: form.acadMin,
    activeDays: [...form.days],
    slots: form.slots.map((s) => ({ ...s })),
  })
  form.dirty = false
  form.saved = true
}
</script>

<template>
  <div class="view">
    <!-- ======= header ======= -->
    <div class="head">
      <span class="head-title">Настройки</span>
      <span class="year-chip mono" title="Настройки ниже относятся к выбранному учебному году">уч. год: {{ workingName }}</span>
      <div class="sp"></div>
      <span v-if="form.dirty" class="dirty-note">есть несохранённые изменения</span>
      <button
        class="save-btn"
        :style="{
          background: form.dirty ? '#1F1E1B' : form.saved ? '#1F8A5B' : '#B5B0A6',
          cursor: form.dirty ? 'pointer' : 'default',
        }"
        @click="save"
      >{{ form.saved ? '✓ Сохранено' : 'Сохранить' }}</button>
    </div>

    <!-- ======= body ======= -->
    <div class="body">
      <div class="col">
        <!-- ===== academic years ===== -->
        <div class="panel sect">
          <div class="sect-head-row">
            <div class="sect-head">
              <span class="sect-title">Учебные годы</span>
              <span class="sect-sub">Год = пара семестров (осень + весна). Все разделы работают с активным годом; между осенью и весной переключаются прямо в шапке «Расписания».</span>
            </div>
            <button class="ghost-btn" @click="openNewYear"><span class="plus">＋</span>Новый уч. год</button>
          </div>
          <div class="yr-table">
            <div class="yr-thead mono">
              <span>УЧ. ГОД</span><span>ОСЕНЬ</span><span>ВЕСНА</span><span>СТАТУС</span><span class="yr-acts-h">ДЕЙСТВИЯ</span>
            </div>
            <template v-for="y in yearRows" :key="y.id">
              <div class="yr-row" :style="{ background: y.bg }">
                <span class="yr-name">
                  <span class="yr-name-txt" :style="{ fontWeight: y.weight }">{{ y.name }}</span>
                </span>
                <span class="yr-range mono">{{ y.aut }}</span>
                <span class="yr-range mono">{{ y.spr }}</span>
                <span class="yr-status mono" :class="y.statusCls">{{ y.status }}</span>
                <div class="yr-acts">
                  <button v-if="!y.active" class="yr-icon" :title="y.actTip" @click="store.activateYear(y.id)">→</button>
                  <button
                    v-if="y.statusCls === 'draft'"
                    class="yr-icon ro"
                    :class="{ on: roll.open && roll.target === y.id }"
                    title="Перенести дисциплины и темы из другого года в этот черновик"
                    @click="openRollover(y)"
                  >⇄</button>
                  <button class="yr-del" :class="{ off: y.active }" :title="y.delTip" @click="removeYear(y)">✕</button>
                </div>
              </div>
            </template>

            <!-- plan transfer (rollover) into the chosen draft year — pinned below the list -->
            <div v-if="roll.open" class="ro-form">
              <div class="ro-form-top">
                <div class="sect-head">
                  <span class="sect-title">Перенос плана в черновик «{{ targetName }}»</span>
                  <span class="sect-sub">Скопирует выбранные дисциплины и их темы. Группы, преподаватели и назначения создаются заново — расписание останется пустым.</span>
                </div>
                <button class="ro-x" title="Свернуть" @click="closeRollover">✕</button>
              </div>

              <div class="ro-controls">
                <div class="select-wrap">
                  <select v-model="roll.source" class="input ro-src">
                    <option value="" disabled>год-источник…</option>
                    <option v-for="o in sourceYearOpts" :key="o.v" :value="o.v">{{ o.label }}</option>
                  </select>
                </div>
                <span v-if="roll.source && roll.discs.length" class="ro-diffsum">
                  <span class="ro-tag new">＋{{ rollNewCount }} новых</span>
                  <span v-if="rollDupCount" class="ro-tag dup">{{ rollDupCount }} уже есть</span>
                </span>
                <span class="sp"></span>
                <button class="btn-primary ro-go" :disabled="!roll.source || !rollChosen || roll.busy" @click="doRollover">
                  {{ roll.busy ? 'Переносим…' : 'Перенести выбранные (' + rollChosen + ')' }}
                </button>
              </div>

              <template v-if="roll.source && roll.discs.length">
                <div class="ro-checkhead">
                  <span class="ro-count mono">Выбрано {{ rollChosen }} из {{ roll.discs.length }}</span>
                  <span class="sp"></span>
                  <button class="link-btn" @click="selectNewRoll">Только новые</button>
                  <button class="link-btn" @click="setAllRoll(true)">Все</button>
                  <button class="link-btn" @click="setAllRoll(false)">Снять</button>
                </div>
                <div class="ro-list">
                  <label
                    v-for="d in rollRows"
                    :key="d.id"
                    class="ro-item"
                    :class="{ dup: d.exists }"
                    @click.prevent="toggleRoll(d.id)"
                  >
                    <span class="ns-box" :class="{ on: roll.checked[d.id] }">{{ roll.checked[d.id] ? '✓' : '' }}</span>
                    <span class="ro-name">{{ d.name }}</span>
                    <span class="ro-meta mono">{{ rollMeta(d) }}</span>
                    <span class="ro-tcount mono">{{ d.topics.length }} тем</span>
                    <span class="ro-status" :class="d.exists ? 'dup' : 'new'">{{ d.exists ? 'уже есть' : 'новая' }}</span>
                  </label>
                </div>
                <div class="footnote">«Уже есть» — дисциплина с тем же названием, курсом и семестром уже заведена в «{{ targetName }}»; по умолчанию такие не переносятся, чтобы не задваивать план. Отметьте вручную, если перенос всё же нужен.</div>
              </template>
              <div v-else-if="roll.source" class="footnote">В выбранном году нет дисциплин для переноса.</div>
              <div v-if="roll.error" class="ro-error">{{ roll.error }}</div>
            </div>
          </div>
          <div class="footnote">Действия справа: «→» делает год активным и открывает его во всех разделах (прежний активный становится черновиком); «⇄» переносит план из другого года в черновик. Новый год создаётся черновиком: перенесите в него план, а когда будете готовы работать с ним — сделайте активным. Активный год удалить нельзя.</div>
        </div>

        <!-- ===== academic hour ===== -->
        <div class="panel sect">
          <div class="sect-head">
            <span class="sect-title">Академический час</span>
            <span class="sect-sub">Базовая единица времени — все длительности в приложении считаются в ак. часах</span>
          </div>
          <div class="ah-row">
            <button class="step" @click="ahDec">−</button>
            <span class="ah-val mono">{{ form.acadMin }} мин</span>
            <button class="step" @click="ahInc">＋</button>
            <span class="slots-note">шаг 5 мин · стандарт 45</span>
          </div>
          <div class="ah-info">
            <span>На академический час завязаны:</span>
            <span>· <b>типы занятий</b> — длительность типа = N × ак.ч ({{ exType }})</span>
            <span>· <b>сетка звонков</b> — время слотов считается из ак. часа и перемен</span>
            <span>· <b>учёт часов</b> — «разложено / заведено / план» в содержании курсов</span>
          </div>
        </div>

        <!-- ===== week ===== -->
        <div class="panel sect">
          <div class="sect-head">
            <span class="sect-title">Учебная неделя</span>
            <span class="sect-sub">Выключенные дни не показываются в сетке «Расписания» и недоступны генератору</span>
          </div>
          <div class="days">
            <button
              v-for="(d, i) in ALL_DAYS"
              :key="d"
              class="day-btn"
              :class="{ on: form.days[i] }"
              @click="toggleDay(i)"
            >{{ d }}</button>
          </div>
        </div>

        <!-- ===== bells / slots ===== -->
        <div class="panel sect">
          <div class="sect-head">
            <span class="sect-title">Сетка звонков</span>
            <span class="sect-sub">Слот = 1–2 ак.ч. Начало урока и перемена после него редактируются прямо в таблице; конец и длительность считаются сами. Изменение начала или перемены сдвигает все уроки ниже.</span>
          </div>

          <div class="slot-table">
            <div class="slot-thead mono">
              <span>СЛОТ</span><span>НАЧАЛО</span><span>АК. ЧАСОВ</span><span>ПЕРЕМЕНА ПОСЛЕ</span><span>КОНЕЦ</span><span>ДЛИТ.</span><span></span>
            </div>
            <div v-for="(b, i) in slotRows" :key="i" class="slot-row">
              <span class="slot-n mono">{{ b.n }}</span>
              <input :value="b.start" class="input mono slot-start" title="Начало урока — редактируется; перемена перед ним и уроки ниже подстроятся" @change="setSlotStart(i, $event.target.value)">
              <span class="hseg">
                <button :class="{ on: b.hours === 1 }" @click="setSlotHours(i, 1)">1 ак.ч</button>
                <button :class="{ on: b.hours === 2 }" @click="setSlotHours(i, 2)">2 ак.ч</button>
              </span>
              <span class="slot-brk" :title="b.brkTitle">
                <template v-if="!b.last">
                  <button class="mini" @click="setSlotBrk(i, b.brk - 5)">−</button>
                  <span class="brk-val mono" :class="{ big: b.brkBig }">{{ b.brkLabel }}</span>
                  <button class="mini" @click="setSlotBrk(i, b.brk + 5)">＋</button>
                </template>
                <span v-else class="brk-val mono dim">—</span>
              </span>
              <span class="slot-end mono">{{ b.end }}</span>
              <span class="slot-mins mono">{{ b.mins }}</span>
              <button class="slot-del" title="Удалить слот" @click="delSlot(i)">✕</button>
            </div>
            <button class="add-slot" @click="addSlot">+ слот</button>
          </div>
          <div class="footnote">Длительность слота = ак. часы × {{ form.acadMin }} мин (+5 мин звонок между часами внутри пары). Большая перемена — просто больше минут после нужного урока; укороченная — меньше. Автогенератор не ставит занятие 2 ак.ч в слот на 1 ак.ч.</div>
        </div>

        <div class="footnote wide">
          Изменения применяются к активному учебному году: сетка «Расписания», проверка конфликтов и генератор
          перечитывают конфиг после сохранения. Уже размещённые занятия при сужении недели или сетки
          помечаются как проблемы, а не удаляются.
        </div>
      </div>
    </div>

    <!-- ===== new academic year modal ===== -->
    <ModalWindow v-if="newYear" title="Новый учебный год" :width="600" @close="newYear = null">
      <div class="ny-body">
        <div class="ny-name">
          <span class="field-label">НАЗВАНИЕ УЧЕБНОГО ГОДА</span>
          <div class="ny-name-row">
            <input v-model="newYear.name" class="input ny-name-input" placeholder="2028/29">
            <span class="ny-hint">пара семестров одного года — осень и весна</span>
          </div>
        </div>

        <div class="ny-terms">
          <div class="ny-term aut">
            <div class="ny-term-head">
              <span class="ny-dot"></span>
              <span class="ny-term-title">Осень</span>
              <span class="sp"></span>
              <span class="ny-term-tag mono">1 СЕМЕСТР</span>
            </div>
            <div class="ny-term-fields">
              <div class="fld">
                <span class="ny-flabel">Начало</span>
                <input v-model="newYear.autFrom" class="input mono ny-date aut" placeholder="01.09.2028">
              </div>
              <span class="ny-arrow">→</span>
              <div class="fld">
                <span class="ny-flabel">Конец</span>
                <input v-model="newYear.autTo" class="input mono ny-date aut" placeholder="24.12.2028">
              </div>
            </div>
          </div>
          <div class="ny-term spr">
            <div class="ny-term-head">
              <span class="ny-dot"></span>
              <span class="ny-term-title">Весна</span>
              <span class="sp"></span>
              <span class="ny-term-tag mono">2 СЕМЕСТР</span>
            </div>
            <div class="ny-term-fields">
              <div class="fld">
                <span class="ny-flabel">Начало</span>
                <input v-model="newYear.sprFrom" class="input mono ny-date spr" placeholder="05.02.2029">
              </div>
              <span class="ny-arrow">→</span>
              <div class="fld">
                <span class="ny-flabel">Конец</span>
                <input v-model="newYear.sprTo" class="input mono ny-date spr" placeholder="27.05.2029">
              </div>
            </div>
          </div>
        </div>

        <label class="ns-copy" @click.prevent="newYear.copy = !newYear.copy">
          <span class="ns-box" :class="{ on: newYear.copy }">{{ newYear.copy ? '✓' : '' }}</span>
          скопировать сетку звонков, учебную неделю и академический час из активного года
        </label>
        <div class="footnote">Год создаётся черновиком — активным его делают отдельно, в списке учебных годов.</div>
      </div>
      <template #footer>
        <span class="sp"></span>
        <button class="btn" @click="newYear = null">Отмена</button>
        <button class="btn-primary" :disabled="!nyValid" @click="createYear">Создать уч. год</button>
      </template>
    </ModalWindow>
  </div>
</template>

<style scoped>
.view { flex: 1; display: flex; flex-direction: column; min-height: 0; }
.sp { flex: 1; }

.head {
  flex: none;
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 10px 16px;
  background: var(--panel);
  border-bottom: 1px solid rgba(0, 0, 0, 0.08);
}
.head-title { font-size: 15px; font-weight: 600; letter-spacing: -0.01em; flex: none; }
.year-chip {
  font: 500 10px var(--mono);
  color: var(--green);
  background: rgba(31, 138, 91, 0.08);
  border-radius: 4px;
  padding: 2px 7px;
}
.dirty-note { font-size: 11.5px; color: #B45309; }
.save-btn {
  flex: none;
  border: none;
  color: #FFFFFF;
  font: 500 13px var(--sans);
  padding: 8px 16px;
  border-radius: var(--r-md);
}

.body { flex: 1; overflow-y: auto; padding: 16px; }
.col { max-width: 700px; display: flex; flex-direction: column; gap: 14px; }

.sect { padding: 16px 18px; gap: 12px; overflow: visible; }
.sect-head { display: flex; flex-direction: column; gap: 2px; }
.sect-head-row { display: flex; align-items: flex-start; gap: 10px; }
.sect-head-row .sect-head { flex: 1; }
.sect-title { font-size: 13.5px; font-weight: 600; }
.sect-sub { font-size: 11.5px; color: var(--muted); }
.micro { font: 500 10.5px var(--mono); letter-spacing: 0.07em; color: var(--muted); }
.field-label { font-size: 11px; font-weight: 600; color: var(--muted); }

.ghost-btn {
  flex: none;
  border: 1px solid var(--line-strong);
  background: var(--panel);
  color: var(--fg);
  font: 500 12px var(--sans);
  padding: 6px 12px;
  border-radius: var(--r-md);
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 5px;
}
.ghost-btn:hover { background: #FBFAF8; }
.plus { font-size: 13px; line-height: 1; }

/* academic years */
.yr-table { display: flex; flex-direction: column; }
.yr-thead, .yr-row {
  display: grid;
  grid-template-columns: 140px 1fr 1fr 84px minmax(220px, auto);
  gap: 8px;
  align-items: center;
}
.yr-thead { padding: 4px 0; font: 500 10px var(--mono); letter-spacing: 0.06em; color: var(--faint); }
.yr-acts-h { justify-self: end; }
.yr-row { padding: 8px 0; border-top: 1px solid rgba(0, 0, 0, 0.06); }
.yr-range { font: 400 10.5px var(--mono); color: var(--muted); }
.yr-status { justify-self: start; font: 500 9.5px var(--mono); border-radius: 4px; padding: 2px 7px; }
.yr-status.active { color: var(--green); background: rgba(31, 138, 91, 0.10); }
.yr-status.done { color: var(--muted); background: var(--chip); }
.yr-status.draft { color: var(--amber); background: rgba(176, 124, 31, 0.10); }
.yr-name { display: inline-flex; align-items: center; gap: 7px; min-width: 0; }
.yr-name-txt { font-size: 12.5px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

/* row actions */
.yr-acts { justify-self: end; display: inline-flex; align-items: center; gap: 12px; }
.yr-icon {
  flex: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border: 1px solid var(--line-strong);
  background: var(--panel);
  color: var(--blue);
  font-size: 13px;
  line-height: 1;
  border-radius: var(--r-md);
  cursor: pointer;
}
.yr-icon:hover { background: #FBFAF8; }
.yr-icon.ro.on { color: #FFFFFF; background: var(--blue); border-color: var(--blue); }
.yr-del { border: none; background: transparent; color: var(--red); font-size: 13px; cursor: pointer; padding: 2px 4px; }
.yr-del.off { color: var(--dim); cursor: default; }

/* in-place plan transfer (rollover) */
.ro-form {
  margin: 10px 0 8px;
  padding: 13px 14px;
  border: 1px solid rgba(59, 98, 196, 0.22);
  border-radius: var(--r-lg);
  background: rgba(59, 98, 196, 0.04);
  display: flex;
  flex-direction: column;
  gap: 11px;
}
.ro-form-top { display: flex; align-items: flex-start; gap: 10px; }
.ro-form-top .sect-head { flex: 1; }
.ro-x { flex: none; border: none; background: transparent; color: var(--muted); font-size: 13px; cursor: pointer; padding: 2px 6px; border-radius: var(--r-sm); }
.ro-x:hover { background: var(--hover); color: var(--fg); }
.ro-controls { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.ro-src { font: 400 12px var(--sans); padding: 6px 9px; min-width: 200px; }
.ro-diffsum { display: inline-flex; align-items: center; gap: 6px; }
.ro-tag { font: 500 10px var(--mono); border-radius: 4px; padding: 2px 7px; }
.ro-tag.new { color: var(--green); background: rgba(31, 138, 91, 0.12); }
.ro-tag.dup { color: var(--muted); background: var(--chip); }
.ro-go { flex: none; }
.ghost-btn:disabled { opacity: 0.5; cursor: default; }
.ro-checkhead { display: flex; align-items: center; gap: 10px; }
.ro-count { font: 500 11px var(--mono); color: var(--sub); }
.link-btn { border: none; background: transparent; color: var(--blue); font: 500 11.5px var(--sans); cursor: pointer; padding: 2px 3px; }
.link-btn:hover { text-decoration: underline; }
.ro-list { max-height: 260px; overflow-y: auto; display: flex; flex-direction: column; gap: 2px; border: 1px solid rgba(0, 0, 0, 0.09); border-radius: var(--r-md); padding: 5px; background: var(--panel); }
.ro-item { display: flex; align-items: center; gap: 9px; padding: 6px 8px; border-radius: var(--r-sm); cursor: pointer; }
.ro-item:hover { background: var(--hover); }
.ro-item.dup { opacity: 0.7; }
.ro-name { font-size: 12.5px; color: #1F1E1B; flex: 1; min-width: 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.ro-meta { font: 400 11px var(--mono); color: var(--faint); flex: none; }
.ro-tcount { font: 400 11px var(--mono); color: var(--muted); flex: none; width: 54px; text-align: right; }
.ro-status { flex: none; font: 500 9px var(--mono); letter-spacing: 0.04em; text-transform: uppercase; border-radius: 4px; padding: 2px 6px; width: 62px; text-align: center; }
.ro-status.new { color: var(--green); background: rgba(31, 138, 91, 0.12); }
.ro-status.dup { color: var(--muted); background: var(--chip); }
.ro-error { font-size: 12px; color: var(--red); }

.fld { display: flex; flex-direction: column; gap: 4px; min-width: 0; }
.ns-copy { display: flex; align-items: center; gap: 8px; cursor: pointer; font-size: 12px; color: #3A382F; }
.ns-box {
  flex: none;
  width: 15px;
  height: 15px;
  border-radius: 4px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  color: #FFF;
  background: #FFF;
  border: 1px solid rgba(0, 0, 0, 0.25);
}
.ns-box.on { background: var(--fg); border-color: var(--fg); }

/* new-year modal */
.ny-body { padding: 16px 18px; display: flex; flex-direction: column; gap: 14px; }
.ny-name { display: flex; flex-direction: column; gap: 5px; }
.ny-name-row { display: flex; align-items: center; gap: 10px; }
.ny-name-input { width: 150px; font-weight: 600; }
.ny-hint { font-size: 11.5px; color: var(--faint); }
.ny-terms { display: flex; gap: 12px; }
.ny-term { flex: 1; min-width: 0; border-radius: var(--r-lg); padding: 12px 13px 13px; display: flex; flex-direction: column; gap: 10px; }
.ny-term.aut { border: 1px solid rgba(176, 124, 31, 0.28); border-top: 3px solid var(--amber); background: rgba(176, 124, 31, 0.05); }
.ny-term.spr { border: 1px solid rgba(31, 138, 91, 0.28); border-top: 3px solid var(--green); background: rgba(31, 138, 91, 0.05); }
.ny-term-head { display: flex; align-items: center; gap: 8px; }
.ny-dot { width: 9px; height: 9px; border-radius: 50%; flex: none; }
.ny-term.aut .ny-dot { background: var(--amber); }
.ny-term.spr .ny-dot { background: var(--green); }
.ny-term-title { font-size: 13.5px; font-weight: 600; }
.ny-term.aut .ny-term-title { color: #8A6A28; }
.ny-term.spr .ny-term-title { color: #166A45; }
.ny-term-tag { font: 500 9px var(--mono); letter-spacing: 0.05em; border-radius: 4px; padding: 2px 7px; }
.ny-term.aut .ny-term-tag { color: #B0894A; background: rgba(176, 124, 31, 0.13); }
.ny-term.spr .ny-term-tag { color: #3E9A6E; background: rgba(31, 138, 91, 0.13); }
.ny-term-fields { display: flex; gap: 8px; align-items: flex-end; }
.ny-flabel { font-size: 10px; color: var(--muted); }
.ny-date { font: 400 11.5px var(--mono); padding: 7px 9px; }
.ny-date.aut { border-color: rgba(176, 124, 31, 0.35); }
.ny-date.spr { border-color: rgba(31, 138, 91, 0.32); }
.ny-arrow { flex: none; font-size: 12px; padding-bottom: 8px; color: var(--faint); }

/* academic hour */
.ah-row { display: flex; align-items: center; gap: 10px; }
.ah-val { font: 500 15px var(--mono); min-width: 64px; text-align: center; }
.slots-note { font-size: 11.5px; color: var(--muted); }
.ah-info {
  display: flex;
  flex-direction: column;
  gap: 5px;
  font-size: 11.5px;
  color: var(--sub);
  line-height: 1.5;
  background: #FBFAF8;
  border-radius: var(--r-md);
  padding: 9px 11px;
}
.step {
  border: 1px solid var(--line-strong);
  background: var(--panel);
  width: 28px;
  height: 28px;
  border-radius: var(--r-md);
  cursor: pointer;
}

/* week */
.days { display: flex; gap: 6px; }
.day-btn {
  border: 1px solid var(--line-strong);
  background: var(--panel);
  color: var(--faint);
  font: 500 12.5px var(--sans);
  padding: 7px 0;
  width: 52px;
  border-radius: var(--r-md);
  cursor: pointer;
}
.day-btn.on { border-color: var(--fg); background: var(--fg); color: #FFFFFF; }

/* slots */
.slot-table { display: flex; flex-direction: column; }
.slot-thead, .slot-row {
  display: grid;
  grid-template-columns: 40px 76px 150px 128px 70px 74px 30px;
  gap: 8px;
  align-items: center;
}
.slot-thead { padding: 4px 0; font: 500 10px var(--mono); letter-spacing: 0.06em; color: var(--faint); }
.slot-row { padding: 7px 0; border-top: 1px solid rgba(0, 0, 0, 0.06); }
.slot-n { font: 400 11px var(--mono); color: var(--faint); }
.slot-start { width: 100%; box-sizing: border-box; text-align: center; font: 400 12px var(--mono); padding: 6px 4px; background: var(--panel); }
.hseg { display: inline-flex; background: #F2F0EB; border-radius: 6px; padding: 2px; gap: 2px; }
.hseg button { border: none; border-radius: 5px; padding: 4px 10px; font: 500 11px var(--sans); color: var(--muted); background: transparent; cursor: pointer; }
.hseg button.on { font-weight: 600; color: var(--fg); background: #FFF; box-shadow: 0 1px 2px rgba(0, 0, 0, 0.14); }
.slot-brk { display: inline-flex; align-items: center; gap: 5px; }
.mini { border: 1px solid var(--line-soft); background: var(--panel); width: 20px; height: 20px; border-radius: 5px; cursor: pointer; font-size: 10px; line-height: 1; }
.brk-val { font: 500 11px var(--mono); min-width: 46px; text-align: center; color: #3A382F; }
.brk-val.big { color: #8A6A28; }
.brk-val.dim { color: var(--dim); }
.slot-end { font: 400 11.5px var(--mono); color: var(--sub); }
.slot-mins { font: 400 10.5px var(--mono); color: var(--faint); }
.slot-del { border: none; background: transparent; color: var(--red); font-size: 13px; cursor: pointer; padding: 2px 6px; }
.add-slot { align-self: flex-start; margin-top: 8px; background: transparent; border: 1px dashed var(--line-strong); border-radius: 6px; padding: 6px 12px; font-size: 11.5px; color: var(--blue); cursor: pointer; }

.footnote { font-size: 11px; color: var(--faint); line-height: 1.5; }
.footnote.wide { font-size: 11.5px; color: var(--muted); line-height: 1.55; padding: 0 4px 8px; }
</style>
