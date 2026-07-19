<script setup>
import { computed } from 'vue'
import { store } from '../store/index.js'
import { ALL_DAYS } from '../utils/kinds.js'

const props = defineProps({
  teacher: { type: Object, required: true },
})

const dayIdxs = computed(() => {
  const f = store.state.periods.fall
  const s = store.state.periods.spring
  const out = []
  for (let i = 0; i < 7; i++) {
    if ((f && f.activeDays[i]) || (s && s.activeDays[i])) out.push(i)
  }
  return out.length ? out : [0, 1, 2, 3, 4]
})

const slotsN = computed(() => {
  const f = store.state.periods.fall
  const s = store.state.periods.spring
  return Math.max(f ? f.slotsPerDay : 7, s ? s.slotsPerDay : 7)
})

const c = computed(() => props.teacher.c || { hard: [], soft: [], method: null, max: null })

function save(next) {
  store.setTeacherConstraints(props.teacher.id, next)
}

function withC(fn) {
  const next = props.teacher.c
    ? JSON.parse(JSON.stringify(props.teacher.c))
    : { hard: [], soft: [], method: null, max: 4 }
  fn(next)
  save(next)
}

function cellState(d, s) {
  const k = d + '-' + s
  if (c.value.method === d) return 'method'
  if (c.value.hard.indexOf(k) >= 0) return 'hard'
  if (c.value.soft.indexOf(k) >= 0) return 'soft'
  return 'free'
}

const cellTip = { method: 'Методический день', hard: 'Недоступен', soft: 'Нежелательно', free: 'Свободно' }

/* клик циклит: свободно → недоступно → нежелательно → свободно */
function cycleCell(d, s) {
  if (c.value.method === d) return
  const k = d + '-' + s
  withC((cc) => {
    const hi = cc.hard.indexOf(k)
    const si = cc.soft.indexOf(k)
    if (hi >= 0) { cc.hard.splice(hi, 1); cc.soft.push(k) }
    else if (si >= 0) cc.soft.splice(si, 1)
    else cc.hard.push(k)
  })
}

function toggleMethod(d) {
  withC((cc) => { cc.method = cc.method === d ? null : d })
}

function maxDec() { withC((cc) => { cc.max = Math.max(1, (cc.max || 4) - 1) }) }
function maxInc() { withC((cc) => { cc.max = Math.min(8, (cc.max || 4) + 1) }) }
</script>

<template>
  <div class="avail">
    <div class="grid" :style="{ gridTemplateColumns: '26px repeat(' + dayIdxs.length + ', 44px)' }">
      <span></span>
      <span v-for="d in dayIdxs" :key="'h' + d" class="day-head">{{ ALL_DAYS[d] }}</span>
      <template v-for="s in slotsN" :key="'r' + s">
        <span class="row-label">{{ s }}</span>
        <span
          v-for="d in dayIdxs"
          :key="d + '-' + s"
          class="cell"
          :class="cellState(d, s - 1)"
          :title="cellTip[cellState(d, s - 1)]"
          @click="cycleCell(d, s - 1)"
        ></span>
      </template>
    </div>
    <div class="legend">
      <span><span class="sw sw-hard"></span> недоступен</span>
      <span><span class="sw sw-soft"></span> нежелательно</span>
      <span><span class="sw sw-method"></span> методический день</span>
    </div>
    <div class="row-opts">
      <div class="opt">
        <span class="field-label">МЕТОДИЧЕСКИЙ ДЕНЬ</span>
        <div class="method-btns">
          <button
            v-for="d in dayIdxs"
            :key="'m' + d"
            class="pick method-btn"
            :class="{ on: c.method === d }"
            @click="toggleMethod(d)"
          >{{ ALL_DAYS[d] }}</button>
        </div>
      </div>
      <div class="opt">
        <span class="field-label">МАКСИМУМ ПАР В ДЕНЬ</span>
        <div class="stepper">
          <button class="step" @click="maxDec">−</button>
          <span class="step-val mono">{{ c.max ? c.max : '—' }}</span>
          <button class="step" @click="maxInc">＋</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.avail { display: flex; flex-direction: column; gap: 12px; }
.grid { display: grid; gap: 3px; }
.day-head { text-align: center; font: 400 10px var(--mono); color: var(--faint); }
.row-label { align-self: center; font: 400 10px var(--mono); color: var(--faint); text-align: center; }
.cell { height: 24px; border-radius: 4px; cursor: pointer; }
.cell.free { background: var(--hover); border: 1px solid rgba(0, 0, 0, 0.10); }
.cell.hard { background: var(--fg); }
.cell.soft { background: rgba(176, 124, 31, 0.45); }
.cell.method {
  background: repeating-linear-gradient(45deg, #D6D2C8, #D6D2C8 3px, #ECEAE4 3px, #ECEAE4 6px);
  cursor: not-allowed;
}
.legend { display: flex; gap: 14px; font-size: 11px; color: var(--sub); }
.sw { display: inline-block; width: 11px; height: 11px; border-radius: 3px; vertical-align: -1px; }
.sw-hard { background: var(--fg); }
.sw-soft { background: rgba(176, 124, 31, 0.45); }
.sw-method { background: repeating-linear-gradient(45deg, #D6D2C8, #D6D2C8 3px, #ECEAE4 3px, #ECEAE4 6px); }

.row-opts { display: flex; gap: 20px; flex-wrap: wrap; }
.opt { display: flex; flex-direction: column; gap: 5px; }
.method-btns { display: flex; gap: 4px; }
.method-btn { font-size: 11.5px; padding: 4px 10px; border-radius: 6px; }
.stepper { display: flex; align-items: center; gap: 6px; }
.step {
  border: 1px solid var(--line-strong);
  background: var(--panel);
  width: 26px;
  height: 26px;
  border-radius: 6px;
  cursor: pointer;
}
.step-val { font: 500 13px var(--mono); min-width: 26px; text-align: center; }
</style>
