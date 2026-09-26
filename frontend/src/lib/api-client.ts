import { clearToken, getToken } from '@/lib/auth'
import type { ApiMeta, ApiResult } from '@/types/api'

const API_BASE = '/api/v1'

export class ApiError extends Error {
  status: number
  detail: string

  constructor(status: number, detail: string) {
    super(detail)
    this.status = status
    this.detail = detail
  }
}

type UnauthorizedHandler = () => void

let onUnauthorized: UnauthorizedHandler | null = null

export function setUnauthorizedHandler(handler: UnauthorizedHandler) {
  onUnauthorized = handler
}

async function parseError(response: Response): Promise<string> {
  try {
    const body = await response.json()
    if (typeof body.detail === 'string') return body.detail
    if (Array.isArray(body.detail)) {
      return body.detail.map((d: { msg?: string }) => d.msg ?? 'Error').join(', ')
    }
    return response.statusText || 'Request failed'
  } catch {
    return response.statusText || 'Request failed'
  }
}

function extractMeta(response: Response, start: number): ApiMeta {
  return {
    requestId: response.headers.get('x-request-id') ?? undefined,
    traceparent: response.headers.get('traceparent') ?? undefined,
    durationMs: Math.round(performance.now() - start),
  }
}

export async function apiRequest<T>(
  path: string,
  options: RequestInit & { auth?: boolean } = {},
): Promise<ApiResult<T>> {
  const { auth = true, ...init } = options
  const headers = new Headers(init.headers)

  if (auth) {
    const token = getToken()
    if (token) headers.set('Authorization', `Bearer ${token}`)
  }

  const start = performance.now()
  const response = await fetch(`${API_BASE}${path}`, { ...init, headers })
  const meta = extractMeta(response, start)

  if (response.status === 401 && auth) {
    clearToken()
    onUnauthorized?.()
    throw new ApiError(401, 'Session expired. Please log in again.')
  }

  if (!response.ok) {
    throw new ApiError(response.status, await parseError(response))
  }

  if (response.status === 204) {
    return { data: undefined as T, meta }
  }

  const data = (await response.json()) as T
  return { data, meta }
}

export async function login(username: string, password: string) {
  const body = new URLSearchParams({ username, password })
  return apiRequest<{ access_token: string; token_type: string }>('/token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: body.toString(),
    auth: false,
  })
}

export async function loginAsDemo() {
  return apiRequest<{ access_token: string; token_type: string }>('/auth/demo', {
    method: 'POST',
    auth: false,
  })
}
