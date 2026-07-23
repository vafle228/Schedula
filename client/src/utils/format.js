/** «Фамилия И. О.» → «ФИ» — initials for avatar placeholders. */
export function initials(name) {
  const p = (name || '').trim().split(/\s+/)
  return (p[0] ? p[0][0] : '') + (p[1] ? p[1][0] : '')
}

/** Russian plural picker: plural(3, 'пара', 'пары', 'пар'). */
export function plural(n, one, few, many) {
  const a = n % 10
  const b = n % 100
  if (a === 1 && b !== 11) return one
  if (a >= 2 && a <= 4 && (b < 12 || b > 14)) return few
  return many
}

export function avatarBg(photo) {
  return photo ? `center/cover no-repeat url("${photo}")` : '#ECEAE4'
}
