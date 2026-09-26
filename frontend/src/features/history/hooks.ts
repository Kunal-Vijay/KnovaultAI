import { useQuery } from '@tanstack/react-query'
import { getQueryDetail, getQueryTrace, listQueries } from './api'
import { useAuth } from '@/hooks/useAuth'

export function useQueryHistory(kbId: number, limit = 20) {
  const { user } = useAuth()
  return useQuery({
    queryKey: ['query-history', user?.id, kbId, limit],
    queryFn: async () => {
      if (!user) throw new Error('Not authenticated')
      const { data } = await listQueries(user.id, kbId, limit, 0)
      return data
    },
    enabled: !!user && kbId > 0,
  })
}

export function useQueryDetail(kbId: number, executionId: string | undefined) {
  const { user } = useAuth()
  return useQuery({
    queryKey: ['query-detail', user?.id, kbId, executionId],
    queryFn: async () => {
      if (!user || !executionId) throw new Error('Missing context')
      const { data } = await getQueryDetail(user.id, kbId, executionId)
      return data
    },
    enabled: !!user && kbId > 0 && !!executionId,
  })
}

export function useQueryTrace(kbId: number, executionId: string | undefined) {
  const { user } = useAuth()
  return useQuery({
    queryKey: ['query-trace', user?.id, kbId, executionId],
    queryFn: async () => {
      if (!user || !executionId) throw new Error('Missing context')
      const { data } = await getQueryTrace(user.id, kbId, executionId)
      return data
    },
    enabled: !!user && kbId > 0 && !!executionId,
  })
}
