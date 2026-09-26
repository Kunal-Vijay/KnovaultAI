import { describe, expect, it } from 'vitest'
import { layoutSpanForest } from '@/features/history/trace/graph-layout'
import { buildSpanForest, spanKey } from '@/features/history/trace/trace-tree'
import type { SpanView } from '@/types/history'

function span(
  id: string,
  name: string,
  parent: string | null = null,
): SpanView {
  return {
    span_id: id,
    parent_span_id: parent,
    name,
    status: 'completed',
    started_at: '2026-01-01T00:00:00Z',
    ended_at: '2026-01-01T00:00:01Z',
    latency_ms: 1000,
  }
}

describe('buildSpanForest', () => {
  it('builds RAG-shaped tree with root and two children', () => {
    const spans = [
      span('root', 'rag_service.get_answer'),
      span('search', 'hybrid_search_service.search', 'root'),
      span('llm', 'llm_gateway.generate_response', 'root'),
    ]
    const forest = buildSpanForest(spans)
    expect(forest).toHaveLength(1)
    expect(forest[0].name).toBe('rag_service.get_answer')
    expect(forest[0].children).toHaveLength(2)
    expect(forest[0].children.map((c) => c.name).sort()).toEqual([
      'hybrid_search_service.search',
      'llm_gateway.generate_response',
    ])
  })

  it('layout assigns distinct positions to siblings', () => {
    const spans = [
      span('root', 'rag_service.get_answer'),
      span('search', 'hybrid_search_service.search', 'root'),
      span('llm', 'llm_gateway.generate_response', 'root'),
    ]
    const forest = buildSpanForest(spans)
    const positions = layoutSpanForest(forest)
    const searchPos = positions.get('search')
    const llmPos = positions.get('llm')
    expect(searchPos).toBeDefined()
    expect(llmPos).toBeDefined()
    expect(searchPos!.x).not.toBe(llmPos!.x)
    expect(spanKey(forest[0])).toBe('root')
  })
})
