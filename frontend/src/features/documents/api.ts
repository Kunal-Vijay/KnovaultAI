import { apiRequest } from '@/lib/api-client'
import type { Document } from '@/types/api'

export function listDocuments(userId: number, kbId: number) {
  return apiRequest<Document[]>(`/users/${userId}/knowledge_bases/${kbId}/documents/`)
}

export async function uploadDocument(userId: number, kbId: number, file: File) {
  const form = new FormData()
  form.append('file', file)
  const token = localStorage.getItem('access_token')
  const start = performance.now()
  const response = await fetch(`/api/v1/users/${userId}/knowledge_bases/${kbId}/documents/upload`, {
    method: 'POST',
    headers: token ? { Authorization: `Bearer ${token}` } : {},
    body: form,
  })
  const meta = {
    requestId: response.headers.get('x-request-id') ?? undefined,
    traceparent: response.headers.get('traceparent') ?? undefined,
    durationMs: Math.round(performance.now() - start),
  }
  if (!response.ok) {
    const text = await response.text()
    throw new Error(text || 'Upload failed')
  }
  const data = (await response.json()) as Document
  return { data, meta }
}

export const TERMINAL_DOCUMENT_STATUSES = new Set(['completed', 'failed'])
