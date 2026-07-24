<script setup>
import { computed, onUnmounted } from 'vue'
import { store } from '../../store/index.js'
import { api } from '../../api/index.js'
import { kindOf } from '../../utils/kinds.js'
import { ui, enriched } from './useSchedule.js'

const gen = computed(() => ui.gen)

const placedN = computed(() => enriched.value.filter((l) => l.d != null).length)
const unplacedN = computed(() => enriched.value.filter((l) => l.d == null).length)
const totalN = computed(() => enriched.value.length)
const noConstraints = computed(() => store.state.teachers.filter((t) => !t.c).length)

const checks = computed(() => {
  const mk = (ok, text, fixLabel, fix) => ({
    icon: ok ? '✓' : '⚠',
    color: ok ? '#1F8A5B' : '#B07C1F',
    border: ok ? 'rgba(31,138,91,0.25)' : 'rgba(176,124,31,0.35)',
    bg: ok ? 'rgba(31,138,91,0.03)' : 'rgba(176,124,31,0.04)',
    text, fixLabel, fix,
  })
  return [
    mk(true, 'Назначено пар: ' + totalN.value + ' (из «Распределения»), в сетке ' + placedN.value),
    mk(
      noConstraints.value === 0,
      noConstraints.value
        ? 'У ' + noConstraints.value + ' преподавателей не задана доступность — генератор считает их полностью доступными'
        : 'Доступность задана у всех преподавателей',
      'Задать',
      () => { const t = store.state.teachers.find((x) => !x.c) || store.state.teachers[0]; ui.co = { tid: t.id } },
    ),
    mk(true, 'Справочник аудиторий: ' + store.state.rooms.length + ' аудиторий, типы заданы', 'Открыть', () => { ui.rooms = true }),
    mk(true, 'Нормы пар/нед: авто из часов плана, ручных правок нет'),
  ]
})

const modes = computed(() => [
  {
    k: 'rebuild',
    title: 'Пересобрать всё расписание',
    desc: 'Снимет ' + placedN.value + ' пар и расставит заново вместе с пулом. Результат можно откатить одним шагом.',
  },
  {
    k: 'fill',
    title: 'Только доразместить',
    desc: 'Расставленные пары не трогаются; генератор заполнит пустые слоты парами из пула (' + unplacedN.value + ').',
  },
])

const issues = computed(() => {
  const out = []
  const sum = gen.value && gen.value.summary
  if (!sum) return out
  sum.unplaced.slice(0, 4).forEach((l) => out.push({
    icon: '✕', color: '#C24536',
    text: l.disc + ' (' + kindOf(l.kind).label.toLowerCase() + ') · ' + l.g + ' — не нашлось слота без конфликта; пара осталась в пуле',
  }))
  if (sum.softN) out.push({ icon: '◐', color: '#B07C1F', text: 'Нарушено мягких пожеланий: ' + sum.softN + ' — см. панель проблем после принятия' })
  return out
})

const title = computed(() => {
  if (!gen.value) return ''
  return gen.value.phase === 'done' ? 'Результат генерации' : gen.value.phase === 'run' ? 'Генерация…' : 'Генерация расписания'
})

let pollT = null

async function run() {
  const { jobId } = await api.startGeneration(store.state.yearId, store.state.period, gen.value.mode)
  ui.gen = { ...gen.value, phase: 'run', jobId, pct: 0, stage: 'Готовлю данные…', live: '' }
  pollT = setInterval(async () => {
    if (!ui.gen || ui.gen.phase !== 'run') { clearInterval(pollT); return }
    const st = await api.getGenerationStatus(ui.gen.jobId)
    if (!ui.gen) return
    if (st.status === 'done') {
      clearInterval(pollT)
      ui.gen = { ...ui.gen, phase: 'done', pct: 100, summary: st.summary }
    } else {
      ui.gen = { ...ui.gen, pct: st.pct, stage: st.stage, live: st.live }
    }
  }, 130)
}

function cancel() {
  clearInterval(pollT)
  if (gen.value && gen.value.jobId && gen.value.phase === 'run') api.cancelGeneration(gen.value.jobId)
  ui.gen = null
}

function rollback() {
  if (gen.value && gen.value.jobId) api.rollbackGeneration(gen.value.jobId)
  ui.gen = null
}

async function accept() {
  const jobId = gen.value.jobId
  ui.gen = null
  await store.acceptGeneration(jobId)
}

function onBackdrop() {
  if (gen.value && gen.value.phase !== 'run') cancel()
}

onUnmounted(() => {
  clearInterval(pollT)
})
</script>

<template>
  <div v-if="gen" class="overlay" @click="onBackdrop">
    <div class="drawer" @click.stop>
      <div class="head">
        <span class="head-title">{{ title }}</span>
        <span class="x-close" title="Закрыть (Esc)" @click="gen.phase !== 'run' && cancel()">×</span>
      </div>

      <!-- PREP -->
      <template v-if="gen.phase === 'prep'">
        <div class="body">
          <div class="intro">
            Генератор — черновик: он расставит пары с учётом ограничений, дальше — доводка руками.
            Результат можно откатить целиком одним Ctrl+Z.
          </div>
          <div class="sect">
            <div class="micro">ГОТОВНОСТЬ ДАННЫХ</div>
            <div
              v-for="(g, i) in checks"
              :key="i"
              class="check"
              :style="{ border: '1px solid ' + g.border, background: g.bg }"
            >
              <span class="check-ico" :style="{ color: g.color }">{{ g.icon }}</span>
              <div class="check-text">{{ g.text }}</div>
              <span v-if="g.fix" class="check-fix" @click="g.fix">{{ g.fixLabel }}</span>
            </div>
          </div>
          <div class="sect">
            <div class="micro">РЕЖИМ</div>
            <div
              v-for="m in modes"
              :key="m.k"
              class="mode"
              :class="{ on: gen.mode === m.k }"
              @click="gen.mode = m.k"
            >
              <span class="radio" :class="{ on: gen.mode === m.k }"><span class="radio-dot"></span></span>
              <div>
                <div class="mode-title">{{ m.title }}</div>
                <div class="mode-desc">{{ m.desc }}</div>
              </div>
            </div>
          </div>
          <div v-if="gen.mode === 'rebuild' && placedN > 0" class="note-danger">
            <span style="color: #C24536; flex: none">⚠</span>
            <span>Будет переставлено {{ placedN }} пар. Результат можно откатить одним шагом.</span>
          </div>
        </div>
        <div class="foot">
          <button class="btn btn-lg" @click="cancel">Отмена</button>
          <span style="flex: 1"></span>
          <button class="btn-primary btn-lg" @click="run">Запустить генерацию</button>
        </div>
      </template>

      <!-- RUN -->
      <template v-else-if="gen.phase === 'run'">
        <div class="run-body">
          <span class="spinner"></span>
          <div class="run-progress">
            <div class="run-row">
              <span>{{ gen.stage }}</span>
              <span class="mono" style="font-size: 11.5px">{{ Math.round(gen.pct) }} %</span>
            </div>
            <div class="bar"><div class="bar-fill" :style="{ width: gen.pct + '%' }"></div></div>
            <div class="live mono">{{ gen.live }}</div>
          </div>
          <button class="btn btn-lg" @click="cancel">Отменить</button>
          <div class="run-hint">
            Отмена вернёт сетку к состоянию до запуска. Сетка на время генерации доступна только для чтения.
          </div>
        </div>
      </template>

      <!-- DONE -->
      <template v-else-if="gen.phase === 'done'">
        <div class="body">
          <div class="stats">
            <div class="stat" style="border: 1px solid rgba(31,138,91,0.3); background: rgba(31,138,91,0.06)">
              <div class="stat-n" style="color: #1F8A5B">{{ gen.summary.placedN }}</div>
              <div class="stat-l">размещено</div>
            </div>
            <div
              class="stat"
              :style="gen.summary.unplacedN
                ? { border: '1px solid rgba(194,69,54,0.3)', background: 'rgba(194,69,54,0.05)' }
                : { border: '1px solid rgba(0,0,0,0.1)', background: '#FBFAF8' }"
            >
              <div class="stat-n" :style="{ color: gen.summary.unplacedN ? '#C24536' : '#8A857C' }">{{ gen.summary.unplacedN }}</div>
              <div class="stat-l">не размещено</div>
            </div>
            <div
              class="stat"
              :style="gen.summary.softN
                ? { border: '1px solid rgba(176,124,31,0.35)', background: 'rgba(176,124,31,0.05)' }
                : { border: '1px solid rgba(0,0,0,0.1)', background: '#FBFAF8' }"
            >
              <div class="stat-n" :style="{ color: gen.summary.softN ? '#B07C1F' : '#8A857C' }">{{ gen.summary.softN }}</div>
              <div class="stat-l">пожеланий нарушено</div>
            </div>
          </div>
          <div class="intro">
            <template v-if="gen.mode === 'rebuild'">Пересобрано {{ gen.summary.moved }} пар. </template>
            Жёсткие ограничения не нарушены. Неразмещённые пары остались в пуле с причиной.
          </div>
          <div
            v-for="(gi, i) in issues"
            :key="i"
            class="check"
            style="border: 1px solid rgba(0,0,0,0.1)"
          >
            <span class="check-ico" :style="{ color: gi.color }">{{ gi.icon }}</span>
            <div class="check-text" style="font-size: 12px">{{ gi.text }}</div>
          </div>
          <div class="run-hint" style="text-align: left; max-width: none">
            Новые пары подсвечены в сетке. «Принять» фиксирует результат (откат — Ctrl+Z одним шагом),
            «Откатить» возвращает всё как было.
          </div>
        </div>
        <div class="foot">
          <button class="btn btn-lg" @click="rollback">Откатить всё</button>
          <span style="flex: 1"></span>
          <button class="accept-btn" @click="accept">Принять результат</button>
        </div>
      </template>
    </div>
  </div>
</template>

<style scoped>
.overlay {
  position: fixed;
  inset: 0;
  z-index: 60;
  background: rgba(31, 30, 27, 0.35);
  display: flex;
  justify-content: flex-end;
}
.drawer {
  width: 430px;
  max-width: 94vw;
  background: var(--panel);
  height: 100%;
  box-shadow: -12px 0 32px rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.head {
  flex: none;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 14px 18px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.08);
}
.head-title { font-size: 15px; font-weight: 600; flex: 1; }
.body { flex: 1; overflow-y: auto; padding: 16px 18px; display: flex; flex-direction: column; gap: 14px; }
.foot { flex: none; display: flex; gap: 8px; padding: 14px 18px; border-top: 1px solid rgba(0, 0, 0, 0.08); }
.intro { font-size: 12.5px; line-height: 1.55; color: var(--sub); }
.sect { display: flex; flex-direction: column; gap: 6px; }
.check { display: flex; gap: 9px; align-items: baseline; border-radius: var(--r-lg); padding: 9px 11px; }
.check-ico { flex: none; font-size: 12px; }
.check-text { flex: 1; font-size: 12.5px; line-height: 1.5; color: #3A382F; }
.check-fix { flex: none; font-size: 11.5px; font-weight: 500; color: var(--blue); cursor: pointer; }

.mode {
  display: flex;
  gap: 10px;
  align-items: baseline;
  border: 1.5px solid rgba(0, 0, 0, 0.12);
  border-radius: var(--r-lg);
  padding: 10px 12px;
  cursor: pointer;
  background: var(--panel);
}
.mode.on { border-color: var(--fg); background: var(--hover); }
.radio {
  flex: none;
  width: 14px;
  height: 14px;
  border-radius: 50%;
  border: 1.5px solid rgba(0, 0, 0, 0.3);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  align-self: center;
}
.radio.on { border-color: var(--fg); }
.radio-dot { width: 7px; height: 7px; border-radius: 50%; background: transparent; }
.radio.on .radio-dot { background: var(--fg); }
.mode-title { font-size: 13px; font-weight: 600; }
.mode-desc { font-size: 11.5px; color: var(--sub); line-height: 1.5; margin-top: 2px; }

.run-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  padding: 24px;
}
.run-progress { width: 100%; max-width: 300px; display: flex; flex-direction: column; gap: 8px; }
.run-row { display: flex; justify-content: space-between; font-size: 12.5px; color: var(--sub); }
.bar { width: 100%; height: 5px; background: var(--active); border-radius: 3px; overflow: hidden; }
.bar-fill { height: 100%; background: var(--fg); transition: width 0.15s; }
.live { font: 400 11.5px var(--mono); color: var(--faint); text-align: center; }
.run-hint { font-size: 11.5px; color: var(--muted); text-align: center; max-width: 280px; line-height: 1.5; }

.stats { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; }
.stat { border-radius: var(--r-lg); padding: 10px; text-align: center; }
.stat-n { font-size: 20px; font-weight: 700; }
.stat-l { font-size: 11px; color: var(--sub); }
.accept-btn {
  border: none;
  background: var(--green);
  color: #FFFFFF;
  font: 500 13px var(--sans);
  padding: 9px 18px;
  border-radius: var(--r-md);
  cursor: pointer;
}
.accept-btn:hover { background: var(--green-dark); }
</style>
