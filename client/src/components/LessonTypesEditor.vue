<script setup>
import { reactive, ref, computed, onMounted, onUnmounted } from 'vue'
import { store } from '../store/index.js'
import { confirmDelete } from '../composables/useConfirm.js'
import { plural } from '../utils/format.js'
import { randomPalette, suggestColor } from '../utils/colors.js'

const acadMin = computed(() => {
  const p = store.state.periods[store.state.period]
  return (p && p.acadMin) || 45
})

const usedColors = computed(() => store.state.topicTypes.map((t) => t.color))

const palOpen = ref(null) // 'new' | type.k
const palette = ref(randomPalette())

const newT = reactive({ label: '', acHours: 2, color: suggestColor(usedColors.value), err: '' })

const rows = computed(() => store.state.topicTypes.map((t) => ({
  ...t,
  minLabel: '· ' + t.acHours * acadMin.value + ' мин',
  usage: t.used ? t.used + ' ' + plural(t.used, 'тема', 'темы', 'тем') : 'не используется',
  locked: t.used > 0,
})))

function swatches(current) {
  const list = [current, ...palette.value.filter((x) => x !== current)].slice(0, 8)
  return list.map((v) => ({ v, current: v === current }))
}

function palToggle(id) {
  if (palOpen.value === id) { palOpen.value = null; return }
  palette.value = randomPalette()
  palOpen.value = id
}
function palShuffle() { palette.value = randomPalette() }
function palCloseAll() { palOpen.value = null }

function pick(id, v) {
  if (id === 'new') newT.color = v
  else store.patchTopicType(id, { color: v })
  palOpen.value = null
}

function newDur(delta) { newT.acHours = Math.min(4, Math.max(1, newT.acHours + delta)) }
function rowDur(t, delta) { store.patchTopicType(t.k, { acHours: Math.min(4, Math.max(1, t.acHours + delta)) }) }

async function addType() {
  const label = newT.label.trim()
  if (!label) { newT.err = 'Укажите название типа'; return }
  if (store.state.topicTypes.some((t) => t.label.toLowerCase() === label.toLowerCase())) {
    newT.err = 'Тип «' + label + '» уже есть'
    return
  }
  await store.createTopicType({ label, acHours: newT.acHours, color: newT.color })
  newT.label = ''
  newT.acHours = 2
  newT.color = suggestColor(usedColors.value)
  newT.err = ''
}

async function delType(t) {
  if (t.locked) return
  const ok = await confirmDelete({
    title: 'Удалить тип занятия?',
    message: 'Тип будет удалён из справочника и перестанет предлагаться в формах. Действие необратимо.',
    entityName: t.label,
  })
  if (ok) store.deleteTopicType(t.k)
}

function onKey(e) { if (e.key === 'Escape' && palOpen.value) palOpen.value = null }
onMounted(() => document.addEventListener('keydown', onKey))
onUnmounted(() => document.removeEventListener('keydown', onKey))
</script>

<template>
  <div class="lt">
    <!-- new type form -->
    <div class="lt-form">
      <div class="lt-form-head">
        <span class="micro">НОВЫЙ ТИП ЗАНЯТИЯ</span>
        <span class="hint">длительность — в ак. часах · минуты считаются из настройки «Академический час» ({{ acadMin }} мин)</span>
      </div>
      <div class="lt-form-row">
        <span class="pal-wrap">
          <button class="dot-btn" :style="{ background: newT.color }" title="Цвет типа — клик открывает варианты" @click="palToggle('new')"></button>
          <template v-if="palOpen === 'new'">
            <div class="pal-backdrop" @click="palCloseAll"></div>
            <div class="pal-pop">
              <span class="micro">ЦВЕТ ТИПА</span>
              <div class="pal-grid">
                <button
                  v-for="c in swatches(newT.color)"
                  :key="c.v"
                  class="sw"
                  :class="{ on: c.current }"
                  :style="{ background: c.v }"
                  :title="c.v"
                  @click="pick('new', c.v)"
                ></button>
              </div>
              <button class="shuffle" @click="palShuffle">⟳ другие варианты</button>
            </div>
          </template>
        </span>
        <input
          v-model="newT.label"
          class="input lt-name"
          placeholder="Название, напр. Семинар"
          @input="newT.err = ''"
          @keydown.enter="addType"
        >
        <div class="dur" title="Длительность в академических часах">
          <button class="step" @click="newDur(-1)">−</button>
          <span class="dur-val mono">{{ newT.acHours }} ак.ч</span>
          <button class="step" @click="newDur(1)">＋</button>
        </div>
        <button class="add-btn" @click="addType">＋ Добавить</button>
      </div>
      <div v-if="newT.err" class="form-err"><span>⚠</span><span>{{ newT.err }}</span></div>
    </div>

    <!-- table -->
    <div class="lt-table">
      <div class="lt-thead mono">
        <span>ЦВЕТ</span><span>ТИП</span><span>ДЛИТЕЛЬНОСТЬ</span><span>ИСПОЛЬЗОВАНИЕ</span><span></span>
      </div>
      <div v-for="t in rows" :key="t.k" class="lt-row">
        <span class="pal-wrap">
          <button class="dot-btn sm" :style="{ background: t.color }" title="Цвет типа — им подкрашены занятия в пуле и на сетке. Клик — выбрать другой" @click="palToggle(t.k)"></button>
          <template v-if="palOpen === t.k">
            <div class="pal-backdrop" @click="palCloseAll"></div>
            <div class="pal-pop">
              <span class="micro">ЦВЕТ ТИПА «{{ t.label }}»</span>
              <div class="pal-grid">
                <button
                  v-for="c in swatches(t.color)"
                  :key="c.v"
                  class="sw"
                  :class="{ on: c.current }"
                  :style="{ background: c.v }"
                  :title="c.v"
                  @click="pick(t.k, c.v)"
                ></button>
              </div>
              <button class="shuffle" @click="palShuffle">⟳ другие варианты</button>
            </div>
          </template>
        </span>
        <span class="lt-name-cell">{{ t.label }}</span>
        <div class="dur">
          <button class="mini" @click="rowDur(t, -1)">−</button>
          <span class="dur-val mono">{{ t.acHours }} ак.ч</span>
          <button class="mini" @click="rowDur(t, 1)">＋</button>
          <span class="min-label mono">{{ t.minLabel }}</span>
        </div>
        <span class="usage" :class="{ free: !t.used }">{{ t.usage }}</span>
        <button
          class="lt-del"
          :class="{ off: t.locked }"
          :title="t.locked ? 'Нельзя удалить: тип используется в темах' : 'Удалить тип занятия'"
          @click="delType(t)"
        >✕</button>
      </div>
    </div>

    <div class="lt-foot">
      Тип задаёт длительность (ак. часы) и цвет. Везде в приложении тип обозначается одинаково —
      круглым маркером цвета типа: в пуле, на сетке, в карточке занятия. При создании типа цвет
      предлагается автоматически; варианты можно перегенерировать.
    </div>
  </div>
</template>

<style scoped>
.lt { flex: 1; display: flex; flex-direction: column; min-height: 0; }
.micro { font: 500 10.5px var(--mono); letter-spacing: 0.07em; color: var(--muted); }
.hint { font-size: 11px; color: var(--faint); }

.lt-form {
  flex: none;
  padding: 12px 18px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.08);
  background: #FBFAF8;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.lt-form-head { display: flex; align-items: baseline; gap: 8px; flex-wrap: wrap; }
.lt-form-row { display: flex; gap: 8px; align-items: center; }
.lt-name { flex: 1; min-width: 0; font-size: 12.5px; padding: 7px 10px; }

.dur { flex: none; display: flex; align-items: center; gap: 6px; }
.dur-val { font: 500 12.5px var(--mono); min-width: 52px; text-align: center; }
.step { border: 1px solid var(--line-strong); background: var(--panel); width: 26px; height: 26px; border-radius: 6px; cursor: pointer; }
.mini { border: 1px solid var(--line-soft); background: var(--panel); width: 22px; height: 22px; border-radius: 5px; cursor: pointer; font-size: 11px; }
.min-label { font: 400 10px var(--mono); color: var(--faint); }

.add-btn { flex: none; border: none; background: var(--fg); color: #FFF; font: 500 12.5px var(--sans); padding: 8px 14px; border-radius: var(--r-md); cursor: pointer; }
.add-btn:hover { background: var(--fg-hover); }
.form-err { display: flex; gap: 7px; font-size: 12px; color: var(--red); }

.lt-table { flex: 1; overflow-y: auto; padding: 10px 18px 14px; }
.lt-thead, .lt-row {
  display: grid;
  grid-template-columns: 44px 1fr 200px 150px 30px;
  gap: 6px;
  align-items: center;
}
.lt-thead { padding: 4px 0; font: 500 10px var(--mono); letter-spacing: 0.06em; color: var(--faint); }
.lt-row { padding: 7px 0; border-top: 1px solid rgba(0, 0, 0, 0.06); }
.lt-name-cell { font-size: 12.5px; font-weight: 600; }
.usage { font-size: 11.5px; color: var(--sub); }
.usage.free { color: var(--faint); }
.lt-del { border: none; background: transparent; color: var(--red); font-size: 13px; cursor: pointer; padding: 2px 6px; justify-self: start; }
.lt-del.off { color: #C9C5BB; cursor: not-allowed; }

.pal-wrap { position: relative; display: inline-flex; }
.dot-btn { width: 26px; height: 26px; border-radius: 50%; border: 2px solid #FFF; box-shadow: 0 0 0 1px rgba(0, 0, 0, 0.18); cursor: pointer; }
.dot-btn.sm { width: 22px; height: 22px; }
.pal-backdrop { position: fixed; inset: 0; z-index: 45; }
.pal-pop {
  position: absolute;
  left: 0;
  top: 30px;
  z-index: 46;
  width: 196px;
  background: var(--panel);
  border: 1px solid rgba(0, 0, 0, 0.12);
  border-radius: 9px;
  box-shadow: 0 10px 28px rgba(0, 0, 0, 0.14);
  padding: 10px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.pal-grid { display: flex; flex-wrap: wrap; gap: 7px; }
.sw { width: 24px; height: 24px; border-radius: 50%; border: 2px solid #FFF; box-shadow: 0 0 0 1px rgba(0, 0, 0, 0.15); cursor: pointer; }
.sw.on { box-shadow: 0 0 0 2px var(--fg); }
.shuffle { align-self: flex-start; background: transparent; border: 1px dashed var(--line-strong); border-radius: 6px; padding: 5px 10px; font-size: 11px; color: var(--blue); cursor: pointer; }

.lt-foot { flex: none; padding: 11px 18px; border-top: 1px solid rgba(0, 0, 0, 0.08); font-size: 11px; color: var(--muted); line-height: 1.5; }
</style>
