import { apiRequest } from '@/lib/api-client'
import type { ExecutionTraceView, PaginatedQueryExecutions, QueryExecutionDetail } from '@/types/history'

export function listQueries(userId: number, kbId: number, limit = 20, offset = 0) {
  return apiRequest<PaginatedQueryExecutions>(
    `/users/${userId}/knowledge_bases/${kbId}/queries?limit=${limit}&offset=${offset}`,
  )
}

export function getQueryDetail(userId: number, kbId: number, executionId: string) {
  return apiRequest<QueryExecutionDetail>(
    `/users/${userId}/knowledge_bases/${kbId}/queries/${executionId}`,
  )
}

export function getQueryTrace(userId: number, kbId: number, executionId: string) {
  return apiRequest<ExecutionTraceView>(
    `/users/${userId}/knowledge_bases/${kbId}/queries/${executionId}/trace`,
  )
}
