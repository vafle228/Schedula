/**
 * Colour helpers for lesson-type markers (Итерация 6.5 / Справочники v2).
 * Palettes are pre-generated at one fixed saturation/lightness so the hues
 * read as siblings — only the tone differs. Colours are emitted as hex so the
 * tint/darken helpers in utils/kinds.js can derive card fills from them.
 */

/** Fixed saturation / lightness — medium-dark, matches the existing palette. */
const SAT = 46
const LIGHT = 42

export function hslToHex(h, s, l) {
  s /= 100
  l /= 100
  const k = (n) => (n + h / 30) % 12
  const a = s * Math.min(l, 1 - l)
  const f = (n) => {
    const c = l - a * Math.max(-1, Math.min(k(n) - 3, Math.min(9 - k(n), 1)))
    return Math.round(255 * c).toString(16).padStart(2, '0')
  }
  return ('#' + f(0) + f(8) + f(4)).toUpperCase()
}

/** One random colour at the shared saturation/lightness. */
export function randomColor() {
  return hslToHex(Math.floor(Math.random() * 360), SAT, LIGHT)
}

/** Eight evenly-spread hues (with a little jitter) — the picker's swatch row. */
export function randomPalette(n = 8) {
  const base = Math.random() * 360
  return Array.from({ length: n }, (_, i) => {
    const hue = Math.round((base + (i * 360) / n + (Math.random() * 24 - 12) + 360) % 360)
    return hslToHex(hue, SAT, LIGHT)
  })
}

/** Suggest a colour for a new type, biased away from hues already in use. */
export function suggestColor(usedHex = []) {
  const usedHues = usedHex.map(hexHue).filter((h) => h != null)
  let best = randomColor()
  let bestGap = -1
  for (let i = 0; i < 12; i++) {
    const hue = Math.floor(Math.random() * 360)
    const gap = usedHues.length
      ? Math.min(...usedHues.map((u) => hueDist(hue, u)))
      : 360
    if (gap > bestGap) { bestGap = gap; best = hslToHex(hue, SAT, LIGHT) }
  }
  return best
}

function hexHue(hex) {
  const m = /^#?([0-9a-f]{6})$/i.exec(hex || '')
  if (!m) return null
  const n = parseInt(m[1], 16)
  const r = ((n >> 16) & 255) / 255
  const g = ((n >> 8) & 255) / 255
  const b = (n & 255) / 255
  const max = Math.max(r, g, b)
  const min = Math.min(r, g, b)
  const d = max - min
  if (!d) return 0
  let h
  if (max === r) h = ((g - b) / d) % 6
  else if (max === g) h = (b - r) / d + 2
  else h = (r - g) / d + 4
  return (h * 60 + 360) % 360
}

function hueDist(a, b) {
  const d = Math.abs(a - b) % 360
  return d > 180 ? 360 - d : d
}
