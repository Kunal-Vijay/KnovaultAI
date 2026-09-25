import { apiRequest } from '@/lib/api-client'
import type { RAGRequest, RAGResponse } from '@/types/api'

export function askRag(userId: number, body: RAGRequest) {
  return apiRequest<RAGResponse>(`/rag?user_id=${userId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
}
