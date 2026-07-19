/**
 * Transport layer. While the backend is not up, every request is served by
 * the in-memory mock (same routes and payloads as the real API). To go live,
 * set USE_MOCK to false — the fetch branch talks to /api/v1 with the exact
 * same interface.
 */
import { mockRequest, ApiError } from './mock/server.js'

const USE_MOCK = true
const BASE = '/api/v1'

export { ApiError }

export async function request(method, path, body) {
  if (USE_MOCK) {
    // keep the async contract of a real transport
    return Promise.resolve().then(() => mockRequest(method, path, body))
  }
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
