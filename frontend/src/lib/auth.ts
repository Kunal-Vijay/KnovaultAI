const TOKEN_KEY = 'access_token'

export interface JwtPayload {
  sub?: string
  user_id?: number
  can_upload?: boolean
  exp?: number
}

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY)
}

export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token)
}

export function clearToken(): void {
  localStorage.removeItem(TOKEN_KEY)
}

export function decodeJwt(token: string): JwtPayload | null {
  try {
    const base64Url = token.split('.')[1]
    if (!base64Url) return null
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/')
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join(''),
    )
    return JSON.parse(jsonPayload) as JwtPayload
  } catch {
    return null
  }
}

export function isTokenExpired(token: string): boolean {
  const payload = decodeJwt(token)
  if (!payload?.exp) return false
  return Date.now() >= payload.exp * 1000
}

export function getUserIdFromToken(): number | null {
  const token = getToken()
  if (!token) return null
  const payload = decodeJwt(token)
  return payload?.user_id ?? null
}

export function canUploadFromToken(token?: string | null): boolean {
  const t = token ?? getToken()
  if (!t) return true
  const payload = decodeJwt(t)
  if (!payload || payload.can_upload === undefined) return true
  return payload.can_upload
}
