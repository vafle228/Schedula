/**
 * Transport layer. Talks to the real backend under /api/v1 with the JSON
 * contract described in «API — Спецификация ендпоинтов».
 */
const BASE = '/api/v1'

/** Error carrying the HTTP status and the server's (Russian) message. */
export class ApiError extends Error {
  constructor(status, message) {
    super(message)
    this.status = status
  }
}

export async function request(method, path, body) {
  const res = await fetch(BASE + path, {
    method,
    headers: { 'Content-Type': 'application/json' },
    body: body !== undefined ? JSON.stringify(body) : undefined,
  })
  if (res.status === 204) return null
  const data = await res.json().catch(() => null)
  if (!res.ok) throw new ApiError(res.status, data && data.error ? data.error.message : res.statusText)
  return data
}

/** Fetch a binary endpoint and hand the user a Save-As dialog for it. */
export async function download(path, filename) {
  if (window.pywebview) {
    const fullUrl = 'http://127.0.0.1:8000' + BASE + path
    const result = await window.pywebview.api.initiate_download(fullUrl, filename || 'export.xlsx')
    if (result && result.status === 'error') throw new ApiError(0, result.message)
    return
  }

  const res = await fetch(BASE + path)
  if (!res.ok) {
    const data = await res.json().catch(() => null)
    throw new ApiError(res.status, data && data.error ? data.error.message : res.statusText)
  }
  const blob = await res.blob()
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename || 'export.xlsx'
  document.body.appendChild(a)
  a.click()
  a.remove()
  URL.revokeObjectURL(url)
}
