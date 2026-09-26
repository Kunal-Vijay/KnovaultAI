/** Match model citations like [Chunk 3] or [Chunk 3, Chunk 7] (not full context headers). */
const CHUNK_GROUP_RE = /\[(?:Chunk\s+\d+(?:,\s*Chunk\s+\d+)*)\]/gi
const CHUNK_NUM_RE = /Chunk\s+(\d+)/gi

/**
 * Turn [Chunk N] groups into markdown links #chunk-N so RagAnswerMarkdown can render badges.
 */
export function linkifyChunkReferences(text: string): string {
  return text.replace(CHUNK_GROUP_RE, (group) => {
    const inner = group.slice(1, -1)
    const nums = [...inner.matchAll(new RegExp(CHUNK_NUM_RE.source, 'gi'))].map((m) => m[1])
    if (nums.length === 0) return group
    return nums.map((n) => `[Chunk ${n}](#chunk-${n})`).join(' ')
  })
}

export function chunkIndexFromHref(href: string | undefined): number | null {
  if (!href) return null
  const m = href.match(/^#chunk-(\d+)$/)
  if (!m) return null
  const n = Number(m[1])
  return Number.isNaN(n) ? null : n
}
