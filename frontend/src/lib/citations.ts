import type { Citation } from '@/types/api'

export interface DeduplicatedCitation {
  documentId: number
  label: string
  chunkCount: number
  pageNumbers: number[]
}

/** One entry per document, preserving first-seen order from retrieval. */
export function deduplicateCitations(citations: Citation[]): DeduplicatedCitation[] {
  const byDocument = new Map<
    number,
    { label: string; count: number; pages: Set<number> }
  >()
  const order: number[] = []

  for (const c of citations) {
    let entry = byDocument.get(c.document_id)
    if (!entry) {
      entry = {
        label: c.source ?? `doc ${c.document_id}`,
        count: 0,
        pages: new Set(),
      }
      byDocument.set(c.document_id, entry)
      order.push(c.document_id)
    }
    entry.count += 1
    if (c.page_number != null) {
      entry.pages.add(c.page_number)
    }
  }

  return order.map((documentId) => {
    const entry = byDocument.get(documentId)!
    return {
      documentId,
      label: entry.label,
      chunkCount: entry.count,
      pageNumbers: [...entry.pages].sort((a, b) => a - b),
    }
  })
}

export function formatCitationLabel(d: DeduplicatedCitation): string {
  let text = d.label
  if (d.pageNumbers.length === 1) {
    text += ` · p.${d.pageNumbers[0]}`
  } else if (d.pageNumbers.length > 1) {
    text += ` · p.${d.pageNumbers.join(', ')}`
  }
  if (d.chunkCount > 1) {
    text += ` · ${d.chunkCount} chunks`
  }
  return text
}
