<script setup>
/* Guided-tour overlay: a dimming curtain with a cut-out around the current
   step's element, plus a tooltip card next to it. Mounted once in App.vue.

   The cut-out is a single div carrying `box-shadow: 0 0 0 9999px <dim>`, so the
   dim layer and the hole are the same element and always stay in sync. Geometry
   lives in onboarding/anchor.js — see its header for the `body { zoom }` note. */
import { computed, onBeforeUnmount, ref, watch, nextTick } from 'vue'
import { useOnboarding } from '../composables/useOnboarding.js'
import { measure, placeCard, viewportBox } from '../onboarding/anchor.js'

const CARD_W = 340
const CARD_H_GUESS = 210

const ob = useOnboarding()
const state = ob.state

const rect = ref(null)
const cardEl = ref(null)
const cardPos = ref({ left: 0, top: 0, side: 'center' })

const step = computed(() => ob.stepAt(state.index))
const total = computed(() => ob.steps.length)
const isLast = computed(() => state.index >= total.value - 1)
const viewport = ref(viewportBox())

/* Re-measure the target and re-place the card. While the next step is still
   settling the previous cut-out is held, so navigation does not flash the whole
   screen dim. */
async function reposition() {
  viewport.value = viewportBox()
  if (state.settling) return
  rect.value = measure(state.target)
  await nextTick()
  const h = cardEl.value ? cardEl.value.offsetHeight : CARD_H_GUESS
  cardPos.value = placeCard(rect.value, { w: CARD_W, h }, step.value?.placement || 'auto')
}

/* The scroll listener is capture-phase, so it fires for every scrollable
   element on the page; coalesce so a flick of the wheel cannot thrash layout. */
let queued = false
function repositionSoon() {
  if (queued) return
  queued = true
  setTimeout(() => {
    queued = false
    reposition()
  }, 16)
}

/* The composable resolves the target after the step's `before()` hook has run;
   a step whose target never appears resolves to null and shows a centred card
   over a plain dim rather than stalling the tour. */
watch(
  () => [state.active, state.target, state.settling],
  () => {
    if (state.active) reposition()
  },
  { immediate: true },
)

function onKey(e) {
  if (e.key === 'Escape') return ob.skipTour()
  if (e.key === 'ArrowRight' || e.key === 'Enter') { e.preventDefault(); ob.next() }
  if (e.key === 'ArrowLeft') { e.preventDefault(); ob.back() }
}

function listen(on) {
  const fn = on ? window.addEventListener : window.removeEventListener
  fn('keydown', onKey, true)
  fn('resize', repositionSoon)
  fn('scroll', repositionSoon, true)
}

watch(() => state.active, (on) => listen(on), { immediate: true })
onBeforeUnmount(() => listen(false))
</script>

<template>
  <div v-if="state.active && step" class="ob-root">
    <!-- swallows clicks so the tour drives navigation, not the page underneath -->
    <div
      class="ob-block"
      :style="{ width: viewport.w + 'px', height: viewport.h + 'px' }"
      @click="ob.next()"
    ></div>

    <div
      v-if="rect"
      class="ob-spot"
      :style="{
        left: rect.left + 'px',
        top: rect.top + 'px',
        width: rect.width + 'px',
        height: rect.height + 'px',
      }"
    ></div>
    <!-- no target resolved: dim the whole screen instead of cutting a hole -->
    <div
      v-else
      class="ob-veil"
      :style="{ width: viewport.w + 'px', height: viewport.h + 'px' }"
    ></div>

    <div
      ref="cardEl"
      class="ob-card"
      :style="{ left: cardPos.left + 'px', top: cardPos.top + 'px', width: CARD_W + 'px' }"
      @click.stop
    >
      <div class="ob-card-head">
        <span class="micro">{{ step.chapter }}</span>
        <span class="sp"></span>
        <span class="x-close" title="Завершить обучение (Esc)" @click="ob.skipTour()">×</span>
      </div>

      <div class="ob-title">{{ step.title }}</div>
      <div class="ob-text">{{ step.text }}</div>

      <div class="ob-dots">
        <button
          v-for="(s, i) in ob.steps"
          :key="s.id"
          class="ob-dot"
          :class="{ on: i === state.index, seen: i < state.index }"
          :title="s.title"
          @click="ob.goToStep(i)"
        ></button>
      </div>

      <div class="ob-foot">
        <span class="ob-count mono">{{ state.index + 1 }} / {{ total }}</span>
        <span class="sp"></span>
        <button v-if="state.index > 0" class="btn" @click="ob.back()">Назад</button>
        <button class="btn-primary" @click="isLast ? ob.finish() : ob.next()">
          {{ isLast ? 'Готово' : 'Далее' }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Above ConfirmDialog (80) so the tour is never buried by a dialog. */
.ob-root { position: fixed; inset: 0; z-index: 90; pointer-events: none; }

.ob-block { position: fixed; left: 0; top: 0; pointer-events: auto; }

.ob-spot {
  position: fixed;
  border-radius: var(--r-xl);
  box-shadow: 0 0 0 9999px rgba(31, 30, 27, 0.55);
  outline: 2px solid rgba(255, 255, 255, 0.75);
  outline-offset: -1px;
  pointer-events: none;
  transition: left 0.22s ease, top 0.22s ease, width 0.22s ease, height 0.22s ease;
}
.ob-veil {
  position: fixed;
  left: 0;
  top: 0;
  background: rgba(31, 30, 27, 0.55);
  pointer-events: none;
}

@keyframes obIn {
  from { opacity: 0; transform: translateY(6px); }
  to { opacity: 1; transform: none; }
}
.ob-card {
  position: fixed;
  background: var(--panel);
  border-radius: var(--r-2xl);
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.3);
  padding: 14px 16px 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  pointer-events: auto;
  animation: obIn 0.16s ease-out;
  transition: left 0.22s ease, top 0.22s ease;
}
.ob-card-head { display: flex; align-items: center; gap: 8px; }
.sp { flex: 1; }

.ob-title { font-size: 14px; font-weight: 600; line-height: 1.3; }
.ob-text { font-size: 12px; line-height: 1.55; color: var(--sub); }

.ob-dots { display: flex; flex-wrap: wrap; gap: 4px; padding: 2px 0; }
.ob-dot {
  width: 6px;
  height: 6px;
  padding: 0;
  border: none;
  border-radius: 50%;
  background: var(--ghost);
  cursor: pointer;
}
.ob-dot.seen { background: var(--dim); }
.ob-dot.on { background: var(--fg); width: 16px; border-radius: 3px; }

.ob-foot { display: flex; align-items: center; gap: 8px; padding-top: 2px; }
.ob-count { font-size: 10.5px; color: var(--faint); letter-spacing: 0.06em; }
</style>
