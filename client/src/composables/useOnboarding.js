/**
 * Single global onboarding instance — the welcome screen and the guided tour.
 *
 * Mirrors `useConfirm.js`: module-scoped reactive state plus imperative
 * functions, with the two overlays mounted once in `App.vue`. Progress lives on
 * the server (`/api/v1/onboarding`), so it survives restarts and the tour
 * resumes where it was left.
 *
 * Nothing here writes user data except `chooseClean()`, which the backend
 * refuses unless the database is still the untouched demo dataset.
 */
import { reactive, nextTick } from 'vue'
import { api } from '../api/index.js'
import { store } from '../store/index.js'
import { router } from '../router.js'
import { confirmDelete } from './useConfirm.js'
import { STEPS } from '../onboarding/steps.js'
import { ensureVisible, waitForTarget } from '../onboarding/anchor.js'

const SAVE_DEBOUNCE_MS = 300

const state = reactive({
  status: 'pending',
  canStartClean: false,
  dataChoice: null,
  /* welcome screen */
  welcome: false,
  busy: false,
  error: '',
  /* tour */
  active: false,
  index: 0,
  target: null, // resolved element for the current step
  settling: false, // between steps: hold the last spotlight instead of flashing
  seen: [],
})

/** Steps whose UI can actually render right now. */
function liveSteps() {
  return STEPS.filter((s) => !s.available || s.available())
}

let steps = STEPS

const stepAt = (i) => steps[i] || null

/* ---------- persistence ---------- */

let saveTimer = null

function saveSoon(patch) {
  clearTimeout(saveTimer)
  saveTimer = setTimeout(() => {
    api.patchOnboarding(patch).catch(() => {
      /* progress is a convenience, not data — a failed write must not break the tour */
    })
  }, SAVE_DEBOUNCE_MS)
}

async function saveNow(patch) {
  clearTimeout(saveTimer)
  try {
    const fresh = await api.patchOnboarding(patch)
    applyServer(fresh)
  } catch {
    /* ignore — see saveSoon */
  }
}

function applyServer(data) {
  if (!data) return
  state.status = data.status
  state.dataChoice = data.dataChoice
  state.seen = data.completedSteps || []
  if (typeof data.canStartClean === 'boolean') state.canStartClean = data.canStartClean
}

/* ---------- lifecycle ---------- */

/**
 * Load the stored state before the app mounts, so the welcome screen is
 * already decided on first paint instead of flashing in afterwards.
 */
export async function initOnboarding() {
  try {
    applyServer(await api.getOnboarding())
  } catch {
    // Backend unreachable: stay quiet rather than blocking the app on a tour.
    state.status = 'skipped'
  }
  if (state.status === 'pending') state.welcome = true
}

/* ---------- welcome choices ---------- */

export async function chooseDemo() {
  state.welcome = false
  await saveNow({ dataChoice: 'demo', status: 'in_progress' })
  runTour(0)
}

export async function chooseClean() {
  const ok = await confirmDelete({
    title: 'Начать с чистого листа?',
    message:
      'Демонстрационные данные будут удалены: учебные годы, специальности, группы, ' +
      'преподаватели, аудитории, дисциплины и занятия. Будет создан пустой активный ' +
      'учебный год. Типы занятий сохранятся.',
    confirmLabel: 'Удалить демо-данные',
  })
  if (!ok) return

  state.busy = true
  state.error = ''
  try {
    const res = await api.startCleanWorkspace()
    applyServer(res.onboarding)
    await store.reloadAll()
    state.welcome = false
    runTour(0)
  } catch (e) {
    state.error = e.message || 'Не удалось очистить данные'
  } finally {
    state.busy = false
  }
}

export async function skipWelcome() {
  state.welcome = false
  await saveNow({ status: 'skipped' })
}

/* ---------- tour ---------- */

/** Restart the tour from the beginning; never touches user data. */
export async function startTour() {
  state.welcome = false
  state.error = ''
  try {
    applyServer(await api.restartOnboarding())
  } catch {
    /* ignore — the tour still runs, just without persisted progress */
  }
  runTour(0)
}

/** Resume where the user left off; falls back to the start if that step is gone. */
export function resumeTour() {
  steps = liveSteps()
  const at = steps.findIndex((s) => !state.seen.includes(s.id))
  state.welcome = false
  runTour(at < 0 ? 0 : at)
}

/**
 * What the sidebar «Обучение» button does.
 *
 * A tour interrupted by closing the app picks up where it stopped; anything
 * else — finished, skipped, never started — replays from the beginning, which
 * is the point of keeping it re-runnable.
 */
export function openTour() {
  if (state.status === 'in_progress' && state.seen.length > 0) return resumeTour()
  return startTour()
}

function runTour(index) {
  steps = liveSteps()
  state.active = true
  state.index = 0
  goTo(index)
}

export function next() {
  if (state.index >= steps.length - 1) return finish()
  goTo(state.index + 1)
}

export function back() {
  if (state.index > 0) goTo(state.index - 1)
}

export function goToStep(i) {
  if (i >= 0 && i < steps.length) goTo(i)
}

export async function finish() {
  closeTour()
  await saveNow({ status: 'completed', currentStep: '' })
}

export async function skipTour() {
  closeTour()
  await saveNow({ status: 'skipped' })
}

function closeTour() {
  state.active = false
  state.target = null
}

let navToken = 0

/**
 * Move to step `i`: navigate if it lives elsewhere, let the step prepare the
 * view, and only then resolve the element to spotlight.
 *
 * Resolution has to happen *here*, after `before()`. Doing it in the overlay
 * (which reacts to the step index) resolved selectors against the outgoing
 * view — «Справочники» renders `.panel.card` on more than one tab, so the tour
 * latched onto the previous tab's card and then lost it when the tab switched.
 * `navToken` drops a stale resolution if the user has already moved on.
 */
async function goTo(i) {
  const step = stepAt(i)
  if (!step) return
  const token = ++navToken
  state.index = i
  state.settling = true

  if (step.route && router.currentRoute.value.path !== step.route) {
    await router.push(step.route)
  }
  if (step.before) await step.before()
  await nextTick()

  const el = await waitForTarget(step.target)
  if (token !== navToken) return
  ensureVisible(el)
  state.target = el
  state.settling = false

  if (!state.seen.includes(step.id)) state.seen.push(step.id)
  saveSoon({
    status: 'in_progress',
    currentStep: step.id,
    completedSteps: [...state.seen],
  })
}

export function useOnboarding() {
  return {
    state,
    get steps() {
      return steps
    },
    stepAt,
    next,
    back,
    goToStep,
    finish,
    skipTour,
    startTour,
    resumeTour,
    openTour,
    chooseDemo,
    chooseClean,
    skipWelcome,
  }
}
