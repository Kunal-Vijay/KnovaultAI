import { apiRequest } from '@/lib/api-client'
import type { KnowledgeBase, KnowledgeBaseCreate } from '@/types/api'

export function listKnowledgeBases(userId: number) {
  return apiRequest<KnowledgeBase[]>(`/users/${userId}/knowledge_bases/`)
}

export function createKnowledgeBase(userId: number, body: KnowledgeBaseCreate) {
  return apiRequest<KnowledgeBase>(`/users/${userId}/knowledge_bases/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
}

export function getKnowledgeBase(userId: number, kbId: number) {
  return apiRequest<KnowledgeBase>(`/users/${userId}/knowledge_bases/${kbId}`)
}
