import { describe, expect, it } from 'vitest'
import { deduplicateCitations, formatCitationLabel } from './citations'
import type { Citation } from '@/types/api'

describe('deduplicateCitations', () => {
  it('merges citations from the same document', () => {
    const citations: Citation[] = [
      { document_id: 1, chunk_id: 10, source: 'notes.pdf', page_number: 2 },
      { document_id: 1, chunk_id: 11, source: 'notes.pdf', page_number: 5 },
      { document_id: 2, chunk_id: 20, source: 'other.pdf' },
    ]
    const deduped = deduplicateCitations(citations)
    expect(deduped).toHaveLength(2)
    expect(deduped[0]).toMatchObject({
      documentId: 1,
      label: 'notes.pdf',
      chunkCount: 2,
      pageNumbers: [2, 5],
    })
    expect(formatCitationLabel(deduped[0])).toBe('notes.pdf · p.2, 5 · 2 chunks')
  })
})
