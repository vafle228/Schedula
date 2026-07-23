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
