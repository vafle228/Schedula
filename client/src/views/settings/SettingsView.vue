<script setup>
import { reactive, ref, computed, watch } from 'vue'
import { store } from '../../store/index.js'
import { ALL_DAYS } from '../../utils/kinds.js'
import { slotEnd, slotLen, recalcStarts } from '../../utils/slots.js'

const activeId = computed(() => store.state.period)
const activeSem = computed(() => store.state.semesters.find((s) => s.status === 'active'))
const activeName = computed(() => (activeSem.value ? activeSem.value.name : 'Осень 2026/27'))

const form = reactive({ dirty: false, saved: false, acadMin: 45, days: [], slots: [], ag: {} })

function loadForm() {
  const p = store.state.periods[activeId.value]
  if (!p) return
  form.dirty = false
  form.saved = false
  form.acadMin = p.acadMin || 45
  form.days = [...p.activeDays]
  form.slots = (p.slots || []).map((s) => ({ ...s }))
  form.ag = { start: '08:30', brk: 15, long: 30, longAfter: 2, ...(p.ag || {}) }
}
loadForm()
watch(activeId, loadForm)

function mark() { form.dirty = true; form.saved = false }

/* ---------- semesters ---------- */

const semRows = computed(() => store.state.semesters.map((s) => {
  const st = s.status
  return {
    id: s.id,
    name: s.name,
    range: s.from + ' — ' + s.to,
    weight: st === 'active' ? 600 : 500,
    bg: st === 'active' ? 'rgba(31,138,91,0.05)' : 'transparent',
    status: st === 'active' ? 'активный' : st === 'done' ? 'завершён' : 'черновик',
    statusCls: st,
    canActivate: st !== 'active' && s.current,
  }
}))

const newSem = ref(null)
function openNewSem() { newSem.value = { name: '', from: '', to: '', copy: true } }
const nsValid = computed(() => !!(newSem.value && newSem.value.name.trim() && newSem.value.from.trim() && newSem.value.to.trim()))
async function createSem() {
  if (!nsValid.value) return
  const ns = newSem.value
  await store.createSemester({ name: ns.name.trim(), from: ns.from.trim(), to: ns.to.trim() })
  newSem.value = null
}

/* ---------- academic hour ---------- */

function ahDec() { form.acadMin = Math.max(30, form.acadMin - 5); mark() }
function ahInc() { form.acadMin = Math.min(60, form.acadMin + 5); mark() }
const exType = computed(() => 'урок 2 ак.ч = ' + slotLen(2, form.acadMin) + ' мин, консультация 1 ак.ч = ' + form.acadMin + ' мин')

/* ---------- week ---------- */

function toggleDay(i) { form.days[i] = !form.days[i]; mark() }

/* ---------- slots (bells) ---------- */

const slotRows = computed(() => form.slots.map((b, i) => ({
  n: i + 1,
  start: b.start,
  hours: b.hours,
  end: slotEnd(b.start, b.hours, form.acadMin),
  mins: slotLen(b.hours, form.acadMin),
})))

function setSlotStart(i, v) { form.slots[i].start = v; mark() }
function setSlotHours(i, h) { form.slots[i].hours = h; mark() }
function delSlot(i) { form.slots.splice(i, 1); mark() }
function addSlot() {
  const last = form.slots[form.slots.length - 1]
  const start = last ? slotEnd(last.start, last.hours, form.acadMin) : form.ag.start
  form.slots.push({ start, hours: 2 })
  mark()
}

function agDec(key, min, step = 5) { form.ag[key] = Math.max(min, form.ag[key] - step); mark() }
function agInc(key, max, step = 5) { form.ag[key] = Math.min(max, form.ag[key] + step); mark() }
function recalc() {
  form.slots = recalcStarts(form.slots, form.ag, form.acadMin)
  mark()
}

/* ---------- save ---------- */

async function save() {
  if (!form.dirty) return
  await store.savePeriod(activeId.value, {
    acadMin: form.acadMin,
    activeDays: [...form.days],
    slots: form.slots.map((s) => ({ ...s })),
    ag: { ...form.ag },
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
      <span class="year-chip mono" title="Настройки ниже относятся к активному семестру">активный семестр: {{ activeName }}</span>
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
        <!-- ===== semesters ===== -->
        <div class="panel sect">
          <div class="sect-head-row">
            <div class="sect-head">
              <span class="sect-title">Семестры</span>
              <span class="sect-sub">Все разделы приложения — распределение, расписание, учёт часов — работают с активным семестром. Переключение меняет данные везде.</span>
            </div>
            <button class="ghost-btn" @click="openNewSem"><span class="plus">＋</span>Новый семестр</button>
          </div>
          <div class="sem-table">
            <div class="sem-thead mono">
              <span>СЕМЕСТР</span><span>ПЕРИОД</span><span>СТАТУС</span><span></span>
            </div>
            <div v-for="s in semRows" :key="s.id" class="sem-row" :style="{ background: s.bg }">
              <span class="sem-name" :style="{ fontWeight: s.weight }">{{ s.name }}</span>
              <span class="sem-range mono">{{ s.range }}</span>
              <span class="sem-status mono" :class="s.statusCls">{{ s.status }}</span>
              <span
                v-if="s.canActivate"
                class="sem-act"
                title="Все разделы переключатся на этот семестр"
                @click="store.activateSemester(s.id)"
              >сделать активным</span>
              <span v-else></span>
            </div>
          </div>

          <div v-if="newSem" class="ns-form">
            <span class="micro">НОВЫЙ СЕМЕСТР</span>
            <div class="ns-fields">
              <div class="fld" style="flex: 1">
                <span class="field-label">НАЗВАНИЕ</span>
                <input v-model="newSem.name" class="input" placeholder="напр. Осень 2027/28">
              </div>
              <div class="fld" style="flex: none; width: 120px">
                <span class="field-label">НАЧАЛО</span>
                <input v-model="newSem.from" class="input mono" placeholder="01.09.2027">
              </div>
              <div class="fld" style="flex: none; width: 120px">
                <span class="field-label">КОНЕЦ</span>
                <input v-model="newSem.to" class="input mono" placeholder="26.12.2027">
              </div>
            </div>
            <label class="ns-copy" @click.prevent="newSem.copy = !newSem.copy">
              <span class="ns-box" :class="{ on: newSem.copy }">{{ newSem.copy ? '✓' : '' }}</span>
              скопировать сетку звонков, учебную неделю и академический час из активного семестра
            </label>
            <div class="ns-actions">
              <button class="btn-primary" :disabled="!nsValid" @click="createSem">Создать семестр</button>
              <button class="btn" @click="newSem = null">Отмена</button>
            </div>
          </div>
          <div class="footnote">Новый семестр создаётся черновиком: настройте сетку и неделю, сделайте назначения в «Распределении» — и переключите его в активные. Завершённые семестры доступны только для чтения и экспорта.</div>
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
            <span>· <b>сетка звонков</b> — конец слота считается из начала и числа ак. часов</span>
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
            <span class="sect-sub">Слот = 2 или 1 ак.ч. Строки сетки «Расписания» повторяют эти слоты один в один; занятие занимает слот целиком</span>
          </div>

          <div class="ag-box">
            <div class="ag-head">
              <span class="micro">АВТОРАСЧЁТ ВРЕМЕНИ</span>
              <span class="ag-note">время каждого слота выводится из ак. часа и перемен — руками задаётся только состав слотов</span>
            </div>
            <div class="ag-controls">
              <div class="ag-fld">
                <span class="field-label">НАЧАЛО ДНЯ</span>
                <input :value="form.ag.start" class="input mono ag-start" @change="form.ag.start = $event.target.value; mark()">
              </div>
              <div class="ag-fld">
                <span class="field-label">ПЕРЕМЕНА</span>
                <div class="ag-step">
                  <button class="mini" @click="agDec('brk', 5)">−</button>
                  <span class="mono ag-val">{{ form.ag.brk }} мин</span>
                  <button class="mini" @click="agInc('brk', 30)">＋</button>
                </div>
              </div>
              <div class="ag-fld">
                <span class="field-label">БОЛЬШАЯ ПЕРЕМЕНА · ПОСЛЕ СЛОТА {{ form.ag.longAfter }}</span>
                <div class="ag-step">
                  <button class="mini" @click="agDec('long', 10)">−</button>
                  <span class="mono ag-val">{{ form.ag.long }} мин</span>
                  <button class="mini" @click="agInc('long', 60)">＋</button>
                </div>
              </div>
              <button class="recalc-btn" title="Пересчитать время всех слотов от начала дня" @click="recalc">⟳ Пересчитать время</button>
            </div>
          </div>

          <div class="slot-table">
            <div class="slot-thead mono">
              <span>СЛОТ</span><span>НАЧАЛО</span><span>АК. ЧАСОВ</span><span>ВРЕМЯ</span><span></span>
            </div>
            <div v-for="(b, i) in slotRows" :key="i" class="slot-row">
              <span class="slot-n mono">{{ b.n }}</span>
              <input :value="b.start" class="input mono slot-start" @change="setSlotStart(i, $event.target.value)">
              <span class="hseg">
                <button :class="{ on: b.hours === 1 }" @click="setSlotHours(i, 1)">1 ак.ч</button>
                <button :class="{ on: b.hours === 2 }" @click="setSlotHours(i, 2)">2 ак.ч</button>
              </span>
              <span class="slot-time mono">→ {{ b.end }} <span class="dim">· {{ b.mins }} мин</span></span>
              <button class="slot-del" title="Удалить слот" @click="delSlot(i)">✕</button>
            </div>
            <button class="add-slot" @click="addSlot">+ слот</button>
          </div>
          <div class="footnote">Конец слота = начало + ак. часы × {{ form.acadMin }} мин (+5 мин между часами внутри пары). Автогенератор не ставит занятие 2 ак.ч в слот на 1 ак.ч.</div>
        </div>

        <div class="footnote wide">
          Изменения применяются к активному семестру: сетка «Расписания», проверка конфликтов и генератор
          перечитывают конфиг после сохранения. Уже размещённые занятия при сужении недели или сетки
          помечаются как проблемы, а не удаляются.
        </div>
      </div>
    </div>
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

/* semesters */
.sem-table { display: flex; flex-direction: column; }
.sem-thead, .sem-row {
  display: grid;
  grid-template-columns: 1fr 170px 100px 130px;
  gap: 8px;
  align-items: center;
}
.sem-thead { padding: 4px 0; font: 500 10px var(--mono); letter-spacing: 0.06em; color: var(--faint); }
.sem-row { padding: 8px 0; border-top: 1px solid rgba(0, 0, 0, 0.06); }
.sem-name { font-size: 12.5px; }
.sem-range { font: 400 11px var(--mono); color: var(--muted); }
.sem-status { justify-self: start; font: 500 9.5px var(--mono); border-radius: 4px; padding: 2px 7px; }
.sem-status.active { color: var(--green); background: rgba(31, 138, 91, 0.10); }
.sem-status.done { color: var(--muted); background: var(--chip); }
.sem-status.draft { color: var(--amber); background: rgba(176, 124, 31, 0.10); }
.sem-act { justify-self: end; font-size: 11.5px; color: var(--blue); cursor: pointer; }
.sem-act:hover { text-decoration: underline; }

.ns-form {
  border: 1.5px solid rgba(31, 138, 91, 0.45);
  border-radius: var(--r-lg);
  padding: 12px;
  background: #FBFAF8;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.ns-fields { display: flex; gap: 8px; }
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
.ns-actions { display: flex; gap: 6px; }

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

/* auto builder */
.ag-box { background: #FBFAF8; border: 1px solid rgba(0, 0, 0, 0.08); border-radius: var(--r-lg); padding: 11px 12px; display: flex; flex-direction: column; gap: 9px; }
.ag-head { display: flex; align-items: baseline; gap: 8px; flex-wrap: wrap; }
.ag-note { font-size: 11px; color: var(--faint); }
.ag-controls { display: flex; gap: 14px; align-items: flex-end; flex-wrap: wrap; }
.ag-fld { display: flex; flex-direction: column; gap: 4px; }
.ag-start { width: 64px; text-align: center; font: 400 12px var(--mono); padding: 6px 8px; }
.ag-step { display: flex; align-items: center; gap: 5px; }
.ag-val { font: 500 12px var(--mono); min-width: 44px; text-align: center; }
.mini { border: 1px solid var(--line-soft); background: var(--panel); width: 22px; height: 22px; border-radius: 5px; cursor: pointer; font-size: 11px; }
.recalc-btn { border: none; background: var(--fg); color: #FFF; font: 500 12px var(--sans); padding: 8px 14px; border-radius: var(--r-md); cursor: pointer; }
.recalc-btn:hover { background: var(--fg-hover); }

/* slots */
.slot-table { display: flex; flex-direction: column; }
.slot-thead, .slot-row {
  display: grid;
  grid-template-columns: 52px 84px 150px 1fr 30px;
  gap: 8px;
  align-items: center;
}
.slot-thead { padding: 4px 0; font: 500 10px var(--mono); letter-spacing: 0.06em; color: var(--faint); }
.slot-row { padding: 6px 0; border-top: 1px solid rgba(0, 0, 0, 0.06); }
.slot-n { font: 400 11px var(--mono); color: var(--faint); }
.slot-start { width: 64px; text-align: center; font: 400 12px var(--mono); padding: 5px 8px; background: #FBFAF8; }
.hseg { display: inline-flex; background: #F2F0EB; border-radius: 6px; padding: 2px; gap: 2px; }
.hseg button { border: none; border-radius: 5px; padding: 4px 10px; font: 500 11px var(--sans); color: var(--muted); background: transparent; cursor: pointer; }
.hseg button.on { font-weight: 600; color: var(--fg); background: #FFF; box-shadow: 0 1px 2px rgba(0, 0, 0, 0.14); }
.slot-time { font: 400 11.5px var(--mono); color: var(--sub); }
.slot-time .dim { color: var(--faint); }
.slot-del { border: none; background: transparent; color: var(--red); font-size: 13px; cursor: pointer; padding: 2px 6px; }
.add-slot { align-self: flex-start; margin-top: 8px; background: transparent; border: 1px dashed var(--line-strong); border-radius: 6px; padding: 6px 12px; font-size: 11.5px; color: var(--blue); cursor: pointer; }

.footnote { font-size: 11px; color: var(--faint); line-height: 1.5; }
.footnote.wide { font-size: 11.5px; color: var(--muted); line-height: 1.55; padding: 0 4px 8px; }
</style>
