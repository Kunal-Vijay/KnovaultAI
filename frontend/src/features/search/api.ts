import { apiRequest } from '@/lib/api-client'
import type { SearchRequest, SearchResponse } from '@/types/api'

export function searchKnowledge(userId: number, body: SearchRequest) {
  return apiRequest<SearchResponse>(`/search?user_id=${userId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
}
