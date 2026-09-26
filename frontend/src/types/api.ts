export interface User {
  id: number
  username: string
  email: string
  is_active: boolean
  created_at: string
}

export interface UserCreate {
  username: string
  email: string
  password: string
}

export interface Token {
  access_token: string
  token_type: string
}

export interface KnowledgeBase {
  id: number
  name: string
  description?: string | null
  owner_id: number
  created_at: string
}

export interface KnowledgeBaseCreate {
  name: string
  description?: string | null
}

export interface Document {
  id: number
  filename: string
  external_storage_ref: string
  knowledge_base_id: number
  status: string
  mime_type?: string | null
  num_pages?: number | null
  raw_content_size?: number | null
  content_sha256?: string | null
  embedding_model?: string | null
  chunk_count?: number
  error_message?: string | null
  created_at: string
}

export interface DocumentChunk {
  id: number
  document_id: number
  content: string
  source?: string | null
  page_number?: number | null
  section?: string | null
  created_at: string
}

export interface SearchRequest {
  knowledge_base_id: number
  query: string
  keyword_query?: string | null
  top_k?: number
  rrf_k?: number
}

export interface SearchResultItem {
  chunk: DocumentChunk
  score: number
}

export interface SearchResponse {
  results: SearchResultItem[]
}

export interface RAGRequest {
  knowledge_base_id: number
  question: string
  top_k?: number
}

export interface Citation {
  document_id: number
  chunk_id: number
  source?: string | null
  page_number?: number | null
  section?: string | null
}

export interface TokenUsage {
  prompt_tokens?: number | null
  completion_tokens?: number | null
  total_tokens?: number | null
}

export interface RAGResponse {
  answer: string
  citations: Citation[]
  execution_id?: string | null
  routed_model?: string | null
  routing_policy?: string | null
  routing_reason?: string | null
  usage?: TokenUsage | null
  estimated_cost_usd?: number | null
  latency_ms?: number | null
}

export interface ApiMeta {
  requestId?: string
  traceparent?: string
  durationMs: number
}

export interface ApiResult<T> {
  data: T
  meta: ApiMeta
}
