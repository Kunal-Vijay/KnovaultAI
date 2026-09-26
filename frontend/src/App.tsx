import { useEffect, useState } from 'react'
import { BrowserRouter, Navigate, Route, Routes, useNavigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from 'sonner'
import { ErrorBoundary } from '@/components/ErrorBoundary'
import { DebugDrawer, type DebugEntry } from '@/components/DebugDrawer'
import { AppLayout } from '@/components/layout/AppLayout'
import { AuthLayout } from '@/components/layout/AuthLayout'
import { ProtectedRoute } from '@/components/layout/ProtectedRoute'
import { LoginPage } from '@/features/auth/LoginPage'
import { RegisterPage } from '@/features/auth/RegisterPage'
import { CreateKnowledgeBasePage } from '@/features/knowledge-bases/CreateKnowledgeBasePage'
import { DashboardPage } from '@/features/knowledge-bases/DashboardPage'
import { KnowledgeBaseWorkspacePage } from '@/features/knowledge-bases/KnowledgeBaseWorkspacePage'
import { QueryHistoryDetailPage } from '@/features/history/QueryHistoryDetailPage'
import { AuthProvider, useAuth } from '@/hooks/useAuth'
import { setUnauthorizedHandler } from '@/lib/api-client'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: 1, staleTime: 30_000 },
  },
})

function UnauthorizedListener() {
  const navigate = useNavigate()
  const { logout } = useAuth()

  useEffect(() => {
    setUnauthorizedHandler(() => {
      logout()
      navigate('/login', { replace: true })
    })
  }, [logout, navigate])

  return null
}

function AppRoutes() {
  const { isAuthenticated, isLoading } = useAuth()

  return (
    <>
      <UnauthorizedListener />
      <Routes>
        <Route element={<AuthLayout />}>
          <Route
            path="/login"
            element={isLoading ? null : isAuthenticated ? <Navigate to="/" replace /> : <LoginPage />}
          />
          <Route
            path="/register"
            element={isLoading ? null : isAuthenticated ? <Navigate to="/" replace /> : <RegisterPage />}
          />
        </Route>

        <Route
          element={
            <ProtectedRoute>
              <AppLayout />
            </ProtectedRoute>
          }
        >
          <Route path="/" element={<DashboardPage />} />
          <Route path="/knowledge-bases/new" element={<CreateKnowledgeBasePage />} />
          <Route path="/knowledge-bases/:kbId" element={<KnowledgeBaseWorkspacePage />} />
          <Route path="/knowledge-bases/:kbId/history/:executionId" element={<QueryHistoryDetailPage />} />
        </Route>

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </>
  )
}

export default function App() {
  const [debugEntry, setDebugEntry] = useState<DebugEntry | null>(null)

  useEffect(() => {
    if (!import.meta.env.DEV) return
    const original = window.fetch
    window.fetch = async (...args) => {
      const start = performance.now()
      const response = await original(...args)
      const input = args[0]
      const url =
        typeof input === 'string'
          ? input
          : input instanceof URL
            ? input.href
            : input.url
      if (url.includes('/api/')) {
        setDebugEntry({
          url,
          status: response.status,
          durationMs: Math.round(performance.now() - start),
        })
      }
      return response
    }
    return () => {
      window.fetch = original
    }
  }, [])

  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <AuthProvider>
          <BrowserRouter>
            <AppRoutes />
            <Toaster richColors position="top-right" />
            <DebugDrawer lastRequest={debugEntry} />
          </BrowserRouter>
        </AuthProvider>
      </QueryClientProvider>
    </ErrorBoundary>
  )
}
