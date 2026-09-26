import type { Citation, TokenUsage } from '@/types/api'

export type { TokenUsage }

export interface QueryExecutionListItem {
  execution_id: string
  question: string
  status: string
  routed_model?: string | null
  total_tokens?: number | null
  estimated_cost_usd?: number | null
  latency_ms?: number | null
  created_at: string
}

export interface PaginatedQueryExecutions {
  items: QueryExecutionListItem[]
  limit: number
  offset: number
  total: number
  has_more: boolean
}

export interface QueryExecutionDetail {
  execution_id: string
  knowledge_base_id: number
  question: string
  answer?: string | null
  status: string
  routed_model?: string | null
  routing_policy?: string | null
  routing_reason?: string | null
  usage?: TokenUsage | null
  estimated_cost_usd?: number | null
  latency_ms?: number | null
  chunks_retrieved?: number | null
  citations: Citation[]
  request_id?: string | null
  otel_trace_id?: string | null
  error_message?: string | null
  created_at: string
}

export interface SpanView {
  span_id: string
  parent_span_id?: string | null
  name: string
  status: string
  started_at: string
  ended_at?: string | null
  latency_ms?: number | null
  model?: string | null
  tokens?: Record<string, unknown> | null
  attributes?: Record<string, unknown>
  input_preview?: string | null
  output_preview?: string | null
  error_message?: string | null
}

export interface SpanTreeNode extends SpanView {
  children: SpanTreeNode[]
  depth: number
}

export interface ExecutionTraceView {
  execution_id: string
  started_at: string
  completed_at?: string | null
  total_latency_ms?: number | null
  spans: SpanView[]
}
