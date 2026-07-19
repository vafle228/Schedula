<script setup>
import { reactive, computed } from 'vue'
import { store } from '../../store/index.js'
import { ALL_DAYS } from '../../utils/kinds.js'

const fall = store.state.periods.fall
const spring = store.state.periods.spring

const form = reactive({
  dirty: false,
  saved: false,
  fall: [fall.dateFrom, fall.dateTo],
  spring: [spring.dateFrom, spring.dateTo],
  days: [...fall.activeDays],
  slots: fall.slotsPerDay,
  bells: fall.bells.map((b) => ({ ...b })),
})

function mark() {
  form.dirty = true
  form.saved = false
}

function toggleDay(i) {
  form.days[i] = !form.days[i]
  mark()
}

function slotsDec() {
  form.slots = Math.max(4, form.slots - 1)
  mark()
}
function slotsInc() {
  form.slots = Math.min(8, form.slots + 1)
  while (form.bells.length < form.slots) form.bells.push({ from: '', to: '' })
  mark()
}

const bellRows = computed(() => form.bells.slice(0, form.slots))

async function save() {
  if (!form.dirty) return
  const shared = {
    activeDays: [...form.days],
    slotsPerDay: form.slots,
    bells: form.bells.slice(0, form.slots).map((b) => ({ ...b })),
  }
  await store.savePeriods(
    { dateFrom: form.fall[0], dateTo: form.fall[1], ...shared },
    { dateFrom: form.spring[0], dateTo: form.spring[1], ...shared },
  )
  form.dirty = false
  form.saved = true
}
</script>

<template>
  <div class="view">
    <!-- ======= header ======= -->
    <div class="head">
      <span class="head-title">Настройки периода</span>
      <span class="year-chip mono">2026 / 2027</span>
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
        <!-- semesters -->
        <div class="panel sect">
          <div class="sect-head">
            <span class="sect-title">Семестры</span>
            <span class="sect-sub">Границы определяют, на какой период строится расписание и в каких пределах задаётся отпуск</span>
          </div>
          <div class="sem-grid">
            <span></span>
            <span class="col-head mono">НАЧАЛО</span>
            <span class="col-head mono">КОНЕЦ</span>
            <span class="sem-name">Осенний</span>
            <input v-model="form.fall[0]" class="input mono sem-input" @input="mark">
            <input v-model="form.fall[1]" class="input mono sem-input" @input="mark">
            <span class="sem-name">Весенний</span>
            <input v-model="form.spring[0]" class="input mono sem-input" @input="mark">
            <input v-model="form.spring[1]" class="input mono sem-input" @input="mark">
          </div>
        </div>

        <!-- week -->
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
          <div class="slots-row">
            <span class="slots-label">Пар в день</span>
            <button class="step" @click="slotsDec">−</button>
            <span class="slots-val mono">{{ form.slots }}</span>
            <button class="step" @click="slotsInc">＋</button>
            <span class="slots-note">определяет число строк сетки</span>
          </div>
        </div>

        <!-- bells -->
        <div class="panel sect">
          <div class="sect-head">
            <span class="sect-title">Сетка звонков</span>
            <span class="sect-sub">Время пар — подписи строк в «Расписании» и в экспорте Excel</span>
          </div>
          <div class="bells">
            <div v-for="(b, i) in bellRows" :key="i" class="bell-row">
              <span class="bell-n mono">{{ i + 1 }} пара</span>
              <input v-model="b.from" class="input mono bell-input" @input="mark">
              <span class="bell-dash">—</span>
              <input v-model="b.to" class="input mono bell-input" @input="mark">
            </div>
          </div>
        </div>

        <div class="footnote">
          Изменения применяются ко всему периоду: сетка «Расписания», проверка конфликтов и генератор
          перечитывают конфиг после сохранения. Уже размещённые пары при сужении недели или сетки
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
  color: var(--orange-dark);
  background: rgba(217, 119, 6, 0.08);
  border-radius: 4px;
  padding: 2px 7px;
}
.dirty-note { font-size: 11.5px; color: var(--orange-dark); }
.save-btn {
  flex: none;
  border: none;
  color: #FFFFFF;
  font: 500 13px var(--sans);
  padding: 8px 16px;
  border-radius: var(--r-md);
}

.body { flex: 1; overflow-y: auto; padding: 16px; }
.col { max-width: 680px; display: flex; flex-direction: column; gap: 14px; }

.sect { padding: 16px 18px; gap: 12px; overflow: visible; }
.sect-head { display: flex; flex-direction: column; gap: 2px; }
.sect-title { font-size: 13.5px; font-weight: 600; }
.sect-sub { font-size: 11.5px; color: var(--muted); }

.sem-grid { display: grid; grid-template-columns: 110px 1fr 1fr; gap: 8px; align-items: center; }
.col-head { font: 500 10px var(--mono); letter-spacing: 0.06em; color: var(--faint); }
.sem-name { font-size: 12.5px; font-weight: 600; color: var(--sub); }
.sem-input { font: 400 12.5px var(--mono); }

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

.slots-row { display: flex; align-items: center; gap: 10px; }
.slots-label { font-size: 12.5px; font-weight: 600; color: var(--sub); }
.step {
  border: 1px solid var(--line-strong);
  background: var(--panel);
  width: 28px;
  height: 28px;
  border-radius: var(--r-md);
  cursor: pointer;
}
.slots-val { font: 500 14px var(--mono); min-width: 24px; text-align: center; }
.slots-note { font-size: 11.5px; color: var(--muted); }

.bells { display: flex; flex-direction: column; gap: 4px; }
.bell-row { display: flex; align-items: center; gap: 10px; }
.bell-n { flex: none; width: 44px; font: 400 11px var(--mono); color: var(--faint); }
.bell-input {
  flex: none;
  width: 64px;
  font: 400 12px var(--mono);
  text-align: center;
  padding: 5px 8px;
  border-radius: 6px;
}
.bell-dash { color: var(--faint); font-size: 11px; }

.footnote { font-size: 11.5px; color: var(--muted); line-height: 1.55; padding: 0 4px 8px; }
</style>
