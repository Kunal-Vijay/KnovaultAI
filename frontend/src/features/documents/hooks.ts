import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { listDocuments, TERMINAL_DOCUMENT_STATUSES, INGESTION_PENDING_STATUSES, uploadDocument } from './api'
import { useAuth } from '@/hooks/useAuth'

export function useDocuments(kbId: number) {
  const { user } = useAuth()
  return useQuery({
    queryKey: ['documents', user?.id, kbId],
    queryFn: async () => {
      if (!user) throw new Error('Not authenticated')
      const { data } = await listDocuments(user.id, kbId)
      return data
    },
    enabled: !!user && kbId > 0,
    refetchInterval: (query) => {
      const docs = query.state.data
      if (!docs?.length) return false
      const hasPending = docs.some(
        (d) =>
          INGESTION_PENDING_STATUSES.has(d.status) ||
          !TERMINAL_DOCUMENT_STATUSES.has(d.status),
      )
      return hasPending ? 3000 : false
    },
  })
}

export function useUploadDocument(kbId: number) {
  const { user } = useAuth()
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (file: File) => {
      if (!user) throw new Error('Not authenticated')
      const { data } = await uploadDocument(user.id, kbId, file)
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents', user?.id, kbId] })
    },
  })
}
