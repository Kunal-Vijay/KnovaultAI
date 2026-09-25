import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { createKnowledgeBase, getKnowledgeBase, listKnowledgeBases } from './api'
import { useAuth } from '@/hooks/useAuth'
import type { KnowledgeBaseCreate } from '@/types/api'

export function useKnowledgeBases() {
  const { user } = useAuth()
  return useQuery({
    queryKey: ['knowledge-bases', user?.id],
    queryFn: async () => {
      if (!user) throw new Error('Not authenticated')
      const { data } = await listKnowledgeBases(user.id)
      return data
    },
    enabled: !!user,
  })
}

export function useKnowledgeBase(kbId: number) {
  const { user } = useAuth()
  return useQuery({
    queryKey: ['knowledge-base', user?.id, kbId],
    queryFn: async () => {
      if (!user) throw new Error('Not authenticated')
      const { data } = await getKnowledgeBase(user.id, kbId)
      return data
    },
    enabled: !!user && kbId > 0,
  })
}

export function useCreateKnowledgeBase() {
  const { user } = useAuth()
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (body: KnowledgeBaseCreate) => {
      if (!user) throw new Error('Not authenticated')
      const { data } = await createKnowledgeBase(user.id, body)
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['knowledge-bases', user?.id] })
    },
  })
}
