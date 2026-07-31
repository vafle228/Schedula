/**
 * Geometry for the tour spotlight.
 *
 * `main.css` sets `body { zoom: 1.15 }`, so two coordinate spaces coexist and
 * every number here has to be pinned to one of them:
 *
 * - `getBoundingClientRect()` and `window.innerWidth` report **device** pixels
 *   (the rail is 188px wide in CSS and measures 216.2 = 188 × 1.15).
 * - A `px` length written onto an element inside the zoomed body is a **CSS**
 *   pixel and renders 1.15× larger.
 *
 * Since the overlay lives in the zoomed body, everything it is given must be in
 * CSS pixels — so measurements are divided by the zoom on the way in. This is
 * the same correction `App.vue` (`calc(100vh / 1.15)`) and `ConfirmDialog.vue`
 * (`calc(92vw / 1.15)`) already make by hand.
 */

const FALLBACK_ZOOM = 1

/** Effective `zoom` applied to `<body>`, or 1 when unset/unsupported. */
export function zoomFactor() {
  const raw = getComputedStyle(document.body).zoom
  const n = parseFloat(raw)
  return Number.isFinite(n) && n > 0 ? n : FALLBACK_ZOOM
}

/** Viewport size in CSS pixels — the space the overlay is laid out in. */
export function viewportBox() {
  const z = zoomFactor()
  return { w: window.innerWidth / z, h: window.innerHeight / z }
}

/** `el`'s box converted from device pixels to CSS pixels. */
function cssRect(el) {
  const r = el.getBoundingClientRect()
  const z = zoomFactor()
  return {
    left: r.left / z,
    top: r.top / z,
    right: r.right / z,
    bottom: r.bottom / z,
    width: r.width / z,
    height: r.height / z,
  }
}

/**
 * Measure `el` for the spotlight, padded outwards and clamped to the viewport.
 * Returns `null` when the element is missing or has collapsed to nothing.
 */
export function measure(el, pad = 6) {
  if (!el) return null
  const r = cssRect(el)
  if (r.width < 1 || r.height < 1) return null
  const { w, h } = viewportBox()
  const left = Math.max(0, r.left - pad)
  const top = Math.max(0, r.top - pad)
  return {
    left,
    top,
    width: Math.min(r.right + pad, w) - left,
    height: Math.min(r.bottom + pad, h) - top,
  }
}

const CARD_GAP = 14

/**
 * Place the tooltip card around `rect`, preferring `placement` and falling back
 * to whichever side actually has room. With no rect the card is centred.
 */
export function placeCard(rect, card, placement = 'auto') {
  const { w, h } = viewportBox()
  if (!rect) {
    return { left: (w - card.w) / 2, top: (h - card.h) / 2, side: 'center' }
  }

  const room = {
    bottom: h - rect.top - rect.height,
    top: rect.top,
    right: w - rect.left - rect.width,
    left: rect.left,
  }
  const need = { bottom: card.h, top: card.h, right: card.w, left: card.w }
  const order =
    placement === 'auto'
      ? ['bottom', 'right', 'top', 'left']
      : [placement, 'bottom', 'right', 'top', 'left']

  const side =
    order.find((s) => room[s] >= need[s] + CARD_GAP) ||
    // nothing fits: use the roomiest side and let the clamp below handle it
    Object.keys(room).sort((a, b) => room[b] - room[a])[0]

  let left
  let top
  if (side === 'bottom' || side === 'top') {
    left = rect.left + rect.width / 2 - card.w / 2
    top = side === 'bottom' ? rect.top + rect.height + CARD_GAP : rect.top - card.h - CARD_GAP
  } else {
    left = side === 'right' ? rect.left + rect.width + CARD_GAP : rect.left - card.w - CARD_GAP
    top = rect.top + rect.height / 2 - card.h / 2
  }

  return {
    left: clamp(left, CARD_GAP, w - card.w - CARD_GAP),
    top: clamp(top, CARD_GAP, h - card.h - CARD_GAP),
    side,
  }
}

function clamp(v, lo, hi) {
  return Math.min(Math.max(v, lo), hi < lo ? lo : hi)
}

/** First selector in `list` that matches something with a real box. */
function findFirst(list) {
  for (const selector of list) {
    const el = document.querySelector(selector)
    if (el && el.getBoundingClientRect().width >= 1) return el
  }
  return null
}

/**
 * Resolve a step's target, retrying briefly because the element may still be
 * mounting after a route change. `target` may be a list of selectors, tried in
 * priority order — several views render their detail pane only once something
 * is selected, so a step wants "the card, or the whole panel if the workspace
 * is still empty". Resolves to `null` when nothing matches, and the caller then
 * shows a centred card rather than breaking the tour.
 *
 * Deliberately on `setTimeout` rather than `requestAnimationFrame`: browsers
 * (and the packaged pywebview window) pause rAF while unfocused or minimised,
 * which would leave the tour waiting forever on a step it could have resolved.
 */
export function waitForTarget(target, timeout = 600, interval = 50) {
  return new Promise((resolve) => {
    if (!target) return resolve(null)
    const list = Array.isArray(target) ? target : [target]
    const deadline = Date.now() + timeout
    const tick = () => {
      const el = findFirst(list)
      if (el) return resolve(el)
      if (Date.now() >= deadline) return resolve(null)
      setTimeout(tick, interval)
    }
    tick()
  })
}

/**
 * Scroll `el` into view if it sits outside the viewport.
 *
 * Jumps rather than smooth-scrolls on purpose: a smooth scroll emits a stream
 * of scroll events for half a second, and the spotlight would spend that time
 * chasing a target that is still moving.
 */
export function ensureVisible(el) {
  if (!el) return
  const r = cssRect(el)
  const { h } = viewportBox()
  if (r.top < 0 || r.bottom > h) {
    el.scrollIntoView({ block: 'center', behavior: 'auto' })
  }
}
