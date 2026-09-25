import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react'
import { apiRequest } from '@/lib/api-client'
import {
  clearToken,
  decodeJwt,
  getToken,
  isTokenExpired,
  setToken,
} from '@/lib/auth'
import type { User } from '@/types/api'

interface AuthContextValue {
  user: User | null
  isLoading: boolean
  isAuthenticated: boolean
  loginWithToken: (token: string) => Promise<void>
  logout: () => void
  refreshUser: () => Promise<void>
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  const refreshUser = useCallback(async () => {
    const token = getToken()
    if (!token || isTokenExpired(token)) {
      clearToken()
      setUser(null)
      return
    }
    const { data } = await apiRequest<User>('/users/me')
    setUser(data)
  }, [])

  const loginWithToken = useCallback(
    async (token: string) => {
      setToken(token)
      await refreshUser()
    },
    [refreshUser],
  )

  const logout = useCallback(() => {
    clearToken()
    setUser(null)
  }, [])

  useEffect(() => {
    const token = getToken()
    if (!token || isTokenExpired(token)) {
      clearToken()
      setIsLoading(false)
      return
    }
    const payload = decodeJwt(token)
    if (!payload?.user_id) {
      clearToken()
      setIsLoading(false)
      return
    }
    refreshUser()
      .catch(() => {
        clearToken()
        setUser(null)
      })
      .finally(() => setIsLoading(false))
  }, [refreshUser])

  const value = useMemo(
    () => ({
      user,
      isLoading,
      isAuthenticated: !!user,
      loginWithToken,
      logout,
      refreshUser,
    }),
    [user, isLoading, loginWithToken, logout, refreshUser],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
